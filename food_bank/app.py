"""Food bank order app — shop, cart, and admin aggregation."""

import json
from functools import wraps

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import store

app = Flask(__name__)
app.secret_key = "dev-secret-change-in-production"

ADMIN_PASSWORD = "Iconic"

store.load()


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            flash("Please log in to access admin.", "error")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def shop():
    items = store.get_items()
    categories = store.get_categories()
    return render_template("shop.html", items=items, categories=categories)


@app.route("/cart")
def cart():
    items = store.get_items()
    return render_template("cart.html", items=items)


@app.route("/confirm")
def confirm():
    items = store.get_items()
    return render_template("confirm.html", items=items)


@app.route("/order", methods=["POST"])
def submit_order():
    household_name = request.form.get("household_name", "").strip()
    cart_json = request.form.get("cart_json", "").strip()

    if not cart_json:
        flash("Your cart is empty. Add items before placing an order.", "error")
        return redirect(url_for("shop"))

    try:
        cart_lines = json.loads(cart_json)
    except json.JSONDecodeError:
        flash("Invalid cart data. Please try again.", "error")
        return redirect(url_for("cart"))

    if not isinstance(cart_lines, list) or not cart_lines:
        flash("Your cart is empty. Add items before placing an order.", "error")
        return redirect(url_for("shop"))

    item_map = store.get_item_map()
    lines: list[dict] = []
    for entry in cart_lines:
        item_id = entry.get("item_id", "")
        quantity = entry.get("quantity", 0)
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue
        if not item_id or quantity < 1:
            continue
        catalog = item_map.get(item_id)
        if catalog:
            lines.append(
                {
                    "item_id": item_id,
                    "name": catalog["name"],
                    "quantity": quantity,
                }
            )

    if not lines:
        flash("No valid items in your cart. Please add items and try again.", "error")
        return redirect(url_for("cart"))

    store.add_order(household_name, lines)
    flash("Order placed successfully! Thank you.", "success")
    return render_template("order_success.html")


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_authenticated"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["admin_authenticated"] = True
            flash("Welcome, admin.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect password.", "error")

    return render_template("admin_login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.pop("admin_authenticated", None)
    flash("Logged out.", "success")
    return redirect(url_for("shop"))


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    tab = request.args.get("tab", "current")
    totals = store.aggregate_totals()
    order_count = len(store.get_orders())
    archive_rounds = store.get_archive()
    return render_template(
        "admin.html",
        tab=tab,
        totals=totals,
        order_count=order_count,
        archive_rounds=archive_rounds,
    )


@app.route("/admin/round/<round_id>")
@admin_required
def admin_round_detail(round_id: str):
    round_entry = store.get_archive_round(round_id)
    if round_entry is None:
        flash("Round not found.", "error")
        return redirect(url_for("admin_dashboard", tab="history"))
    return render_template("admin_round.html", round_entry=round_entry)


@app.route("/admin/reset", methods=["POST"])
@admin_required
def admin_reset():
    if not store.get_orders():
        flash("No orders to archive. The current round is already empty.", "error")
        return redirect(url_for("admin_dashboard", tab="current"))

    round_entry = store.archive_current_round()
    if round_entry:
        flash(
            f"Round archived ({round_entry['order_count']} orders). Shopping list reset.",
            "success",
        )
    return redirect(url_for("admin_dashboard", tab="history"))


if __name__ == "__main__":
    app.run(debug=True)
