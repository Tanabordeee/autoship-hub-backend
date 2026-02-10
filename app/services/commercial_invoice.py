from weasyprint import HTML, CSS
import jinja2
import os
from datetime import datetime
from app.schemas.commercial_invoice import CommercialInvoice
from app.repositories.proforma_invoice_repo import ProformaInvoiceRepo
from app.repositories.lc_repo import LCRepo
from app.repositories.bv import BVRepository
from app.repositories.si import SI_Repository
from app.repositories.booking import BookingRepo
import re
import ollama
from sqlalchemy.orm import Session
import json


def call_gemma_extract(prompt: str, system_prompt: str):
    response = ollama.chat(
        model="qwen2.5:7b-instruct",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    )
    return response["message"]["content"]


def parse_json_result(result_str: str):
    """
    Cleans and parses a JSON string from LLM output.
    Handles potential markdown code blocks.
    """
    if not result_str:
        return []
    try:
        # Check for markdown code blocks
        if "```json" in result_str:
            result_str = result_str.split("```json")[1].split("```")[0].strip()
        elif "```" in result_str:
            result_str = result_str.split("```")[1].split("```")[0].strip()

        # Clean up any potential leading/trailing non-json text
        result_str = result_str.strip()
        if not result_str.startswith("[") and "[" in result_str:
            result_str = result_str[result_str.find("[") :]
        if not result_str.endswith("]") and "]" in result_str:
            result_str = result_str[: result_str.rfind("]") + 1]

        return json.loads(result_str)
    except Exception as e:
        print(f"Error parsing JSON from LLM: {e}")
        # Fallback: if it's a multiline string that looks like a list
        lines = [
            line.strip().strip("-").strip("*").strip()
            for line in result_str.strip().split("\n")
            if line.strip()
        ]
        return lines


def generate_commercial_invoice(payload: CommercialInvoice, db: Session):
    pi = ProformaInvoiceRepo.get_by_id(db, payload.pi_id)
    lc = LCRepo.get_by_id(db, payload.lc_id)
    si = SI_Repository.get_by_id(db, payload.si_id)
    bv = BVRepository.get_by_id(db, payload.bv_id)
    booking = BookingRepo.get_by_id(db, payload.booking_id)
    # Setup Jinja2
    template_path = (
        r"E:\\job\\autoship-hub-server\\app\\templates\\commercial_invoice.html"
    )
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    # logo_path should be a file:// URL for WeasyPrint on Windows
    logo_file_path = r"E:\\job\\autoship-hub-server\\app\\assets\\logopap.png"
    logo_url = "file:///" + logo_file_path.replace("\\", "/")

    # Initialize variables for 46A extraction
    proforma_invoice_no = ""
    E_46A = []
    A_46A = ""
    beneficiary_to_certify = ""

    for i in (lc.document_require_46a or {}).get("items", []):
        if i.get("doc_type") == "INVOICE":
            conditions = i.get("conditions", "")
            match = re.search(r"PAP-\d+\s+OF\s+\d{2}\.\d{2}\.\d{4}", conditions)
            if match:
                proforma_invoice_no = match.group()
            E_46A_raw = call_gemma_extract(
                conditions,
                """
            You are a text extraction system.
From the input text below, extract ONLY the list of vehicle safety/accessory items
that are enumerated with (I), (II), (III), (IV).
Rules:
- Extract only the text belonging to items (I)–(IV)
- Do NOT include any other sentences
- Return the result as a JSON array of strings
- Keep the original wording exactly
            """,
            )
            E_46A = parse_json_result(E_46A_raw)
            A_46A = call_gemma_extract(
                conditions,
                """
                You are a text extraction system.
Task:
Extract ONLY the text labeled "A)".
Rules:
- Extract the full sentence(s) belonging to A)
- Stop extraction before item B)
- Do NOT summarize or paraphrase
- Preserve original wording exactly
- Return the result as plain text only (no JSON, no explanation)
                """,
            )
            beneficiary_to_certify = re.search(
                r"BENEFICIARY TO CERTIFY ON THE INVOICES?\s+(.*?\.)",
                conditions,
                re.IGNORECASE | re.DOTALL,
            )
            beneficiary_to_certify = (
                beneficiary_to_certify.group(1) if beneficiary_to_certify else ""
            )

    desc_items = (lc.description_of_good_45a_45b or {}).get("items", [])
    desc_text = desc_items[0].get("description", "") if desc_items else ""
    description = desc_text + (bv.engine_no if bv and bv.engine_no else "")
    freight_charge = 0
    insurance_charge = 0
    for p in pi.items:
        if p.description == "Freight":
            freight_charge = p.amount_in_usd
        if p.description == "Insurance":
            insurance_charge = p.amount_in_usd
    # Render HTML with dummy data
    html_out = template.render(
        invoice={
            "invoice_no": pi.pi_id,
            "date": pi.date,
            "proforma_invoice_no": proforma_invoice_no,
            "unit_price": pi.items[0].unit_price,
            "amount_in_usd": pi.items[0].amount_in_usd,
            "unit": pi.items[0].unit,
            "freight_charge": freight_charge,
            "insurance_charge": insurance_charge,
            "total_price": pi.total_price,
        },
        lc={
            "applicant": lc.applicant_50,
            "beneficiary": lc.beneficiary_59,
            "payment_terms": lc.form_of_documentary_credit_40a,
            "lc_number": lc.docmentary_credit_number_20,
            "date_of_issue": lc.date_of_issue_31c,
            "description": description,
            "E_46A": E_46A,
            "A_46A": A_46A,
            "beneficiary_to_certify": beneficiary_to_certify,
        },
        booking={
            "port_of_discharge": booking.port_of_disch,
            "port_of_loading": booking.port_of_loading,
        },
        si={
            "gross_weight": si.gross_weight,
            "port_of_loading": si.port_of_loading,
            "port_of_discharge": si.port_of_discharge,
        },
        bv={
            "country_of_origin": bv.country_of_origin,
            "year_of_manufacture": bv.year_of_manufacture,
            "make": bv.make,
            "model": bv.model,
            "type_of_vehicle": bv.type_of_vehicle,
            "year_of_registration": bv.year_month_of_first_registration,
            "bv_ref_no": bv.bv_ref_no,
            "commonly_called": bv.commonly_called,
        },
        bank=payload.bank,
        direction=payload.director,
        logo_path=logo_url,
    )

    # Ensure output directory exists
    output_dir = r"E:\\job\\autoship-hub-server\\app\\pdf"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate filename
    filename = f"commercial_invoice_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    output_path = os.path.join(output_dir, filename)

    # Add Tailwind CSS
    css_path = os.path.join(os.getcwd(), "static", "tailwind.css")
    stylesheets = []
    if os.path.exists(css_path):
        stylesheets.append(CSS(filename=css_path))

    # Convert to PDF using WeasyPrint
    # Providing base_url helps resolve relative assets if any
    HTML(string=html_out, base_url=template_dir).write_pdf(
        output_path, stylesheets=stylesheets
    )

    return {"output_path": output_path}
