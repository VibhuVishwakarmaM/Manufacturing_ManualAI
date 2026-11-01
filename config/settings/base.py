import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-manufacturing-manual-ai-prod-key-hackathon-2026')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,0.0.0.0').split(',') if host.strip()]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',

    # Project core apps
    'apps.accounts.apps.AccountsConfig',
    'apps.machines.apps.MachinesConfig',
    'apps.manuals.apps.ManualsConfig',
    'apps.document_processing.apps.DocumentProcessingConfig',
    'apps.rag_engine.apps.RagEngineConfig',
    'apps.question_history.apps.QuestionHistoryConfig',
    'apps.dashboard.apps.DashboardConfig',
    'apps.audit_logs.apps.AuditLogsConfig',
    'apps.notifications.apps.NotificationsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.dashboard.context_processors.app_settings_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database Configuration
# Default: PostgreSQL as required by official problem specifications.
# In local development without an active Postgres daemon, fall back gracefully if enabled.
DB_ENGINE = os.getenv('DB_ENGINE', 'django.db.backends.postgresql')
DB_NAME = os.getenv('DB_NAME', 'manufacturing_manuals')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
USE_SQLITE_FALLBACK = os.getenv('USE_SQLITE_FALLBACK', 'True').lower() in ('true', '1', 't')

# Test environment detection or check if Postgres is running
IS_TESTING = 'pytest' in sys.modules or 'test' in sys.argv

def configure_database():
    if IS_TESTING or (USE_SQLITE_FALLBACK and DB_ENGINE == 'django.db.backends.sqlite3'):
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
    
    # Try PostgreSQL configuration
    if DB_ENGINE == 'django.db.backends.postgresql':
        # Check if Postgres is reachable or if we need fallback
        if USE_SQLITE_FALLBACK:
            try:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                port = int(DB_PORT)
                res = s.connect_ex((DB_HOST, port))
                s.close()
                if res != 0:
                    # Postgres port not reachable, use SQLite fallback for seamless execution
                    return {
                        'default': {
                            'ENGINE': 'django.db.backends.sqlite3',
                            'NAME': BASE_DIR / 'db.sqlite3',
                        }
                    }
            except Exception:
                pass

        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': DB_NAME,
                'USER': DB_USER,
                'PASSWORD': DB_PASSWORD,
                'HOST': DB_HOST,
                'PORT': DB_PORT,
            }
        }

    return {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

DATABASES = configure_database()

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 6},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (PDF Manuals)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Django REST Framework Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS configuration
CORS_ALLOW_ALL_ORIGINS = DEBUG

# ==============================================================================
# AI & RAG CONFIGURATION
# ==============================================================================
AI_SETTINGS = {
    'LLM_PROVIDER': os.getenv('LLM_PROVIDER', 'mock'),
    'LLM_MODEL': os.getenv('LLM_MODEL', 'gpt-4o-mini'),
    'LLM_API_KEY': os.getenv('LLM_API_KEY', ''),
    'LLM_API_BASE_URL': os.getenv('LLM_API_BASE_URL', 'https://api.openai.com/v1'),

    'EMBEDDING_PROVIDER': os.getenv('EMBEDDING_PROVIDER', 'mock'),
    'EMBEDDING_MODEL': os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small'),
    'EMBEDDING_API_KEY': os.getenv('EMBEDDING_API_KEY', ''),
    'EMBEDDING_DIMENSION': int(os.getenv('EMBEDDING_DIMENSION', '1536')),

    'VECTOR_STORE_PROVIDER': os.getenv('VECTOR_STORE_PROVIDER', 'in_db'),
    'VECTOR_COLLECTION': os.getenv('VECTOR_COLLECTION', 'manual_chunks'),
    'VECTOR_STORE_URL': os.getenv('VECTOR_STORE_URL', ''),

    'CHUNK_SIZE': int(os.getenv('CHUNK_SIZE', '500')),
    'CHUNK_OVERLAP': int(os.getenv('CHUNK_OVERLAP', '100')),
    'TOP_K': int(os.getenv('TOP_K', '4')),
    'SIMILARITY_THRESHOLD': float(os.getenv('SIMILARITY_THRESHOLD', '0.65')),

    'MAX_UPLOAD_SIZE_MB': int(os.getenv('MAX_UPLOAD_SIZE_MB', '25')),
    'ALLOWED_PDF_TYPES': [t.strip() for t in os.getenv('ALLOWED_PDF_TYPES', 'application/pdf').split(',')],
    'RAG_PROMPT_VERSION': os.getenv('RAG_PROMPT_VERSION', 'v1'),
}
