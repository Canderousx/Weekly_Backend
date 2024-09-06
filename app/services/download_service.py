import os.path
from functools import wraps
from os import abort
from flask import current_app as app,abort,send_file


def downloadable(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        filepath = func(*args,**kwargs)

        if not os.path.isfile(os.path.join('app',filepath)):
            app.logger.error(f"File '{filepath}' is not a valid file path!")
            abort(404)

        return send_file(filepath, as_attachment=True)
    return wrapper