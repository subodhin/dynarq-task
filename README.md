# Payment Reminder Assistant

A Python rules engine and web page for reviewing overdue business invoices.

## Requirements
- Python 3.11 or newer.
- Run commands from the `python/` directory unless stated otherwise.

## Tests
`python -m unittest discover -s tests -v`

## Generate the reminder plan
`python plan.py --invoices ../data/invoices.json --sent ../data/sent.json --today 2026-10-12 --out ../actions.json`

## Run the web page
`python app.py`
Open `http://localhost:8000/`.

## Configuration
The web app supports `PORT`, `DATA_DIR`, and `TODAY` environment variables.
Defaults are port 8000, `../data`, and the current date.

## Decisions
- Used a deterministic rules engine that runs offline.
- Validated invoice data in the required precedence order.
- Planned only the highest eligible reminder step.
- Prevented reminders when the same or a higher step was already sent.
- Kept CLI action objects to the exact required output schema.
- Reused the rules engine in the web app.
- Kept approval decisions in memory; no messages are sent.

## Next steps
- Add more edge-case and web application tests.
- Improve logging and operational error reporting.
- Verify legal and reference-rate details against authoritative current sources.