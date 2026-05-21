import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto.settings')

if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    os.makedirs('/tmp/media', exist_ok=True)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application

if os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'):
    try:
        from django.core.management import call_command

        call_command('migrate', '--noinput', verbosity=0)
    except Exception:
        pass
