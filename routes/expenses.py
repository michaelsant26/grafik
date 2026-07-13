import csv
import io
from datetime import datetime

from flask import (
    Blueprint, render_template, redirect, url_for, flash, request, Response, current_app
)
from flask_login import login_required, current_user

from extensions import db
from models import Expense
from forms import ExpenseForm

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/expenses")
@login_required
def list_expenses():
    page = request.args.get("page", 1, type=int)
    category = request.args.get("category", "")
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    query = Expense.query.filter_by(user_id=current_user.id)

    if category:
        query = query.filter(Expense.category == category)
    if start_date:
        try:
            sd = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(Expense.date >= sd)
        except ValueError:
            pass
    if end_date:
        try:
            ed = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(Expense.date <= ed)
        except ValueError:
            pass

    pagination = query.order_by(Expense.date.desc(), Expense.id.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    total_filtered = sum(e.amount for e in query.all())

    return render_template(
        "expenses/list.html",
        expenses=pagination.items,
        pagination=pagination,
        categories=current_app.config["CATEGORIES"],
        selected_category=category,
        start_date=start_date,
        end_date=end_date,
        total_filtered=total_filtered,
    )


@expenses_bp.route("/expenses/add", methods=["GET", "POST"])
@login_required
def add_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            user_id=current_user.id,
            amount=form.amount.data,
            category=form.category.data,
            description=form.description.data.strip() if form.description.data else "",
            date=form.date.data,
        )
        db.session.add(expense)
        db.session.commit()
        flash("Pengeluaran berhasil ditambahkan.", "success")
        return redirect(url_for("expenses.list_expenses"))

    return render_template("expenses/form.html", form=form, title="Tambah Pengeluaran")


@expenses_bp.route("/expenses/edit/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    form = ExpenseForm(obj=expense)

    if form.validate_on_submit():
        expense.amount = form.amount.data
        expense.category = form.category.data
        expense.description = form.description.data.strip() if form.description.data else ""
        expense.date = form.date.data
        db.session.commit()
        flash("Pengeluaran berhasil diperbarui.", "success")
        return redirect(url_for("expenses.list_expenses"))

    return render_template("expenses/form.html", form=form, title="Edit Pengeluaran")


@expenses_bp.route("/expenses/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash("Pengeluaran berhasil dihapus.", "info")
    return redirect(url_for("expenses.list_expenses"))


@expenses_bp.route("/expenses/export")
@login_required
def export_csv():
    expenses = (
        Expense.query.filter_by(user_id=current_user.id)
        .order_by(Expense.date.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Tanggal", "Kategori", "Deskripsi", "Jumlah (Rp)"])
    for e in expenses:
        writer.writerow([e.date.strftime("%Y-%m-%d"), e.category, e.description, e.amount])

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=pengeluaran.csv"
    return response
