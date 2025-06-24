from flask import Flask, render_template, request, redirect, url_for, session
import json
import uuid
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = '93jsdf983jdfQWEr9023r'

TICKETS_FILE = 'data/tickets.json'
AZURE_FILE = 'data/azure_mock.json'

def load_tickets():
    with open(TICKETS_FILE, 'r') as f:
        return json.load(f)

def save_tickets(tickets):
    with open(TICKETS_FILE, 'w') as f:
        json.dump(tickets, f, indent=4)

@app.route('/')
def home():
    tickets = load_tickets()
    
    total_tickets = len(tickets)
    open_tickets = sum(1 for t in tickets if t['status'] == 'Open')
    closed_tickets = sum(1 for t in tickets if t['status'] == 'Closed')

    high_priority = sum(1 for t in tickets if t.get('priority') == 'High')
    medium_priority = sum(1 for t in tickets if t.get('priority') == 'Medium')
    low_priority = sum(1 for t in tickets if t.get('priority') == 'Low')

    session['open_count'] = open_tickets

    return render_template(
        'index.html',
        total=total_tickets,
        open_count=open_tickets,
        closed_count=closed_tickets,
        high=high_priority,
        medium=medium_priority,
        low=low_priority
    )

@app.route('/tickets', methods=['GET', 'POST'])
def tickets():
    tickets = load_tickets()

    if request.method == 'POST':
        issue_text = request.form['issue'].lower()

        if any(word in issue_text for word in ['network', 'down', 'email', 'outage']):
            priority = 'High'
        elif any(word in issue_text for word in ['printer', 'software', 'slow', 'password']):
            priority = 'Medium'
        else:
            priority = 'Low'

        new_ticket = {
            "id": str(uuid.uuid4())[:8],
            "name": request.form['name'],
            "issue": request.form['issue'],
            "status": "Open",
            "created": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "priority": priority
        }

        tickets.append(new_ticket)
        save_tickets(tickets)
        return redirect(url_for('tickets', success='1'))

    # Handle search
    query = request.args.get('search', '').lower()
    success = request.args.get('success')

    if query:
        tickets = [
            t for t in tickets
            if query in t['name'].lower()
            or query in t['issue'].lower()
            or query in t['status'].lower()
            or query in t.get('priority', '').lower()
        ]

    return render_template('tickets.html', tickets=tickets, search=query, success=success)

@app.route('/tickets/close/<ticket_id>')
def close_ticket(ticket_id):
    tickets = load_tickets()
    for t in tickets:
        if t['id'] == ticket_id:
            t['status'] = 'Closed'
    save_tickets(tickets)
    return redirect(url_for('tickets'))

@app.route('/azure')
def azure():
    with open(AZURE_FILE) as f:
        azure_data = json.load(f)
    return render_template('azure.html', azure=azure_data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
