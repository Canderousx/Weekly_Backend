import os.path
from os import abort

from flask import current_app as app, request, Blueprint, Response, jsonify, send_file,abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services import expense_service, user_service,week_service
from app import db
from app.models import Currency, Expense, Week
from app.services.download_service import downloadable
from app.services.security_service import validate_user_week, validate_user_expense, cors_header, \
    require_password_recovery_token, require_email_confirmation_token, require_access_token
from app.services import stats_service, email_service,security_service


bp = Blueprint('auth',__name__)

@bp.before_request
def print_data():
    print("REQUEST FROM:",request.host,request.host_url)

@bp.route('/signup', methods = ['POST'])
def signup():
    data = request.json
    if data is not None and 'username' in data and 'email' in data and 'password' in data:
        email = data['email']
        username = data['username']
        password = data['password']
        if not user_service.email_exists(email) and not user_service.username_exists(username):
            user_service.add_user(username, email, password)
            email_service.send_email_confirmation_mail(email)
            return jsonify({"message":"Signup successful! To activate your account you need to confirm your email address! Check your email."}),200
        else:
            return jsonify({"message":"Username or email already exists. Please login!"}),403

    else:
        app.logger.error("Required query params not found")
        abort(404)


@bp.route('/confirmEmail', methods = ['GET'])
@require_email_confirmation_token
def confirm_email():
    email = get_jwt_identity()
    user_service.confirm_user(email)
    return jsonify({"message":"Your email has been confirmed! You can now login!"})


@bp.route("/email_exists",methods = ['POST'])
def email_exists():
    email = request.json['email']
    print('email to check:',email)
    exists = user_service.email_exists(email)
    print('exists:',exists)
    return jsonify({"emailExists": exists })

@bp.route("/username_exists",methods = ['POST'])
def username_exists():
    username = request.json['username']
    print('username to check:',username)
    exists = user_service.username_exists(username)
    print('exists:',exists)
    return jsonify({"usernameExists": exists})



@bp.route("/login",methods = ['POST'])
def login():
    data = request.json
    if data is not None and 'email' in data and 'password' in data:
        email = data['email']
        password = data['password']
        token = user_service.login(email, password)
        if isinstance(token, str):
            return jsonify({"authToken": token})
        elif isinstance(token, tuple):
            return token
        else:
            return jsonify({"message": "Invalid username or password!"}), 403

    else:
        app.logger.error("Invalid request data")
        abort(400)

@bp.route("/sendPasswordRecoveryMail",methods = ['POST'])
def send_recovery_token():
    email = request.json['email']
    return email_service.send_password_recovery_email(email)



@bp.route("/recoverPassword",methods=['POST'])
@require_password_recovery_token
def password_recovery():
    password = request.json['password']
    user_service.change_password(get_jwt_identity(),password)
    return jsonify({"message":"Password has been changed. You can now login"}),200



@bp.route("/getCurrenciesNames",methods = ['GET'])
@require_access_token
def get_currencies_names():
    return jsonify({"names":Currency.get_currencies_names()})



@bp.route("/getCurrentUser",methods = ['GET'])
@require_access_token
def get_current_user():
    user_email = get_jwt_identity()
    print("user email:",user_email)
    current_user = user_service.get_user_by_email(user_email)
    if current_user is None:
        app.logger.error("Current user not found!")
        abort(404)
    return jsonify(current_user.to_json())


@bp.route("/getUserCurrency",methods = ['GET'])
@require_access_token
def get_user_currency():
    return jsonify({"currency": user_service.get_user_by_email(get_jwt_identity()).currency})




@bp.route("/setWeeklyPlan",methods = ['POST'])
@require_access_token
def set_weekly_plan():
    data = request.json
    user = user_service.get_user_by_email(get_jwt_identity())
    if user_service.set_user_weekly_plan(data, user):
        return jsonify({"message":"Weekly Plan saved successfully!"}),200
    else:
        app.logger.error("There was an error during Weekly Plan saving for user:",user.id)
        abort(500)

@bp.route("/editWeeklyPlan",methods = ['POST'])
@require_access_token
def edit_weekly_plan():
    data = request.json
    user = user_service.get_user_by_email(get_jwt_identity())
    if user_service.edit_user_weekly_plan(data, user):
        return jsonify({"message":"Weekly Plan saved successfully!"}),200
    else:
        app.logger.error("There was an error during Weekly Plan saving for user:",user.id)
        abort(500)





@bp.route("/getCurrentWeek",methods = ['GET'])
@require_access_token
def get_current_week():
    user = user_service.get_user_by_email(get_jwt_identity())
    week = user_service.get_today_week(user)
    return jsonify(week.to_json())


