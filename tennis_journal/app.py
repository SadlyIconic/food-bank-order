"""Flask tennis journal — CRUD for match entries."""

from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for

import insights
import store

app = Flask(__name__)
app.secret_key = "dev-secret-change-in-production"

store.load()

REQUIRED_FIELDS = ("opponent", "date", "score")


def parse_form() -> dict:
    return {
        "opponent": request.form.get("opponent", "").strip(),
        "date": request.form.get("date", "").strip(),
        "score": request.form.get("score", "").strip(),
        "notes": request.form.get("notes", "").strip(),
        "result": request.form.get("result", "").strip(),
        "match_type": request.form.get("match_type", "singles").strip(),
    }


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if not data.get(field):
            errors.append(f"{field.replace('_', ' ').title()} is required.")
    if data.get("date"):
        try:
            datetime.strptime(data["date"], "%Y-%m-%d")
        except ValueError:
            errors.append("Date must be in YYYY-MM-DD format.")
    return errors


@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    entries = store.get_all(q=q)
    return render_template("index.html", entries=entries, q=q)


@app.route("/insights")
def insights_page():
    entries = store.get_all()
    report = insights.analyze(entries)
    return render_template("insights.html", report=report)


@app.route("/entries/new", methods=["GET", "POST"])
def create_entry():
    if request.method == "POST":
        data = parse_form()
        errors = validate(data)
        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("form.html", entry=data, is_edit=False)
        store.create(data)
        flash("Entry saved.", "success")
        return redirect(url_for("index"))
    return render_template("form.html", entry=None, is_edit=False)


@app.route("/entries/<entry_id>")
def view_entry(entry_id: str):
    entry = store.get_by_id(entry_id)
    if entry is None:
        flash("Entry not found.", "error")
        return redirect(url_for("index"))
    return render_template("entry.html", entry=entry)


@app.route("/entries/<entry_id>/edit", methods=["GET", "POST"])
def edit_entry(entry_id: str):
    entry = store.get_by_id(entry_id)
    if entry is None:
        flash("Entry not found.", "error")
        return redirect(url_for("index"))
    if request.method == "POST":
        data = parse_form()
        errors = validate(data)
        if errors:
            for err in errors:
                flash(err, "error")
            data["id"] = entry_id
            return render_template("form.html", entry=data, is_edit=True)
        store.update(entry_id, data)
        flash("Entry saved.", "success")
        return redirect(url_for("index"))
    return render_template("form.html", entry=entry, is_edit=True)


@app.route("/entries/<entry_id>/delete", methods=["POST"])
def delete_entry(entry_id: str):
    if store.delete(entry_id):
        flash("Entry deleted.", "success")
    else:
        flash("Entry not found.", "error")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
