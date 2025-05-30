
"""
Cấu hình ứng dụng Achievo
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Cấu hình cơ bản cho ứng dụng"""
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database configuration
    FIREBASE_CREDENTIALS_PATH = os.getenv('FIREBASE_CREDENTIALS_PATH')
    POSTGRES_URL = os.getenv('POSTGRES_URL')
    
    # Cardano configuration
    KOIOS_API_URL = os.getenv('KOIOS_API_URL', 'https://preprod.koios.rest/api/v1')
    KOIOS_API_TOKEN = os.getenv('KOIOS_API_TOKEN')
    CARDANO_NETWORK = os.getenv('CARDANO_NETWORK', 'preprod')
    
    # IPFS configuration
    PINATA_API_KEY = os.getenv('PINATA_API_KEY')
    PINATA_SECRET_KEY = os.getenv('PINATA_SECRET_KEY')
    PINATA_JWT = os.getenv('PINATA_JWT')
    IPFS_GATEWAY = os.getenv('IPFS_GATEWAY', 'https://harlequin-impressed-guan-658.mypinata.cloud/ipfs/')
    
    # Firebase configuration
    FIREBASE_PROJECT_ID = os.getenv('FIREBASE_PROJECT_ID')
    FIREBASE_AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
    
    # Security configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    RATE_LIMIT_STORAGE_URL = os.getenv('RATE_LIMIT_STORAGE_URL', 'memory://')
    
    # Email configuration (for notifications)
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    SENTRY_DSN = os.getenv('SENTRY_DSN')


class DevelopmentConfig(Config):
    """Cấu hình cho môi trường development"""
    DEBUG = True


class ProductionConfig(Config):
    """Cấu hình cho môi trường production"""
    DEBUG = False
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting for production
    RATE_LIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    
    # Enhanced logging
    LOG_LEVEL = 'WARNING'
    
    # Production Cardano network
    CARDANO_NETWORK = os.getenv('CARDANO_NETWORK', 'mainnet')
    KOIOS_API_URL = os.getenv('KOIOS_API_URL', 'https://api.koios.rest/api/v1')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
