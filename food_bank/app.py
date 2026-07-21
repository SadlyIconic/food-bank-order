"""Food bank demand intelligence — category requests, weekly trends, CSV export."""

import csv
import io
import os
import uuid
from functools import wraps

from flask import (
    Flask,
    Response,
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

PUBLIC_ENDPOINTS = frozenset({
    "request_board",
    "submit_requests",
    "community_board",
    "community_pledge",
    "community_pledge_success",
    "about",
})

store.load()


def _ensure_client_id() -> str:
    client_id = session.get("client_id")
    if not client_id:
        client_id = str(uuid.uuid4())
        session["client_id"] = client_id
    return client_id


@app.before_request
def _manage_admin_session():
    session.permanent = False
    if request.endpoint in PUBLIC_ENDPOINTS:
        session.pop("admin_authenticated", None)


@app.context_processor
def inject_globals():
    settings = store.get_app_settings()
    return {
        "agency_name": settings.get("agency_display_name", "Food Bank"),
        "visit_week": store.visit_week_key(),
    }


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_authenticated"):
            flash("Please log in to access admin.", "error")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/about")
def about():
    settings = store.get_app_settings()
    trip = store.get_trip_settings()
    return render_template("about.html", settings=settings, trip=trip)


@app.route("/")
def request_board():
    client_id = _ensure_client_id()
    settings = store.get_app_settings()
    week_key = store.visit_week_key()
    already_submitted = store.client_submitted_this_week(client_id, settings["food_bank_id"], week_key)
    categories = store.get_planning_categories(settings["food_bank_id"])
    return render_template(
        "request.html",
        categories=categories,
        already_submitted=already_submitted,
        week_key=week_key,
    )


@app.route("/request", methods=["POST"])
def submit_requests():
    client_id = _ensure_client_id()
    settings = store.get_app_settings()
    category_ids = request.form.getlist("category_ids")
    expecting_raw = request.form.get("expecting_visit", "").strip().lower()
    if expecting_raw == "yes":
        expecting_visit = True
    elif expecting_raw == "no":
        expecting_visit = False
    else:
        expecting_visit = None

    try:
        count = store.add_client_requests(
            client_id,
            category_ids,
            settings["food_bank_id"],
            expecting_visit=expecting_visit,
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("request_board"))

    flash(f"Thank you! {count} categor{'y' if count == 1 else 'ies'} recorded for this week.", "success")
    return render_template("request_success.html", count=count)


@app.route("/shop")
@app.route("/cart")
@app.route("/confirm")
def legacy_shop_redirect():
    return redirect(url_for("request_board"))


@app.route("/order", methods=["POST"])
def legacy_order_redirect():
    return redirect(url_for("request_board"))


@app.route("/community")
def community_board():
    board = store.get_community_needs()
    return render_template("community.html", board=board)


@app.route("/community/pledge", methods=["GET", "POST"])
def community_pledge():
    board = store.get_community_needs()
    open_categories = board.get("category_items", []) if board.get("published") else []

    if request.method == "POST":
        anonymous = request.form.get("anonymous") == "on"
        donor_name = "" if anonymous else request.form.get("donor_name", "")
        category_id = request.form.get("category_id", "")
        note = request.form.get("note", "")
        try:
            pledge = store.add_category_pledge(donor_name, category_id, note)
        except ValueError as exc:
            flash(str(exc), "error")
            return redirect(url_for("community_pledge"))
        session["pledge_thanks_category"] = pledge["category_name"]
        session["pledge_thanks_category_id"] = pledge["category_id"]
        return redirect(url_for("community_pledge_success"))

    return render_template(
        "community_pledge.html",
        board=board,
        open_categories=open_categories,
    )


@app.route("/community/pledge/thanks")
def community_pledge_success():
    category_name = session.pop("pledge_thanks_category", None)
    category_id = session.pop("pledge_thanks_category_id", None)
    if not category_name:
        return redirect(url_for("community_board"))
    board = store.get_community_needs()
    settings = store.get_app_settings()
    return render_template(
        "community_pledge_success.html",
        category_name=category_name,
        category_id=category_id or "",
        board=board,
        dropoff_instructions=settings.get("donor_dropoff_instructions", ""),
        dropoff_map_url=settings.get("donor_dropoff_map_url", ""),
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
        return redirect(url_for("admin_trends"))
    flash("Incorrect password.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("request_board"))


@app.route("/admin/trends")
@admin_required
def admin_trends():
    settings = store.get_app_settings()
    week_key = request.args.get("week", store.visit_week_key()).strip() or store.visit_week_key()
    report = store.compute_weekly_trends(settings["food_bank_id"], week_key)
    snapshot = store.get_trend_snapshot(settings["food_bank_id"], week_key)
    return render_template(
        "admin_trends.html",
        report=report,
        snapshot=snapshot,
        settings=settings,
        week_key=week_key,
    )


@app.route("/admin/trends/refresh", methods=["POST"])
@admin_required
def admin_trends_refresh():
    settings = store.get_app_settings()
    week_key = request.form.get("week_key", store.visit_week_key()).strip() or store.visit_week_key()
    report = store.compute_weekly_trends(settings["food_bank_id"], week_key)
    store.save_trend_snapshot(settings["food_bank_id"], week_key, report)
    flash(f"Trend snapshot saved for {week_key}.", "success")
    return redirect(url_for("admin_trends", week=week_key))


@app.route("/admin/trends/export.csv")
@admin_required
def admin_trends_export():
    settings = store.get_app_settings()
    week_key = request.args.get("week", store.visit_week_key()).strip() or store.visit_week_key()
    report = store.compute_weekly_trends(settings["food_bank_id"], week_key)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "week",
            "category",
            "clients",
            "demand_pct",
            "vs_last_week_pct",
            f"vs_{report['rolling_weeks']}_week_avg_pct",
            "insight",
        ]
    )
    for row in report["categories"]:
        writer.writerow(
            [
                week_key,
                row["display_name"],
                row["client_count"],
                row["demand_pct"],
                row.get("vs_prior_week_pct", ""),
                row.get("vs_rolling_avg_pct", ""),
                row.get("insight", ""),
            ]
        )

    filename = f"demand-trends-{week_key}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.route("/admin/settings", methods=["GET", "POST"])
@admin_required
def admin_settings():
    settings = store.get_app_settings()
    trip = store.get_trip_settings()
    if request.method == "POST":
        store.save_app_settings(
            {
                "agency_display_name": request.form.get("agency_display_name", ""),
                "food_bank_id": request.form.get("food_bank_id", ""),
                "rolling_weeks": request.form.get("rolling_weeks", settings["rolling_weeks"]),
                "max_fll_pallets": request.form.get("max_fll_pallets", settings["max_fll_pallets"]),
                "high_demand_threshold": request.form.get(
                    "high_demand_threshold", settings["high_demand_threshold"]
                ),
                "donor_dropoff_instructions": request.form.get("donor_dropoff_instructions", ""),
                "agency_hours": request.form.get("agency_hours", ""),
                "agency_about_extra": request.form.get("agency_about_extra", ""),
                "donor_dropoff_map_url": request.form.get("donor_dropoff_map_url", ""),
            }
        )
        store.save_trip_settings(
            {
                "trip_name": request.form.get("trip_name", ""),
                "pickup_date": request.form.get("pickup_date", ""),
                "store_name": request.form.get("store_name", ""),
            }
        )
        flash("Settings saved.", "success")
        return redirect(url_for("admin_settings"))
    return render_template(
        "admin_settings.html",
        settings=store.get_app_settings(),
        trip=store.get_trip_settings(),
    )


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    return redirect(url_for("admin_trends"))


@app.route("/admin/supply", methods=["GET", "POST"])
@admin_required
def admin_supply():
    thresholds = store.get_staff_thresholds()
    categories = store.get_planning_categories(active_only=True)
    level_options = [(v, store.STAFF_THRESHOLD_LABELS[v]) for v in store.STAFF_THRESHOLD_LEVELS]

    if request.method == "POST":
        cat_levels = {}
        for category in categories:
            val = request.form.get(f"cat_{category['id']}", "ok")
            if val in store.STAFF_THRESHOLD_LEVELS:
                cat_levels[category["id"]] = val
        storage_levels = {}
        for storage_type in store.STORAGE_TYPES:
            val = request.form.get(f"storage_{storage_type}", "ok")
            if val in store.STAFF_THRESHOLD_LEVELS:
                storage_levels[storage_type] = val
        store.save_staff_thresholds(cat_levels, storage_levels)
        flash("Supply levels saved.", "success")
        return redirect(url_for("admin_supply"))

    return render_template(
        "admin_supply.html",
        thresholds=thresholds,
        categories=categories,
        cat_levels=thresholds.get("categories", {}),
        storage_levels=thresholds.get("storage", {}),
        storage_types=store.STORAGE_TYPES,
        storage_labels=store.STORAGE_TYPE_LABELS,
        level_options=level_options,
    )


@app.route("/admin/order")
@admin_required
def admin_order():
    week_key = request.args.get("week", store.visit_week_key()).strip() or store.visit_week_key()
    plan = store.compute_order_plan(week_key=week_key)
    return render_template("admin_order.html", plan=plan)


@app.route("/admin/order/export.csv")
@admin_required
def admin_order_export():
    week_key = request.args.get("week", store.visit_week_key()).strip() or store.visit_week_key()
    plan = store.compute_order_plan(week_key=week_key)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["section", "week", "name", "value", "detail"])
    for rec in plan["fll_recommendations"]:
        writer.writerow(
            [
                "fll_pallet",
                week_key,
                rec["display_name"],
                rec["suggested_pallets"],
                rec["reason"],
            ]
        )
    for row in plan["categories"]:
        writer.writerow(
            [
                "category",
                week_key,
                row["display_name"],
                row["priority_score"],
                f"demand={row['demand_pct']}% supply={row['supply_label']}",
            ]
        )
    for row in plan["donor_candidates"]:
        writer.writerow(
            [
                "donor_candidate",
                week_key,
                row["display_name"],
                row["supply_label"],
                row["reason"],
            ]
        )

    filename = f"fll-order-worksheet-{week_key}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.route("/admin/capacity", methods=["GET", "POST"])
