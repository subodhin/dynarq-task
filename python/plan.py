from datetime import date
from collections import Counter

"""Payment reminder rules engine (part 1).

Run from inside python/:

    python plan.py --invoices ../data/invoices.json --sent ../data/sent.json --today 2026-10-12 --out ../actions.json

This starter only reads the files and writes an empty plan in the required shape.
The rules are yours to build.
"""

import argparse
import json


def parse_date(value):
    """Return a date for a valid YYYY-MM-DD string, otherwise None."""
    if not isinstance(value, str):
        return None

    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None

    if parsed.isoformat() != value:
        return None

    return parsed
def validate_amount(value):
    """Return True if value is a positive JSON number, excluding booleans."""
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and value > 0
    )
def validate_invoice(invoice, today_date):
    """Return the first validation error, or None when the invoice is valid."""

    if not validate_amount(invoice.get("amount")):
        return "invalid_amount"

    due_date_value = invoice.get("due_date")

    if due_date_value is None or due_date_value == "":
        return "missing_due_date"

    due_date = parse_date(due_date_value)

    if due_date is None:
        return "invalid_due_date"

    paid_date_value = invoice.get("paid_date")

    if paid_date_value is not None:
        paid_date = parse_date(paid_date_value)

        if paid_date is None or paid_date > today_date:
            return "invalid_paid_date"

    return None
def calculate_days_overdue(due_date, today_date):
    """Return calendar days overdue. Future due dates produce a negative value."""
    return (today_date - due_date).days

def build_plan(invoices, sent, today):
    """Build a reminder plan for the given date."""

    today_date = parse_date(today)
    if today_date is None:
        raise ValueError("today must be a valid YYYY-MM-DD date")

    # Count IDs before processing invoices so every duplicate is caught.
    counts = Counter(
        invoice.get("id")
        for invoice in invoices
        if isinstance(invoice, dict)
    )

    duplicate_ids = {
        invoice_id
        for invoice_id, count in counts.items()
        if count > 1
    }

    actions = []
    skipped = [
        {"invoice_id": invoice_id, "reason": "duplicate_id"}
        for invoice_id in duplicate_ids
    ]

    for invoice in invoices:
        if not isinstance(invoice, dict):
            continue

        invoice_id = invoice.get("id")

        # Duplicate IDs take precedence over other validation errors.
        if invoice_id in duplicate_ids:
            continue

        reason = validate_invoice(invoice, today_date)

        if reason is not None:
            skipped.append({
                "invoice_id": invoice_id,
                "reason": reason,
            })
            continue

                # Paid invoices should not receive reminders.
        if invoice.get("paid_date") is not None:
            continue

        due_date = parse_date(invoice["due_date"])
        days_overdue = calculate_days_overdue(due_date, today_date)

        step = select_reminder_step(days_overdue)

        # Not overdue enough for a reminder.
        if step is None:
            continue

        if already_sent(invoice_id, step, sent):
            continue
       
        actions.append({
            "invoice_id": invoice_id,
            "step": step,
            "needs_approval": step in ("firm", "final"),
            "days_overdue": days_overdue,
            "message": build_message(invoice, step, days_overdue),
        })

    actions.sort(key=lambda action: action["invoice_id"])
    skipped.sort(key=lambda item: item["invoice_id"])

    return {
        "today": today,
        "actions": actions,
        "skipped": skipped,
    }

def already_sent(invoice_id, step, sent):
    """Check whether this reminder step or a higher step was already sent."""
    step_rank = {
        "friendly": 1,
        "firm": 2,
        "final": 3,
    }

    current_rank = step_rank[step]

    for record in sent:
        if not isinstance(record, dict):
            continue

        if record.get("invoice_id") != invoice_id:
            continue

        previous_rank = step_rank.get(record.get("step"), 0)

        if previous_rank >= current_rank:
            return True

    return False

def select_reminder_step(days_overdue):
    """Return the highest reminder step reached, or None if not overdue enough."""
    if days_overdue >= 24:
        return "final"
    if days_overdue >= 10:
        return "firm"
    if days_overdue >= 3:
        return "friendly"
    return None

def build_message(invoice, step, days_overdue):
    """Build a reminder using only facts supplied by the invoice and rules."""
    customer = invoice["customer"]
    invoice_id = invoice["id"]
    due_date = invoice["due_date"]
    amount = f'{invoice["currency"]} {invoice["amount"]:.2f}'

    if step == "friendly":
        tone = (
            f"Hi {customer}, this is a friendly reminder that invoice "
            f"{invoice_id} for {amount} was due on {due_date}. "
            f"It is {days_overdue} days overdue. Could you please arrange payment?"
        )
    elif step == "firm":
        tone = (
            f"Hello {customer}, invoice {invoice_id} for {amount}, due on "
            f"{due_date}, is now {days_overdue} days overdue. "
            f"Please arrange payment as soon as possible."
        )
    else:
        tone = (
            f"Hello {customer}, our records show invoice {invoice_id} for "
            f"{amount}, due on {due_date}, is {days_overdue} days overdue. "
            f"Please give this outstanding payment your urgent attention."
        )

    return tone

def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Plan today's payment reminders.")
    parser.add_argument("--invoices", required=True, help="path to invoices.json")
    parser.add_argument("--sent", required=True, help="path to sent.json")
    parser.add_argument("--today", required=True, help="date as YYYY-MM-DD")
    parser.add_argument("--out", required=True, help="path to write the plan JSON")
    args = parser.parse_args()

 
    try:
        invoices = read_json(args.invoices)
        sent = read_json(args.sent)
        plan = build_plan(invoices, sent, args.today)

        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(plan, f, indent=2)
            f.write("\n")

    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

if __name__ == "__main__":
    main()
