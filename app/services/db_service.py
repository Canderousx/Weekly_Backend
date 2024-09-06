from app import db
from flask import current_app


def db_commit(func):
    def commit_db_changes(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            current_app.logger.info("Commiting updates in db.")
            db.session.commit()
            return result
        except Exception as e:
            current_app.logger.error("There was an error during commiting db changes. Rolling back")
            db.session.rollback()
            raise e
    return commit_db_changes











