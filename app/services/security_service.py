import os
from datetime import timedelta
from functools import wraps
from os import abort

from flask import abort, current_app as app, jsonify, request, Response, make_response
from flask_jwt_extended import get_jwt_identity, create_access_token, verify_jwt_in_request, get_jwt, decode_token
from jwt import ExpiredSignatureError

from app.models import Week, Expense
from app.services import user_service,email_service


front_url = os.getenv('WEEKLY_FRONT_URL')

def get_raw_token():
    auth_header = request.headers.get('Authorization',None)
    if auth_header:
        token = auth_header.split('Bearer ')[-1]
        return token
    return None

def generate_password_recovery_token(email):
    expires_delta = timedelta(minutes=30)
    additional_claims = {"src":"password_recovery"}
    recovery_token = create_access_token(identity=email,additional_claims=additional_claims,expires_delta=expires_delta)
    return recovery_token

def generate_email_confirmation_token(email):
    expires_delta = timedelta(minutes=30)
    additional_claims = {"src":"email_confirmation"}
    confirmation_token = create_access_token(identity=email,additional_claims=additional_claims,expires_delta=expires_delta)
    return confirmation_token

def generate_access_token(identity):
    access_token = create_access_token(identity, expires_delta=timedelta(days=1))
    return access_token

def require_email_confirmation_token(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('src') != 'email_confirmation':
                app.logger.error("Token without proper src has been used for email confirmation attempt!!")
                abort(401)
            return func(*args, **kwargs)
        except ExpiredSignatureError:
            token = get_raw_token()
            email = decode_token(token,allow_expired=True).get('sub','unknown')
            app.logger.info(f"Expired token used for email confirmation attempt. Sending another confirmation to: {email}")
            email_service.send_email_confirmation_mail(email)
            return jsonify({'message': "Link expired. New confirmation mail has been sent."}), 401
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            abort(500)
    return wrapper

def require_access_token(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('src') is None:
                return func(*args, **kwargs)

            app.logger.error("Token with src has been used for access attempt!!")
            abort(401)
        except ExpiredSignatureError:
            return jsonify({'message': "Your session has expired. Please login."}), 401
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            abort(500)



    return wrapper




def require_password_recovery_token(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('src') != 'password_recovery':
                app.logger.error("Access token has been used to attempt recovering a password!!")
                abort(401)
            return func(*args, **kwargs)
        except ExpiredSignatureError:
            app.logger.info('Password recovery token is expired!')
            return jsonify({'message': "Password recovery token expired"}), 401
        except Exception as e:
            app.logger.error(f"An error occurred: {str(e)}")
            abort(500)
    return wrapper


def cors_header(header_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            response = func(*args,**kwargs)
            if not isinstance(response,Response):
                response = make_response(response)
            response.headers['Access-Control-Expose-Headers'] = header_name
            return response
        return wrapper
    return decorator


def unauthorized_error():
    app.logger.error("Unauthorized!")
    abort(403)



def validate_user_week(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        requesting_user_id = user_service.get_user_by_email(get_jwt_identity()).id
        requested_week_id = request.args.get('id') or request.form.get('id')
        requested_user_id = Week.query.filter_by(id=requested_week_id).first().user_id

        print("REQUESTING USER ID:",requesting_user_id)
        print("REQUESTED USER ID:",requested_user_id)

        if not requested_user_id == requesting_user_id:
            unauthorized_error()
        return func(*args, **kwargs)

    return wrapper


def validate_user_expense(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        requesting_user_id = user_service.get_user_by_email(get_jwt_identity()).id
        requested_expense_id = request.args.get('id') or request.form.get('id')
        expense = Expense.query.filter_by(id=requested_expense_id).first()
        requested_week_id = Week.query.filter_by(id=expense.week_id).first().id
        requested_user_id = Week.query.filter_by(id=requested_week_id).first().user_id
        print("REQUESTING USER ID:",requesting_user_id)
        print("REQUESTED USER ID:",requested_user_id)

        if not requested_user_id == requesting_user_id:
            unauthorized_error()
        return func(*args, **kwargs)

    return wrapper











