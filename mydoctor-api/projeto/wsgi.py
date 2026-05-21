import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto.settings')

if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    os.makedirs('/tmp/media', exist_ok=True)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application

if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    from django.core.management import call_command

    call_command('migrate', '--noinput', verbosity=0)
    call_command('create_admin', verbosity=0)
