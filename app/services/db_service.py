from app import db


def db_commit(func):
    def commit_db_changes(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            print("Commiting updates in db.")
            db.session.commit()
            return result
        except Exception as e:
            print("There was an error during commiting db changes. Rolling back")
            db.session.rollback()
            raise e
    return commit_db_changes











