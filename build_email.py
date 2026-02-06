from typing import Dict, List


def build_subject(topic: str) -> str:
    return f"Practice Interview: {topic} — 10 Q&A"


def build_body(topic: str, qas: List[Dict[str, str]]) -> str:
    lines = []
    lines.append(f"Practice Interview Pack — Topic: {topic}")
    lines.append("")
    lines.append("Here are 10 frequently asked questions with sample answers.")
    lines.append("")

    for i, qa in enumerate(qas, start=1):
        q = qa["question"]
        a = qa["answer"]
        lines.append(f"{i}) Q: {q}")
        lines.append(f"   A: {a}")
        lines.append("")

    lines.append("Tip: Reply to yourself with notes, then practice answering each question out loud in 2 minutes.")
    return "\n".join(lines).strip()
