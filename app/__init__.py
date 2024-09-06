from flask import Flask
from flask.logging import default_handler
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config
from flask.cli import with_appcontext
from flask_mail import Mail, Message
import os
import click

import logging

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def logger_setup(app):
    app.logger.setLevel(logging.INFO)

    error_file_handler = logging.FileHandler('error_logs.log')
    error_file_handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(pathname)s:%(lineno)d - %(funcName)s]')
    error_file_handler.setFormatter(formatter)
    app.logger.addHandler(error_file_handler)

    info_file_handler = logging.FileHandler('info_logs.log')
    info_file_handler.setLevel(logging.INFO)
    info_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    info_file_handler.setFormatter(info_formatter)
    app.logger.addHandler(info_file_handler)


def clear_db():
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(f'Clear table {table}')
        db.session.execute(table.delete())
    db.session.commit()

@click.command(name='clear-db')
@with_appcontext
def clear_db_command():
    clear_db()
    click.echo('Database cleared.')



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.cli.add_command(clear_db_command)
    logger_setup(app)
    app.logger.setLevel(logging.INFO)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.getenv('WEEKLY_EMAIL_ADDRESS')
    app.config['MAIL_PASSWORD'] = os.getenv('WEEKLY_EMAIL_PASSWORD')

    mail.init_app(app)

    front = os.getenv('WEEKLY_FRONT_URL')

    CORS(app, resources={r"/*": {"origins": front}}, allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    db.init_app(app)
    migrate.init_app(app,db)
    jwt.init_app(app)
    from app.routes import bp as routes_bp
    from app.models import User
    app.register_blueprint(routes_bp)

    return app