import uuid
from datetime import datetime, timedelta
from email.policy import default
from enum import Enum

from sqlalchemy import DateTime, String, Boolean, false
from sqlalchemy.types import CHAR

from app.services import expense_service

from app import db
from werkzeug.security import generate_password_hash, check_password_hash

from app.services.formatter_service import format_date


def start_of_week():
    today = datetime.now()
    return today - timedelta(days=today.weekday())

def end_of_week():
    today = datetime.now()
    days_until_end = 6 - today.weekday()
    return today + timedelta(days=days_until_end)

class Currency(Enum):
    GBP = "£"
    PLN = "PLN"
    CHF = "CHF"

    @classmethod
    def get_currencies_names(cls):
        return [currency.name for currency in cls]

    @classmethod
    def get_currencies_symbols(cls):
        return [currency.value for currency in cls]

    @classmethod
    def get_currency_symbol(cls, currency_name):
        try:
            return cls[currency_name].value
        except KeyError:
            return None

    @classmethod
    def get_currency_name(cls, currency_symbol):
        for currency in cls:
            if currency.value == currency_symbol:
                return currency.name
        return None


class User(db.Model):
    id = db.Column(CHAR(36), primary_key=True, default=lambda:str(uuid.uuid4()))
    username = db.Column(db.String(120), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    weeklyPlan = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), default=Currency.PLN.value)
    weeks = db.relationship('Week', back_populates='user')
    email_confirmed = db.Column(Boolean, default= False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_weekly_plan(self, amount):
        self.weeklyPlan = amount

    def set_currency(self, currency_name):
        self.currency = Currency.get_currency_symbol(currency_name)

    def __repr__(self):
        return f'<User {self.username}> <Email {self.email}>'

    def to_json(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "weeklyPlan": self.weeklyPlan,
            "currency": self.currency
        }


class Week(db.Model):
    id = db.Column(CHAR(36), primary_key=True, default=lambda:str(uuid.uuid4()))
    user_id = db.Column(CHAR(36), db.ForeignKey('user.id'))
    week_start = db.Column(DateTime, default=start_of_week)
    week_end = db.Column(DateTime, default=end_of_week)
    user = db.relationship("User", back_populates="weeks")
    expenses = db.relationship("Expense", back_populates="week")

    @format_date
    def get_start_date(self):
        return self.week_start

    @format_date
    def get_end_date(self):
        return self.week_end

    def to_json(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'weekStart': self.week_start.isoformat() if self.week_start else None,
            'weekEnd': self.week_end.isoformat() if self.week_end else None,
            'expenses': expense_service.get_week_expenses_amount(self.id)
        }
    def to_json_xlsx(self):
        return {
            'Week': f'{self.get_start_date()} - {self.get_end_date()}',
            'Total Expenses': expense_service.get_week_expenses_amount(self.id)
        }




class Expense(db.Model):
    id = db.Column(CHAR(36), primary_key=True, default=lambda:str(uuid.uuid4()))
    name = db.Column(String(150),nullable = False)
    amount = db.Column(db.Float, default=0.0)
    week_id = db.Column(CHAR(36), db.ForeignKey('week.id'))
    date = db.Column(DateTime, default=datetime.now)
    week = db.relationship("Week", back_populates="expenses")

    @format_date
    def get_date(self):
        return self.date

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'amount': self.amount,
            'weekId': self.week_id,
            'date': self.date.isoformat() if self.date else None
        }


    def to_json_for_xlsx(self):
        user = User.query.filter_by(id=Week.query.filter_by(id=self.week_id).first().user_id).first()
        return {
            'name': self.name,
            'amount': f'{self.amount} {user.currency}',
            'date': self.get_date() if self.date else None
        }

