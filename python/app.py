"""Owner's payment reminder page.

Run from inside python/:
    python app.py

Environment variables:
    PORT: port to listen on, default 8000
    DATA_DIR: folder containing invoices.json and sent.json, default ../data
    TODAY: date in YYYY-MM-DD format, default the real date
"""

import json
import os
from datetime import date
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from plan import build_plan, read_json


PORT = int(os.environ.get("PORT", "8000"))
DATA_DIR = os.environ.get("DATA_DIR", "../data")
TODAY = os.environ.get("TODAY") or date.today().isoformat()

DECISIONS = {}


REASON_LABELS = {
    "duplicate_id": "Duplicate invoice ID",
    "invalid_amount": "Missing or invalid amount",
    "missing_due_date": "Due date is missing",
    "invalid_due_date": "Due date is invalid",
    "invalid_paid_date": "Payment date is invalid",
}


def render_page(plan, decisions, error=None):
    """Render the reminder plan as a responsive HTML page."""

    if error:
        actions_html = (
            '<p class="error">The reminder data could not be loaded. '
            f"{escape(str(error))}</p>"
        )
        skipped_html = ""
    else:
        cards = []

        for action in plan["actions"]:
            invoice_id = str(action["invoice_id"])
            step = str(action["step"])
            approval_required = action.get(
                "needs_approval",
                action.get("requires_approval", step in ("firm", "final")),
            )

            approval_html = ""

            if approval_required:
                decision = decisions.get(invoice_id)

                if decision:
                    approval_html = (
                        '<p class="decision">Decision: '
                        f"{escape(decision.title())}</p>"
                    )
                else:
                    approval_html = f"""
                    <form method="post" action="/">
                        <input type="hidden" name="invoice_id"
                               value="{escape(invoice_id, quote=True)}">
                        <button type="submit" name="decision"
                                value="approve">Approve</button>
                        <button type="submit" name="decision"
                                value="reject">Reject</button>
                    </form>
                    """

            else:
                approval_html = (
                    '<p class="decision">No approval required</p>'
                )

            card = f"""
            <article class="card">
                <h2>{escape(str(action['customer']))}</h2>
                <p><strong>Invoice:</strong>
                   {escape(invoice_id)}</p>
                <p><strong>Amount:</strong>
                   {escape(str(action['currency']))}
                   {float(action['amount']):,.2f}</p>
                <p><strong>Due date:</strong>
                   {escape(str(action['due_date']))}</p>
                <p><strong>Days overdue:</strong>
                   {action['days_overdue']}</p>
                <p><strong>Step:</strong>
                   {escape(step.upper())}</p>
                <p class="message">{escape(str(action['message']))}</p>
                {approval_html}
            </article>
            """
            cards.append(card)

        actions_html = (
            "\n".join(cards)
            if cards
            else "<p>There are no reminders to review today.</p>"
        )

        skipped_items = []

        for item in plan["skipped"]:
            invoice_id = escape(str(item["invoice_id"]))
            reason = REASON_LABELS.get(
                item["reason"],
                "Invoice data could not be validated",
            )
            skipped_items.append(
                f"<li><strong>{invoice_id}</strong> — "
                f"{escape(reason)}</li>"
            )

        skipped_html = (
            "<ul>" + "\n".join(skipped_items) + "</ul>"
            if skipped_items
            else "<p>No invoices were skipped.</p>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Payment reminders</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: system-ui, sans-serif;
            max-width: 850px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f6f8;
            color: #222;
            line-height: 1.5;
        }}
        .card {{
            background: white;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 18px;
            margin: 16px 0;
            overflow-wrap: anywhere;
        }}
        .message {{
            background: #f0f4f8;
            padding: 12px;
            border-radius: 6px;
        }}
        button {{
            font: inherit;
            padding: 10px 16px;
            margin: 6px 8px 6px 0;
            cursor: pointer;
        }}
        button:focus-visible {{
            outline: 3px solid #245dcc;
            outline-offset: 2px;
        }}
        .decision {{ font-weight: bold; }}
        .error {{ color: #9c1c1c; }}
        @media (max-width: 420px) {{
            body {{ padding: 12px; }}
            .card {{ padding: 12px; }}
        }}
    </style>
</head>
<body>
    <h1>Payment reminders</h1>
    <p>Today's plan: {escape(TODAY)}</p>
    <h2>Reminders</h2>
    {actions_html}
    <h2>Skipped invoices</h2>
    {skipped_html}
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return

        try:
            invoices = read_json(os.path.join(DATA_DIR, "invoices.json"))
            sent = read_json(os.path.join(DATA_DIR, "sent.json"))
            plan = build_plan(invoices, sent, TODAY)
            
            invoice_by_id = {
                invoice["id"]: invoice
                for invoice in invoices
                if isinstance(invoice, dict) and "id" in invoice
            }

            display_plan = dict(plan)
            display_plan["actions"] = [
                {
                    **action,
                    "customer": invoice_by_id[action["invoice_id"]].get("customer", ""),
                    "amount": invoice_by_id[action["invoice_id"]].get("amount", 0),
                    "currency": invoice_by_id[action["invoice_id"]].get("currency", ""),
                    "due_date": invoice_by_id[action["invoice_id"]].get("due_date", ""),
                }
                for action in plan["actions"]
                if action["invoice_id"] in invoice_by_id
            ]

        except (OSError, ValueError, json.JSONDecodeError) as exc:
            body = render_page(None, DECISIONS, error=exc)
            self.send_html(body, status=500)
            return

        self.send_html(render_page(display_plan, DECISIONS))

    def do_POST(self):
        if self.path != "/":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))

            if length <= 0 or length > 10_000:
                self.send_error(400, "Invalid form submission")
                return

            from urllib.parse import parse_qs

            raw = self.rfile.read(length).decode("utf-8")
            form = parse_qs(raw)
            invoice_id = form.get("invoice_id", [""])[0]
            decision = form.get("decision", [""])[0]

            if decision not in ("approve", "reject"):
                self.send_error(400, "Invalid decision")
                return

            invoices = read_json(os.path.join(DATA_DIR, "invoices.json"))
            sent = read_json(os.path.join(DATA_DIR, "sent.json"))
            plan = build_plan(invoices, sent, TODAY)

            eligible = {
                action["invoice_id"]
                for action in plan["actions"]
                if action["step"] in ("firm", "final")
                and action.get(
                    "needs_approval",
                    action.get("requires_approval", True),
                )
            }

            if invoice_id not in eligible:
                self.send_error(400, "Invoice is not awaiting approval")
                return

            DECISIONS[invoice_id] = decision

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()

        except (OSError, ValueError, json.JSONDecodeError) as exc:
            self.send_error(500, f"Could not record decision: {exc}")

    def send_html(self, body, status=200):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    server = ThreadingHTTPServer(("", PORT), Handler)
    print(f"Serving on http://localhost:{PORT}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()