@bp.route("/addExpense",methods = ['POST'])
@require_access_token
def add_expense():
    data = request.json
    print("DATA CURRENCY:",data['currency'])
    week = user_service.get_today_week(user_service.get_user_by_email(get_jwt_identity()))
    expense_service.add_expense(week, data['name'], data['amount'], data['currency'])
    return jsonify({"message":"Expense added successfully"})

@bp.route("/getExpense",methods = ['GET'])
@require_access_token
@validate_user_expense
def get_expense():
    expense_id = request.args.get('id','not provided')
    if expense_id != 'not provided':
        return jsonify(Expense.query.filter_by(id = expense_id).first().to_json()),200
    else:
        app.logger.error("Couldn't load desired object.")
        abort(500)



@bp.route("/getExpenses",methods = ['GET'])
@require_access_token
@validate_user_week
@cors_header(header_name="total_size")
def get_expenses():
    page_size = int(request.args.get('page_size',10))
    page = int(request.args.get('page',1))
    week_id = request.args.get('id',"not_provided")
    print("WEEK_ID:",week_id)
    expenses = expense_service.get_week_expenses(week_id,page_size,page)
    total_size = expense_service.get_expenses_total_quantity(week_id)
    if expenses is not None:
        expenses_json = [expense.to_json() for expense in expenses]
        response = jsonify({"expenses":expenses_json})
        response.headers['total_size'] = total_size
        return response,200
    else:
        app.logger.error("Expenses not found!")
        abort(404)


@bp.route("/editExpense",methods = ['POST'])
@require_access_token
def edit_expense():
    expense_id = request.args.get('id',"not provided")
    if expense_id != 'not provided':
        expense_service.edit_expense(expense_id, user_service.get_user_by_email(get_jwt_identity()).id, request.json['name'], request.json['amount'], request.json['currency'])
        return jsonify({"message":"Changes has been saved"}),200
    else:
        app.logger.error("Missing expense ID in URL")
        abort(500)


@bp.route("/deleteExpense",methods = ['DELETE'])
@require_access_token
def delete_expense():
    expense_id = request.args.get('id',"not provided")
    if expense_id != 'not provided':
        expense = Expense.query.filter_by(id=expense_id).first()
        user = user_service.get_user_by_email(get_jwt_identity())
        week = user_service.get_today_week(user)
        if week.id == expense.week_id:
            db.session.delete(expense)
            db.session.commit()
            return jsonify({"message": "Expense has been deleted"}), 200
        else:
            app.logger.error("Unauthorized!")
            abort(401)

    else:
        app.logger.error("Missing expense ID in URL")
        abort(500)


@bp.route('/exportToXlsx', methods=['GET'])
@require_access_token
@validate_user_week
@downloadable
def export_to_xlsx():
    week_id = request.args.get('id', "not provided")
    week = Week.query.filter_by(id=week_id).first()

    if not week:
        app.logger.error("Week id:",week_id,"not found")
        abort(404)

    result = week_service.export_to_xlsx(week)

    filename = f'user_{week.user_id}_week_{week.id}.xlsx'
    filepath = os.path.join('resources', 'generated', 'xlsx', filename)

    return filepath


@bp.route('/getAverageWeeklyExpense', methods=['GET'])
@require_access_token
def get_average_week_expense():
    user = user_service.get_user_by_email(get_jwt_identity())
    avg = stats_service.get_average_week_expense(user.id)
    return jsonify({"average":avg})

@bp.route('/getAverageTotalExpense', methods=['GET'])
@require_access_token
def get_average_total_expense():
    user = user_service.get_user_by_email(get_jwt_identity())
    avg = stats_service.get_average_total_expense(user.id)
    return jsonify({"average":avg})

@bp.route('/howManyWeeks', methods=['GET'])
@require_access_token
def how_many_weeks():
    quantity = len(week_service.get_all_weeks(user_service.get_user_by_email(get_jwt_identity()).id))
    return jsonify({"quantity":quantity})

@bp.route('/getWeeks', methods=['GET'])
@require_access_token
@cors_header(header_name="total_size")
def get_weeks():
    page = request.args.get('page',default= 1)
    page_size = request.args.get('page_size',default=10)
    user = user_service.get_user_by_email(get_jwt_identity())
    weeks = week_service.get_all_weeks_pageable(user_id=user.id,page=int(page),page_size=int(page_size))
    total_size = week_service.get_weeks_total_size(user.id)
    weeks_json = [week.to_json() for week in weeks]
    response = jsonify({"weeks":weeks_json})
    response.headers['total_size'] = total_size
    return response,200

@bp.route('/exportSummaryToXlsx', methods=['GET'])
@require_access_token
@downloadable
def summary_to_xlsx():
    user = user_service.get_user_by_email(get_jwt_identity())

    if not user:
        app.logger.error("User not found")
        abort(404)

    result = week_service.summary_to_xlsx(user)

    filename = f'user_{user.id}_weekly_summary.xlsx'
    filepath = os.path.join('resources', 'generated', 'xlsx', filename)

    return filepath














