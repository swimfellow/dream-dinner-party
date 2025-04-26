from flask import Flask, render_template, request, redirect, url_for
import os
import csv

app = Flask(__name__)
CSV_FILE = "responses.csv"

@app.route("/")
@app.route("/<user>")
def ddp(user=None):
    return render_template('index.html', user=user)

@app.route("/survey/<user>")
def survey(user):
    individual = get_next_individual(user)
    if individual:
        return render_template(
    'survey.html',
    user=user,
    label=individual['label'],
    wikipedia_url=individual['wikipedia_url'],
    description=individual['description'],
    image_url=individual['image_url'],
    completed=individual['progress']['completed'],
    total=individual['progress']['total']
)

    else:
        return "Thank you! Calculating..."

@app.route("/submit", methods=["POST"])
def submit():
    user = request.form.get("user")
    label = request.form.get("label")
    likert_response = request.form.get("likert")

    update_response(user, label, likert_response)
    return redirect(url_for('survey', user=user))

def get_next_individual(user):
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        user_rows = [row for row in rows if row["user"] == user]
        total = len(user_rows)
        completed = sum(1 for row in user_rows if row["likert_response"] != "")
        
        for row in user_rows:
            if row["likert_response"] == "":
                # Return both the individual and progress data
                return {
                    'label': row['label'],
                    'wikipedia_url': row['wikipedia_url'],
                    'description': row['description'],
                    'image_url': row['image_url'],
                    'progress': {
                        'completed': completed,
                        'total': total
                    }
                }
    return None

def update_response(user, label, likert_response):
    rows = []
    fieldnames = None
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames  # <-- Capture the fieldnames!
        for row in reader:
            if row["user"] == user and row["label"] == label and row["likert_response"] == "":
                row["likert_response"] = likert_response
            rows.append(row)

    with open(CSV_FILE, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)