import os
from flask import current_app
from app import db
from app.models import User
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity


def register_user(username, password):
    if not username or not password:
        return {'error': 'Données manquantes'}, 400

    if User.query.filter_by(username=username).first():
        print('Nom d\'utilisateur déjà utilisé')
        return {'error': 'Nom d\'utilisateur déjà utilisé'}, 400

    new_user = User(username=username)
    new_user.password = password
    db.session.add(new_user)
    db.session.commit()

    user_directory = os.path.join(current_app.root_path, '..', 'user_storage', username)
    os.makedirs(user_directory, exist_ok=True)

    return {'message': 'Utilisateur créé avec succès'}, 201

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
