"""Food bank order app — shop, cart, admin aggregation, and trip planning."""

import json
import os
from datetime import datetime, timezone
from functools import wraps
from types import SimpleNamespace

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
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Iconic")
PLEDGE_COOLDOWN_SECONDS = 60

# Visiting public pages ends the admin login for this browser session.
PUBLIC_ENDPOINTS = frozenset(
    {
        "shop",
        "cart",
        "confirm",
        "submit_order",
        "household_status",
        "community_board",
        "community_pledge",
    }
)

store.load()


@app.before_request
def _manage_admin_session():
    """Session cookie only (no long-lived persistence). Drop admin auth on public pages."""
    session.permanent = False
    endpoint = request.endpoint
    if endpoint in PUBLIC_ENDPOINTS:
        session.pop("admin_authenticated", None)


@app.context_processor
def inject_globals():
    trip = store.get_trip_settings()
    return {
        "order_weight_limit_lb": trip.get("order_weight_limit_lb", 10),
        "is_community_page": False,
    }


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            flash("Please log in to access admin.", "error")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


def _pledge_rate_limited() -> bool:
    last = session.get("last_pledge_at")
    if not last:
        return False
    try:
        last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
        return elapsed < PLEDGE_COOLDOWN_SECONDS
    except ValueError:
        return False


@app.route("/")
def shop():
    items = store.get_items()
    categories = store.get_categories()
    trip = store.get_trip_settings()
    return render_template(
        "shop.html",
        items=items,
        categories=categories,
        order_weight_limit_lb=trip.get("order_weight_limit_lb", 10),
    )


@app.route("/cart")
def cart():
    items = store.get_items()
    trip = store.get_trip_settings()
    return render_template(
        "cart.html",
        items=items,
        order_weight_limit_lb=trip.get("order_weight_limit_lb", 10),
    )


@app.route("/confirm")
def confirm():
    items = store.get_items()
    trip = store.get_trip_settings()
    return render_template(
        "confirm.html",
        items=items,
        order_weight_limit_lb=trip.get("order_weight_limit_lb", 10),
    )


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

    order_weight = store.compute_lines_weight(lines)
    weight_limit = store.get_order_weight_limit_lb()
    if order_weight > weight_limit:
        flash(
            f"Order weight ({order_weight:.1f} lb) exceeds the "
            f"{weight_limit:.0f} lb limit. Remove items and try again.",
            "error",
        )
        return redirect(url_for("cart"))

    store.add_order(household_name, lines)
    flash("Order placed successfully! Thank you.", "success")
    return render_template("order_success.html")


@app.route("/status", methods=["GET"])
def household_status():
    name = request.args.get("name", "").strip()
    status = store.lookup_household_status(name) if name else None
    return render_template("status.html", name=name, status=status)


def _board_view(data: dict) -> SimpleNamespace:
    """Wrap board dict so templates can use attribute access (avoids dict.items clash)."""
    trip = SimpleNamespace(**data.get("trip", {}))
    return SimpleNamespace(**{**data, "trip": trip})


@app.route("/community")
def community_board():
    board = _board_view(store.get_community_needs())
    return render_template(
        "community.html",
        board=board,
        is_community_page=True,
    )


