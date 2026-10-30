import os

from flask import Flask

from config import Config
from app.extensions import (
    babel,
    csrf,
    db,
    limiter,
    login_manager,
    migrate,
)


def create_app(config_class=Config):

    app = Flask(
        __name__,
        instance_relative_config=True,
    )

    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    babel.init_app(app)

    # Configure login manager
    login_manager.login_view = "auth.login"
    login_manager.login_message = "يرجى تسجيل الدخول للمتابعة."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):

        from app.models import User

        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    # Register models
    from app import models

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app
