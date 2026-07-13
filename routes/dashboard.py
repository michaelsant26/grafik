from datetime import date
from calendar import month_name

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract

from extensions import db
from models import Expense

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    today = date.today()

    total_all_time = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(Expense.user_id == current_user.id)
        .scalar()
    )

    total_this_month = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            Expense.user_id == current_user.id,
            extract("year", Expense.date) == today.year,
            extract("month", Expense.date) == today.month,
        )
        .scalar()
    )

    total_transactions = Expense.query.filter_by(user_id=current_user.id).count()

    top_category_row = (
        db.session.query(Expense.category, func.sum(Expense.amount).label("total"))
        .filter(Expense.user_id == current_user.id)
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .first()
    )
    top_category = top_category_row[0] if top_category_row else "-"

    recent_expenses = (
        Expense.query.filter_by(user_id=current_user.id)
        .order_by(Expense.date.desc(), Expense.id.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        total_all_time=total_all_time,
        total_this_month=total_this_month,
        total_transactions=total_transactions,
        top_category=top_category,
        recent_expenses=recent_expenses,
    )


@dashboard_bp.route("/api/chart/by-category")
@login_required
def chart_by_category():
    """Data untuk pie chart: total pengeluaran per kategori (bulan berjalan)."""
    today = date.today()
    rows = (
        db.session.query(Expense.category, func.sum(Expense.amount))
        .filter(
            Expense.user_id == current_user.id,
            extract("year", Expense.date) == today.year,
            extract("month", Expense.date) == today.month,
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    return jsonify({
        "labels": [r[0] for r in rows],
        "values": [round(r[1], 2) for r in rows],
    })


@dashboard_bp.route("/api/chart/monthly-trend")
@login_required
def chart_monthly_trend():
    """Data untuk line/bar chart: tren pengeluaran 6 bulan terakhir."""
    rows = (
        db.session.query(
            extract("year", Expense.date).label("year"),
            extract("month", Expense.date).label("month"),
            func.sum(Expense.amount).label("total"),
        )
        .filter(Expense.user_id == current_user.id)
        .group_by("year", "month")
        .order_by("year", "month")
        .all()
    )

    # Ambil 6 bulan terakhir yang ada datanya
    rows = rows[-6:]

    labels = [f"{month_name[int(r.month)][:3]} {int(r.year)}" for r in rows]
    values = [round(r.total, 2) for r in rows]

    return jsonify({"labels": labels, "values": values})
