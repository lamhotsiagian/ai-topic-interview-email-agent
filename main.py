import argparse
import json
import os
from typing import Any, Dict

from dotenv import load_dotenv

from sheets_public import fetch_public_sheet_rows, extract_topics
from llm_openai import generate_interview_qa
from build_email import build_subject, build_body
from email_smtp import send_email_smtp


STATE_PATH = "state.json"


def must_get(key: str) -> str:
    v = (os.getenv(key) or "").strip()
    if not v:
        raise SystemExit(f"Missing required env var: {key}")
    return v


def load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_PATH):
        return {"cursor": 0}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: Dict[str, Any]) -> None:
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def pick_next_topic(topics: list[str]) -> str:
    if not topics:
        raise SystemExit("No topics found in the sheet. Check TOPIC_COLUMN_NAME and sheet content.")

    state = load_state()
    cursor = int(state.get("cursor", 0))

    cursor = cursor % len(topics)
    topic = topics[cursor]

    state["cursor"] = (cursor + 1) % len(topics)
    save_state(state)

    return topic


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Read next topic from public sheet -> generate interview Q&A -> email to you"
    )
    parser.add_argument("--send", action="store_true", help="Actually send the email (default is dry-run)")
    parser.add_argument("--topic", default="", help="Override topic (skip sheet) for testing")
    args = parser.parse_args()

    sheet_csv_url = must_get("SHEET_CSV_URL")
    topic_col = os.getenv("TOPIC_COLUMN_NAME", "topic")
    qa_count = int(os.getenv("QA_COUNT", "10"))
    model = os.getenv("OPENAI_MODEL", "gpt-5.2")

    if args.topic.strip():
        topic = args.topic.strip()
    else:
        rows = fetch_public_sheet_rows(sheet_csv_url)
        topics = extract_topics(rows, topic_col)
        topic = pick_next_topic(topics)

    out_topic, qas = generate_interview_qa(topic=topic, count=qa_count, model=model)

    subject = build_subject(out_topic)
    body = build_body(out_topic, qas)

    to_email = must_get("TO_EMAIL")
    from_email = must_get("FROM_EMAIL")

    print("\n--- PREVIEW ---")
    print("To:", to_email)
    print("Subject:", subject)
    print("\n" + body)
    print("--------------\n")

    if not args.send:
        print("Dry-run only. Re-run with --send to email it.")
        return

    send_email_smtp(
        smtp_host=must_get("SMTP_HOST"),
        smtp_port=int(must_get("SMTP_PORT")),
        smtp_user=must_get("SMTP_USER"),
        smtp_pass=must_get("SMTP_PASS"),
        from_email=from_email,
        to_email=to_email,
        subject=subject,
        body=body,
    )
    print("✅ Email sent.")


if __name__ == "__main__":
    main()
