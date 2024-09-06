from datetime import datetime
from functools import wraps


def format_date(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        date = func(*args,**kwargs)
        if not isinstance(date,datetime):
            raise ValueError('Function must return an instance of datetime')

        formatted_date = date.strftime('%d.%m.%Y')
        return formatted_date
    return wrapper
