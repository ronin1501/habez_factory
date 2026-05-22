from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # ВАЖНО: Импортируем модели внутри функции после инициализации db, 
    # чтобы избежать циклических импортов и дать Alembic их увидеть.
    with app.app_context():
        from app import models
        # Если модели лежат в другом месте, укажите правильный путь:
        # from app.catalog.models import Category, Product 
    
    # Регистрируем блюпринты
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.catalog import catalog_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(catalog_bp, url_prefix='/catalog')

    return app