"""
WSGI config for quizp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from dotenv import load_dotenv 
from django.core.wsgi import get_wsgi_application

BASE_DIR = Path(__file__).resolve().parent.parent 
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=dotenv_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizp.settings')

application = get_wsgi_application()
