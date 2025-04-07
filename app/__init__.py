from os import getenv
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_apscheduler import APScheduler


if getenv('SENTRY_DSN'):
    import sentry_sdk
    sentry_sdk.init(
        dsn=getenv('SENTRY_DSN'),
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
    )

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'main.index'
login.login_message = 'Please log in to access this page.'
scheduler = APScheduler()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.subdomain_matching = True

    # Add APScheduler configuration
    app.config['SCHEDULER_API_ENABLED'] = False
    app.config['SCHEDULER_TIMEZONE'] = 'UTC'

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    # Register scheduled tasks
    with app.app_context():
        from app.tasks import init_scheduler
        init_scheduler()

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.collector import bp as collector_bp
    app.register_blueprint(collector_bp)

    return app

from app import models