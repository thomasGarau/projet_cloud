from flask_jwt_extended import JWTManager

def setup_jwt(app):
    jwt = JWTManager(app)

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return {'error': 'Accès non autorisé. Veuillez vous connecter.'}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return {'error': 'Token invalide. Veuillez vous reconnecter.'}, 422

    @jwt.expired_token_loader
    def expired_token_callback(callback):
        return {'error': 'Token expiré. Veuillez vous reconnecter.'}, 401
