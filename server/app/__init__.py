from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os
from flask_cors import CORS
import logging
from .config import Config
from .extensions import db
from .routes.user_routes import user_bp
from .routes.user_files_routes import user_files_bp

migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_object(Config)
    app.logger.setLevel(app.config['LOGGING_LEVEL'])
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['USER_STORAGE'] = os.path.join(os.path.dirname(app.instance_path), 'user_storage')



    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(user_files_bp, url_prefix='/files')

    return app
