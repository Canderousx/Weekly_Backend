from app.models import Expense, Week
from app.services.xlsx_service import week_to_xlsx_file, summary_to_xlsx_file
from app import db
from sqlalchemy import func


@week_to_xlsx_file(user_id_key='week.user_id',week_id_key='week.id')
def export_to_xlsx(week):
    expenses = Expense.query.filter_by(week_id= week.id).all()
    return [expense.to_json_for_xlsx() for expense in expenses]


def get_all_weeks(user_id):
    return Week.query.filter_by(user_id = user_id).all()

def get_weeks_total_size(user_id):
    return db.session.query(func.count(Week.id)).filter(Week.user_id == user_id).scalar()

def get_all_weeks_pageable(user_id,page_size,page):
    return Week.query.filter_by(user_id = user_id).order_by(Week.week_end.desc()).paginate(page=page,per_page=page_size)

@summary_to_xlsx_file()
def summary_to_xlsx(user):
    weeks = get_all_weeks(user.id)
    return [week.to_json_xlsx() for week in weeks]
