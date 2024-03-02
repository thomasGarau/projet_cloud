from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .services import auth_service
from flask import request
from flask import current_app as app

main = Blueprint('main', __name__)

@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    if not all([username, password, email, first_name, last_name]):
        return jsonify({'error': 'Données manquantes'}), 400

    result, status = auth_service.register_user(username, password, email, first_name, last_name)
    return jsonify(result), status

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    result, status = auth_service.authenticate_user(data.get('username'), data.get('password'))
    return jsonify(result), status

@main.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@main.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    result, status = auth_service.verify_token()
    return jsonify(result), status
