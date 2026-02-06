from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()

Title = 'CoolStack'

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = 'your_secret_key'
    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or "sqlite:///../instance/coolstack.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_TIME_LIMIT'] = None
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    db.init_app(app)
    migrate.init_app(app, db) 
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # Import and register blueprint with prefix
    from app import routes
    app.register_blueprint(routes.bp, url_prefix='/main')  # ✅ updated

    from app.models import User, Post, Like

    with app.app_context():
        db.create_all()

    return app
