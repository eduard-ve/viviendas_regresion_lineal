import os
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Configuración base"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Datos
    DATASET_PATH = os.environ.get('DATASET_PATH') or BASE_DIR / 'dataset_vivienda.xlsx'
    API_EXCHANGE_URL = 'https://open.er-api.com/v6/latest/USD'
    FALLBACK_EXCHANGE_RATE = 0.00025  # COP a USD
    
    # Paginación
    ITEMS_PER_PAGE = 10
    MAX_ITEMS_PER_PAGE = 100
    
    # Cache (para futuras mejoras)
    CACHE_TIMEOUT = 300  # 5 minutos
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Gráficos
    PLOT_DPI = 100
    PLOT_FIGSIZE = (10, 6)
    PLOT_STYLE = 'seaborn-v0_8'

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    # En producción, usar variables de entorno para datos sensibles
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Configuraciones de seguridad
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False

# Mapeo de configuraciones
config_mapping = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtener configuración basada en la variable de entorno"""
    env = os.environ.get('FLASK_ENV', 'default')
    return config_mapping.get(env, DevelopmentConfig)