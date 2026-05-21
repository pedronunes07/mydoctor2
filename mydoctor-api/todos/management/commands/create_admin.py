import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Cria conta de administrador para testes (superuser).'

    def add_arguments(self, parser):
        parser.add_argument('--username', default=None)
        parser.add_argument('--email', default=None)
        parser.add_argument('--password', default=None)
        parser.add_argument('--force', action='store_true', help='Atualiza a senha se o usuário já existir.')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username'] or os.environ.get('ADMIN_USERNAME', 'admin')
        email = options['email'] or os.environ.get('ADMIN_EMAIL', 'admin@mydoctor.local')
        password = options['password'] or os.environ.get('ADMIN_PASSWORD', 'Admin@MyDoctor2026')
        force = options['force']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Admin criado: {username} / {email}'))
        elif force:
            user.email = email
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.WARNING(f'Admin atualizado: {username}'))
        else:
            self.stdout.write(self.style.NOTICE(f'Admin já existe: {username} (use --force para resetar senha)'))
