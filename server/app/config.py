import logging

class Config:
    LOGGING_LEVEL = logging.INFO
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 1 jour (en secondes)
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 jours pour un token refresh (facultatif)