@admin_required
def admin_capacity():
    return redirect(url_for("admin_supply"))


@app.route("/admin/community", methods=["GET"])
@admin_required
def admin_community():
    board = store.get_community_needs(admin_preview=True)
    pledges = store.get_all_category_pledges_for_round()
    thresholds = store.get_staff_thresholds()
    blocked_storage = [
        store.STORAGE_TYPE_LABELS[st]
        for st, level in thresholds.get("storage", {}).items()
        if level == "full"
    ]
    return render_template(
        "admin_community.html",
        board=board,
        pledges=pledges,
        blocked_storage=blocked_storage,
    )


@app.route("/admin/inventory", methods=["GET", "POST"])
@admin_required
def admin_inventory():
    return redirect(url_for("admin_trends"))


@app.route("/admin/plan", methods=["GET", "POST"])
@admin_required
def admin_plan():
    return redirect(url_for("admin_trends"))


@app.route("/admin/trip", methods=["POST"])
@admin_required
def admin_trip_settings():
    return redirect(url_for("admin_settings"))


@app.route("/admin/reset", methods=["POST"])
@admin_required
def admin_reset():
    settings = store.get_app_settings()
    result = store.reset_planning_week(settings["food_bank_id"])
    if result["snapshot_saved"]:
        flash(
            f"Planning week reset. Trend snapshot saved for {result['week_key']} "
            f"({result['total_clients']} clients).",
            "success",
        )
    else:
        flash(
            f"Planning week reset for {result['week_key']}. Supply cleared and donor board taken offline.",
            "success",
        )
    return redirect(url_for("admin_settings"))


@app.route("/admin/community/publish", methods=["POST"])
@admin_required
def admin_community_publish():
    published = request.form.get("published", "0") == "1"
    store.set_community_published(published)
    if published:
        flash("Donor board is now live.", "success")
    else:
        flash("Donor board taken offline.", "success")
    next_page = request.form.get("next", "")
    if next_page == "admin_community":
        return redirect(url_for("admin_community"))
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
    try:
        updated = store.update_category_pledge_status(pledge_id, status)
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("admin_community"))
    if updated is None:
        flash("Pledge not found.", "error")
    else:
        flash(f"Pledge marked {status}.", "success")
    return redirect(url_for("admin_community"))


@app.route("/admin/round/<round_id>")
@admin_required
def admin_round_detail(round_id: str):
    del round_id
    return redirect(url_for("admin_trends"))


if __name__ == "__main__":
    app.run(debug=True)
