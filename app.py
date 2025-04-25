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
        return render_template('survey.html', user=user, individual=individual)
    else:
        return "Thank you! Calculating..."

@app.route("/submit", methods=["POST"])
def submit():
    user = request.form.get("user")
    individual = request.form.get("individual")
    likert_response = request.form.get("likert")

    update_response(user, individual, likert_response)
    return redirect(url_for('survey', user=user))

def get_next_individual(user):
    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["user"] == user and row["likert_response"] == "":
                return row["individual"]
    return None

def update_response(user, individual, likert_response):
    rows = []
    with open(CSV_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["user"] == user and row["individual"] == individual and row["likert_response"] == "":
                row["likert_response"] = likert_response
            rows.append(row)

    with open(CSV_FILE, "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["user", "individual", "likert_response"])
        writer.writeheader()
        writer.writerows(rows)