@app.route("/community/pledge", methods=["GET", "POST"])
def community_pledge():
    board_data = store.get_community_needs()
    board = _board_view(board_data)
    open_items = [item for item in board_data["items"] if item["remaining_need"] > 0]

    if request.method == "POST":
        if not board_data.get("published"):
            flash("The community board is not open for pledges yet.", "error")
            return redirect(url_for("community_pledge"))

        if _pledge_rate_limited():
            flash("Please wait a minute before submitting another pledge.", "error")
            return redirect(url_for("community_pledge"))

        donor_name = request.form.get("donor_name", "").strip()
        if request.form.get("anonymous") == "on":
            donor_name = store.ANONYMOUS_DONOR_NAME

        item_id = request.form.get("item_id", "").strip()
        qty_raw = request.form.get("quantity", "1").strip()
        note = request.form.get("note", "").strip()

        try:
            quantity = int(qty_raw)
        except ValueError:
            quantity = 0

        try:
            store.add_donor_pledge(donor_name, item_id, quantity, note)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("community_pledge"))

        session["last_pledge_at"] = datetime.now(timezone.utc).isoformat()
        flash("Thank you! Your pledge has been recorded.", "success")
        return redirect(url_for("community_board"))

    return render_template(
        "community_pledge.html",
        board=board,
        open_items=open_items,
        is_community_page=True,
    )


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        session.pop("admin_authenticated", None)
        return render_template("admin_login.html")

    password = request.form.get("password", "")
    if password == ADMIN_PASSWORD:
        session.clear()
        session.permanent = False
        session["admin_authenticated"] = True
        flash("Welcome, admin.", "success")
        return redirect(url_for("admin_dashboard"))
    flash("Incorrect password.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("shop"))


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    tab = request.args.get("tab", "current")
    sort_mode = request.args.get("sort", "demand")
    trip = store.get_trip_settings()
    totals = store.aggregate_totals(sort_mode=sort_mode)
    demand_weight = store.demand_weight_lb()
    weight_limit = trip.get("weight_limit_lb", 200)
    order_count = len(store.get_orders())
    orders_detail = store.orders_with_weight()
    archive_rounds = store.get_archive()
    over_by = max(0, round(demand_weight - weight_limit, 2))
    return render_template(
        "admin.html",
        tab=tab,
        sort_mode=sort_mode,
        totals=totals,
        demand_weight=demand_weight,
        weight_limit=weight_limit,
        over_by=over_by,
        order_count=order_count,
        orders_detail=orders_detail,
        trip=trip,
        archive_rounds=archive_rounds,
    )


@app.route("/admin/trip", methods=["POST"])
@admin_required
def admin_trip_settings():
    try:
        weight_limit = float(request.form.get("weight_limit_lb", 200))
        order_weight_limit = float(request.form.get("order_weight_limit_lb", 10))
    except ValueError:
        flash("Invalid weight values.", "error")
        return redirect(url_for("admin_dashboard", tab="current"))

    store.save_trip_settings(
        {
            "weight_limit_lb": max(0, weight_limit),
            "order_weight_limit_lb": max(1, order_weight_limit),
            "trip_name": request.form.get("trip_name", "").strip(),
            "pickup_date": request.form.get("pickup_date", "").strip(),
            "store_name": request.form.get("store_name", "").strip(),
        }
    )
    flash("Trip settings saved.", "success")
    return redirect(url_for("admin_dashboard", tab="current"))


@app.route("/admin/inventory", methods=["GET", "POST"])
@admin_required
def admin_inventory():
    items = store.get_items()
    inventory = store.get_store_inventory()
    trip = store.get_trip_settings()

    if request.method == "POST":
        lines = []
        for item in items:
            qty_raw = request.form.get(f"qty_{item['id']}", "0").strip()
            expires = request.form.get(f"expires_{item['id']}", "").strip()
            try:
                qty = max(0, int(qty_raw or 0))
            except ValueError:
                qty = 0
            if qty > 0:
                lines.append(
                    {
                        "item_id": item["id"],
                        "available_qty": qty,
                        "weight_lb": item.get("weight_lb", 0),
                        "expires_at": expires,
                    }
                )
        store.save_store_inventory(
            {
                "store_name": request.form.get("store_name", "").strip()
                or trip.get("store_name", ""),
                "expires_by": request.form.get("expires_by", "").strip(),
                "lines": lines,
            }
        )
        flash("Store inventory saved.", "success")
        return redirect(url_for("admin_inventory"))

    inv_map = {l["item_id"]: l for l in inventory.get("lines", [])}
    return render_template(
        "admin_inventory.html",
        items=items,
        inventory=inventory,
        inv_map=inv_map,
        trip=trip,
    )


@app.route("/admin/plan", methods=["GET", "POST"])
@admin_required
def admin_plan():
    trip = store.get_trip_settings()
    weight_limit = trip.get("weight_limit_lb", 200)

    if request.method == "POST":
        action = request.form.get("action", "save")
        if action == "suggest":
            store.suggest_fill()
            flash("Suggested fill applied based on demand and weight limit.", "success")
        elif action == "fulfill":
            store.save_fulfillment()
            flash("Fulfillment recorded from current selection.", "success")
        else:
            lines = []
            for key, val in request.form.items():
                if key.startswith("pick_"):
                    item_id = key[5:]
                    try:
                        pick_qty = max(0, int(val or 0))
                    except ValueError:
                        pick_qty = 0
                    if pick_qty > 0:
                        lines.append(
                            {
                                "item_id": item_id,
                                "pick_qty": pick_qty,
                                "weight_lb": store.item_weight_lb(item_id),
                            }
                        )
            store.save_selection({"lines": lines})
            flash("Selection saved.", "success")
        return redirect(url_for("admin_plan"))

    planner_rows = store.build_planner_rows()
    selection = store.get_selection()
    return render_template(
        "admin_plan.html",
        planner_rows=planner_rows,
        selection=selection,
        weight_limit=weight_limit,
        trip=trip,
    )


@app.route("/admin/round/<round_id>")
@admin_required
def admin_round_detail(round_id: str):
    round_entry = store.get_archive_round(round_id)
    if round_entry is None:
        flash("Round not found.", "error")
        return redirect(url_for("admin_dashboard", tab="history"))
    return render_template("admin_round.html", round_entry=round_entry)


@app.route("/admin/community", methods=["GET"])
@admin_required
def admin_community():
    board = _board_view(store.get_community_needs(include_unpublished=True))
    pledges = store.get_all_pledges_for_round()
    return render_template(
        "admin_community.html",
        board=board,
        pledges=pledges,
    )


@app.route("/admin/reset", methods=["POST"])
@admin_required
def admin_reset():
    if not store.get_orders():
        flash("No orders to archive. The current round is already empty.", "error")
        return redirect(url_for("admin_dashboard", tab="current"))

    store.save_fulfillment()
    round_entry = store.archive_current_round()
    if round_entry:
        flash(
            f"Round archived ({round_entry['order_count']} orders). Shopping list reset.",
            "success",
        )
    return redirect(url_for("admin_dashboard", tab="history"))


@app.route("/admin/community/publish", methods=["POST"])
@admin_required
def admin_community_publish():
    published = request.form.get("published", "0") == "1"
    if published and not store.get_fulfillment().get("items"):
        flash("Record fulfillment before publishing the community board.", "error")
        return redirect(url_for("admin_community"))

    store.set_community_published(published)
    if published:
        flash("Community board is now public.", "success")
    else:
        flash("Community board unpublished.", "success")
    return redirect(url_for("admin_community"))


@app.route("/admin/community/pledge/<pledge_id>", methods=["POST"])
@admin_required
def admin_pledge_action(pledge_id: str):
    action = request.form.get("action", "")
    status_map = {"received": "received", "cancelled": "cancelled"}
    status = status_map.get(action)
    if not status:
        flash("Invalid action.", "error")
        return redirect(url_for("admin_community"))

    result = store.update_pledge_status(pledge_id, status)
    if result is None:
        flash("Pledge not found.", "error")
    elif status == "received":
        flash(
            "Donation marked received — inventory and fulfillment updated. "
            "Community needs board reflects the new totals.",
            "success",
        )
    else:
        flash(f"Pledge marked as {status}.", "success")
    return redirect(url_for("admin_community"))


if __name__ == "__main__":
    app.run(debug=True)
