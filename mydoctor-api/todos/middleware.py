from django.contrib.auth import login
from django.contrib.auth.models import User

from .models import Medico


AUTH_SNAPSHOT_KEY = 'mydoctor_auth_snapshot'


def build_auth_snapshot(user):
    snapshot = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
    }
    try:
        snapshot['medico'] = {
            'crm': user.medico.crm,
            'especialidade': user.medico.especialidade,
        }
    except Medico.DoesNotExist:
        snapshot['medico'] = None
    return snapshot


def restore_user_from_snapshot(snapshot):
    if not snapshot or not snapshot.get('username'):
        return None

    user, _ = User.objects.get_or_create(username=snapshot['username'])
    user.email = snapshot.get('email', '')
    user.first_name = snapshot.get('first_name', '')
    user.last_name = snapshot.get('last_name', '')
    user.is_staff = bool(snapshot.get('is_staff'))
    user.is_superuser = bool(snapshot.get('is_superuser'))
    user.is_active = True
    user.save()

    medico = snapshot.get('medico')
    if medico and medico.get('crm'):
        Medico.objects.update_or_create(
            user=user,
            defaults={
                'crm': medico['crm'],
                'especialidade': medico.get('especialidade', ''),
            },
        )
    return user


class SignedCookieAuthRecoveryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.session[AUTH_SNAPSHOT_KEY] = build_auth_snapshot(request.user)
        else:
            user = restore_user_from_snapshot(request.session.get(AUTH_SNAPSHOT_KEY))
            if user:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                request.user = user

        return self.get_response(request)
