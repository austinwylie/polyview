"""
WSGI config for yolo_nemesis project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os

import sys

sys.path.append('/home/bitnami/apps/django/django_projects/yolo_nemesis')
os.environ.setdefault("PYTHON_EGG_CACHE",
                      '/home/bitnami/apps/django/django_projects/yolo_nemesis/egg_cache')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "yolo_nemesis.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
