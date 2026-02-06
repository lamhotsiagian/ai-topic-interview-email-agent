import json
from typing import Any, Dict, List, Tuple

from openai import OpenAI


def _safe_json_loads(text: str) -> Dict[str, Any]:
    """
    Best-effort JSON parse. If the model returns extra text, try extracting the first {...}.
    """
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def generate_interview_qa(topic: str, count: int, model: str) -> Tuple[str, List[Dict[str, str]]]:
    """
    Returns: (topic, qa_list) where qa_list = [{"question":..., "answer":...}, ...]
    Uses Structured Outputs (json_schema) to force consistent JSON.
    """
    client = OpenAI()

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "topic": {"type": "string"},
            "qas": {
                "type": "array",
                "minItems": count,
                "maxItems": count,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "question": {"type": "string"},
                        "answer": {"type": "string"}
                    },
                    "required": ["question", "answer"]
                }
            }
        },
        "required": ["topic", "qas"]
    }

    instructions = (
        "You are a senior interviewer. Generate practical, frequently-asked interview Q&A. "
        "Answers should be clear, correct, and actionable. Keep each answer ~60–120 words."
    )

    user_input = (
        f"Topic: {topic}\n"
        f"Generate exactly {count} frequently asked interview questions and strong sample answers.\n"
        "Make the set balanced: fundamentals, practical scenario, pitfalls, best practices, and 1 advanced question."
    )

    resp = client.responses.create(
        model=model,
        instructions=instructions,
        input=user_input,
        text={
            "format": {
                "type": "json_schema",
                "name": "practice_interview_qas",
                "strict": True,
                "schema": schema,
            }
        },
    )

    data = _safe_json_loads(resp.output_text)
    out_topic = str(data["topic"]).strip()
    qas = data["qas"]

    cleaned: List[Dict[str, str]] = []
    for item in qas:
        cleaned.append({
            "question": str(item["question"]).strip(),
            "answer": str(item["answer"]).strip()
        })

    return out_topic, cleaned
