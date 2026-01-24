from ollama import chat
from pydantic import BaseModel
class LCBoundary(BaseModel):
    start_id: str | None
    end_id: str | None
def boundary_text(query : str):
    MODEL_REASONING = "ministral-3:14b"
    prompt = """
    You are a strict PDF document parser.
    Your task is to locate a single continuous section that matches the query.

    Rules:
    - The section MUST start at the exact heading that best matches the query.
    - The section MUST end immediately before the next heading of the same or higher level.
    - If the topic spans multiple pages, include all chunks.
    - Do NOT guess. If unsure, return null IDs.

    Return ONLY valid JSON in this exact format:
    {
    "start_id": string | null,
    "end_id": string | null,
    } 
    {query}
    OUTPUT FORMAT (MANDATORY)
    Return ONLY this JSON structure.
    All values must be strings or null.
    EXAMPLE :
    {
    "start_id": "p5-c12",
    "end_id": "p6-c34",
    }
    Return ONLY valid JSON in this exact format:
    {
    "start_id": string | null,
    "end_id": string | null,
    }

    STRICT OUTPUT RULE:
    - Output MUST be a single valid JSON object
    - Do NOT output explanations
    - Do NOT wrap in markdown
    - Do NOT add comments
    - If any rule conflicts, OUTPUT JSON ONLY
    """
    response = chat(model=MODEL_REASONING, messages=[
        {"role": "user", "content": prompt}
    ] , format=LCBoundary.model_json_schema())
    return response