from datetime import datetime
from app import db
from app.services.db_service import db_commit
from app.models import User, Week, start_of_week, end_of_week
from app.models import Currency
from app.services import security_service
from flask import current_app as app, jsonify


@db_commit
def add_user(username,email,password):
    user = User()
    user.username = username
    user.email = email
    user.set_password(password)
    user.email_confirmed = False
    db.session.add(user)


@db_commit
def confirm_user(email):
    user = User.query.filter_by(email = email).first()
    user.email_confirmed = True

@db_commit
def add_week(user):
    week = Week()
    week.user_id = user.id
    week.week_start = start_of_week()
    week.week_end = end_of_week()
    db.session.add(week)
    return week

def email_exists(email):
    user = User.query.filter_by(email = email).first()
    return user is not None

def username_exists(username):
    user = User.query.filter_by(username = username).first()
    return user is not None

@db_commit
def change_password(email,password):
    user = get_user_by_email(email)
    user.set_password(password)
    app.logger.info(f"User: {user.id} password has been changed!")

def login (email, password):
    user = User.query.filter_by(email = email).first()
    if user:
        if not user.email_confirmed:
            app.logger.info(f'User: {email} tried to login without confirmation.')
            return jsonify({"message":"You need to confirm your email address first!"}),403
        if User.check_password(user,password):
            return security_service.generate_access_token(email)
        else:
            return None

    else:
        app.logger.info(f"User with email {email} doesn't exist")
        return None


def get_user_by_email(email):
    user = User.query.filter_by(email = email).first()
    if user.weeklyPlan is None:
        user.weeklyPlan = 0.0
    if user.currency is None:
        user.currency = Currency.PLN.value
    return user

@db_commit
def set_user_weekly_plan(data,user):
    if data.get('weeklyPlan') is None or data.get('currency') is None:
        app.logger.error('Missing data')
        return False
    if user.weeklyPlan is None:
        app.logger.error("User weekly plan already exist")
        return False
    user.set_weekly_plan(data['weeklyPlan'])
    user.set_currency(data['currency'])
    return True

@db_commit
def edit_user_weekly_plan(data,user):
    if data.get('weeklyPlan') is None:
        app.logger.error('Missing data')
        return False
    user.set_weekly_plan(data['weeklyPlan'])
    return True

def get_today_week(user):
    today = datetime.now()
    week = Week.query.filter_by(user_id=user.id) \
        .filter(Week.week_start <= today, Week.week_end >= today) \
        .first()
    if week is None:
        week = add_week(user)
    return week


