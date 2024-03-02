import os
from flask import current_app
from app import db
from app.models import User
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
import re


def register_user(username, password, email, first_name, last_name):
    if not all([username, password, email, first_name, last_name]):
        return {'error': 'Données manquantes'}, 400

    if User.query.filter_by(username=username).first():
        return {'error': 'Nom d\'utilisateur déjà utilisé'}, 400

    if User.query.filter_by(email=email).first():
        return {'error': 'Email déjà utilisé'}, 400

    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return {'error': 'Format d\'email invalide'}, 400

    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$'
    if not re.match(password_regex, password):
        return {'error': 'Le mot de passe doit contenir au moins 12 caractères, dont une majuscule, une minuscule, un chiffre et un caractère spécial'}, 400

    new_user = User(username=username, email=email, first_name=first_name, last_name=last_name)
    new_user.password = password
    db.session.add(new_user)
    db.session.commit()

    user_directory = os.path.join(current_app.root_path, '..', 'user_storage', username)
    os.makedirs(user_directory, exist_ok=True)

    token = create_access_token(identity=username)
    return {'token': token}, 200

def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        token = create_access_token(identity=username)
        return {'token': token}, 200

    return {'error': 'Identifiants invalides'}, 401


def verify_token():
    try:
        current_user = get_jwt_identity()
        return {'status': 'success', 'message': 'Token valide', 'user': current_user}, 200
    except Exception as e:
        return {'status': 'failure', 'message': 'Erreur lors de la vérification du token'}, 400
