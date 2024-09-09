from app.services import week_service
from app.services import expense_service




def get_average_week_expense(user_id):
    weeks = week_service.get_all_weeks(user_id)
    quantity = len(weeks)
    sum_expenses = 0.0
    for week in  weeks:
        sum_expenses += expense_service.get_week_expenses_amount(week.id)
    return  round(sum_expenses / quantity,2)


def get_average_total_expense(user_id):
    weeks = week_service.get_all_weeks(user_id)
    expenses = []
    for week in weeks:
        expenses.extend(expense_service.get_all_week_expenses(week.id))

    if not expenses or len(expenses) == 0:
        return 0.0

    sum_expenses = 0.0
    for expense in expenses:
        sum_expenses += expense.amount

    return round(sum_expenses / len(expenses),2)


