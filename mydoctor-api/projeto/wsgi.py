import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto.settings')

if os.environ.get('VERCEL'):
    os.makedirs('/tmp/media', exist_ok=True)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application

if os.environ.get('VERCEL'):
    from django.core.management import call_command

    call_command('migrate', '--noinput', verbosity=0)
