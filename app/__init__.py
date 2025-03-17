# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
# from flask_login import LoginManager
# from app.config import Config

# # Initialize extensions
# db = SQLAlchemy()
# migrate = Migrate()
# login = LoginManager()
# login.login_view = 'auth.login'

# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)

#     # Initialize Flask extensions
#     db.init_app(app)
#     migrate.init_app(app, db)
#     login.init_app(app)

#     # Import models here
#     from app.models.user import User  # Add this line
#     from app.models.record  import Record

#     # Register blueprints
#     from app.routes import main
#     app.register_blueprint(main.bp)

#     return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_object=None):
    app = Flask(__name__)
    
    if config_object is None:
        app.config.from_object('app.config.Config')
    else:
        app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'main.home'
    login_manager.login_message_category = 'info'

    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app