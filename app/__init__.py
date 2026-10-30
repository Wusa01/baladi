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
        instance_relative_config=True
    )

    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    babel.init_app(app)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app
