import re


def clean_text_common(text: str) -> str:
    text = re.sub(
        r"THIS CREDIT IS VALID ONLY WHEN USED.*?(?=\n)|"
        r"NOTIFICATION OF LC ADVICE.*?(?=\n)|"
        r"PAGE \d+/.*?(?=\n)|"
        r"\[Page \d+\].*?(?=\n)|"
        r"^standard chartered\s*$|"
        r"^COMMERCIAL BANK OF CEYLON PLC\s*$|"
        r"^SH REL.*?(?=\n)|"
        r".*?ARR \.DATE=.*?(?=\n)|"
        r".*?ARR \.TIME=.*?(?=\n)|"
        r".*?REF \.NO\..*?(?=\n)|"
        r"^ARR .*?(?=\n)|"
        r"^REF .*?(?=\n)|"
        r"^DEAL=.*?(?=\n)|"
        r"^SENDER:.*?(?=\n)|"
        r".*?TEST AGREED SENDER.*?(?=\n)|"
        r"^Tel .*?(?=\n)|"
        r"^Fax .*?(?=\n)|"
        r"^Registration .*?(?=\n)|"
        r"^โทรศัพท์ .*?(?=\n)|"
        r"^โทรสาร .*?(?=\n)|"
        r"^ทะเบียนเลขที่ .*?(?=\n)|"
        r"^ธนาคารสแตนดาร์ดชาร์เตอร์ด.*?(?=\n)|"
        r"^140 ถนน.*?(?=\n)|"
        r"^140 Wireless.*?(?=\n)|"
        r"^ITSD-14.*?(?=\n)|"
        r"^\d+\s+TEST AGREED.*?(?=\n)|"
        r"^\d+\s*$|"
        r"^COLOMBO\s*$|"
        r"^Bangkok \d+.*?(?=\n)|"
        r"Standard Chartered Bank.*?(?=\n)|"
        r"TEST AGREED COMMERCIAL BANK OF CEYLON PLC COLOMBO.*?(?=\n)|"
        r"ICC PUBLICATION NO\.600 IS EXCLUDED.*?(?=\n)|"
        r"ARTICLE\s+\d+.*?UCP.*?(?=\n)|",
        "",
        text,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    return text


def clean_45a_text(text: str) -> str:
    # ตัดทุกอย่างหลัง noise marker (STOP WORDS)
    stop_patterns = [
        r"THIS CREDIT IS VALID ONLY WHEN USED",
        r"NOTIFICATION OF LC ADVICE",
        r"PAGE\s+\d+/",
        r"\[Page\s*\d+\]",
        r"Standard Chartered Bank",
        r"ธนาคารสแตนดาร์ดชาร์เตอร์ด",
        r"COMMERCIAL BANK OF CEYLON",
        r"COMERCIAL BANK OF CEYLON",
        r"SH REL\. DATE",
        r"SENDER:",
    ]

    for p in stop_patterns:
        text = re.split(p, text, flags=re.IGNORECASE)[0]

    # cleanup whitespace
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    return text


def extract_document_require_46A(full_text: str):
    patterns = {
        1: r"46A\s*:\s*DOCUMENTS\s*REQUIRED\s*(.+?)(?=\s*2\))",
        2: r"2\)\s*(.+?)(?=\s*3\))",
        3: r"3\)\s*(.+?)(?=\s*4\))",
        4: r"4\)\s*(.+?)(?=\s*5\))",
        5: r"5\)\s*(.+?)(?=\s*6\))",
        6: r"6\)\s*(.+?)(?=\s*7\))",
        7: r"7\)\s*(.+?)(?=\s*:?\s*47A\s*:|$)",
    }

    doc_types = {
        1: "INVOICE",
        2: "BILL_OF_LADING",
        3: "INSURANCE",
        4: "CERTIFICATE_OF_REGISTRATION",
        5: "TRANSLATION",
        6: "INSPECTION_CERTIFICATE",
        7: "INSPECTION_CERTIFICATE",
    }

    items = []

    for item_no in range(1, 8):
        match = re.search(patterns[item_no], full_text, re.DOTALL | re.IGNORECASE)
        if not match:
            continue

        text = match.group(1).strip()

        # =================================================
        # CLEANUP LOGIC (ใช้ชุดเดิม 100% กับทุก item)
        # =================================================
        text = clean_text_common(text)

        text = re.sub(r"\n\s*\n+", "\n", text).strip()

        item = {"item_no": item_no, "doc_type": doc_types[item_no], "conditions": text}

        # =================================================
        # SPECIAL FORMAT : ITEM 6
        # =================================================
        if item_no == 6:
            annexures = []

            annexure_block_match = re.search(
                r"ORIGINAL\s+CERTIFICATE\s+OF\s+PRE\s+SHIPMENT\s+INSPECTION.*?"
                r"THIS\s+REPORT\s+SHOULD\s+HAVE\s+THE\s+FOLLOWING\s+ANNEXTURE\.(.+?)"
                r"(?=\n?\s*THE\s+STAMP\s+OF|\n?\s*\d+\)|$)",
                item["conditions"],
                flags=re.DOTALL | re.IGNORECASE,
            )

            if annexure_block_match:
                annexure_block = annexure_block_match.group(1)

                annexure_matches = re.findall(
                    r"\(([A-C])\)\s*(.+?)(?=\n?\([A-C]\)|$)",
                    annexure_block,
                    flags=re.DOTALL | re.IGNORECASE,
                )

                annexures = [
                    {
                        "code": code.upper(),
                        "text": re.sub(r"\n\s*\n+", "\n", body).strip(),
                    }
                    for code, body in annexure_matches
                ]

            if annexures:
                item["annexures"] = annexures

            # ลบ annexure block ออกจาก conditions (ให้เหลือแต่ requirement หลัก)
            item["conditions"] = re.sub(
                r"THIS\s+REPORT\s+SHOULD\s+HAVE\s+THE\s+FOLLOWING\s+ANNEXTURE\..*",
                "",
                item["conditions"],
                flags=re.DOTALL | re.IGNORECASE,
            ).strip()

        items.append(item)

    return {"items": items}
