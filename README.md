# AI Topic Interview Email Agent (Public Google Sheet -> Generate Q&A -> Email)

This project reads the next **topic** from a **public Google Sheet (CSV)**, generates **10 interview Q&A** using OpenAI, and emails it to you via SMTP.

## 1) Google Sheet format (topics only)
Your sheet should have a header row:

| topic |
|------|
| Playwright Java |
| REST Assured |
| AI Agents |

Make the sheet public and ideally **Publish to the web** so CSV access works without login.

## 2) Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with:
- `SHEET_CSV_URL` (public CSV export URL)
- OpenAI API key/model
- SMTP settings
- `FROM_EMAIL` and `TO_EMAIL`

## 3) Run

Preview (dry-run):
```bash
python main.py
```

Send the email:
```bash
python main.py --send
```

Test without sheet (override topic):
```bash
python main.py --topic "Playwright Java" --send
```

## Notes
- This project uses the OpenAI Responses API and Structured Outputs (JSON schema) to reliably parse Q&A.
- `state.json` is created automatically to keep a cursor of which topic to use next.
# ai-topic-interview-email-agent
