from datetime import datetime

from app.services.db_service import db_commit
from app.models import Expense, Currency

from app.models import User

from app.services import currency_service

from app import db

from sqlalchemy import func

def expense_currency_calculator(user,amount, expense_currency, expense):
    currency_name = Currency.get_currency_name(user.currency)
    if currency_name != expense_currency:
        expense.amount = currency_service.change_currency(expense_currency, currency_name, amount)
    else:
        expense.amount = amount
    expense.amount = round(expense.amount,2)

@db_commit
def add_expense(week,name,amount,currency_name):
    user = User.query.filter_by(id = week.user_id).first()
    expense = Expense()
    expense_currency_calculator(user,amount,currency_name,expense)
    expense.week_id = week.id
    expense.date = datetime.now()
    expense.name = name
    db.session.add(expense)



def get_week_expenses_amount(week_id):
    expenses = get_all_week_expenses(week_id)
    amount = 0.0
    for expense in expenses:
        amount+= expense.amount
    amount = round(amount,2)
    return amount


def get_week_expenses(week_id,page_size,page):
    return Expense.query.filter_by(week_id = week_id).order_by(Expense.amount.desc(),Expense.date.desc()).paginate(page=page,per_page=page_size)

def get_all_week_expenses(week_id):
    return Expense.query.filter_by(week_id=week_id).all()

def get_expenses_total_quantity(week_id):
    return db.session.query(func.count(Expense.id)).filter(Expense.week_id == week_id).scalar()

@db_commit
def edit_expense(expense_id,user_id, name,amount,currency):
    user = User.query.filter_by(id = user_id).first()
    expense = Expense.query.filter_by(id = expense_id).first()
    expense.name = name
    expense_currency_calculator(user,amount,currency,expense)



