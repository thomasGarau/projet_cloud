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
from .models.file_models import File
from .models.user_models import User
import shutil
from .services.compression_service import test_compression_decompression


migrate = Migrate()
jwt = JWTManager()
app = None

def create_app():
    global app
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
    #with app.app_context():
    #  empty_user_storage()
    #  delete_all_entries()
    #test_compression_decompression()
    return app

def delete_all_entries():
    try:
        db.session.query(File).delete()
        db.session.query(User).delete()
        
        db.session.commit() 
        print("Toutes les entrées ont été supprimées.")
    except Exception as e:
        db.session.rollback() 
        print(f"Erreur lors de la suppression des entrées : {e}")

def empty_user_storage():
    user_storage_path = os.path.join('./user_storage')
    for username in os.listdir(user_storage_path):
        user_folder_path = os.path.join(user_storage_path, username)
        if os.path.isdir(user_folder_path):
            for file in os.listdir(user_folder_path):
                file_path = os.path.join(user_folder_path, file)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Erreur lors de la suppression de {file_path}: {e}")

    print("Les dossiers des utilisateurs ont été vidés.")


