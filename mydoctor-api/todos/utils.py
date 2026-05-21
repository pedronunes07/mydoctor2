from django.urls import reverse
from django.utils.crypto import get_random_string

from .models import ChatRoom, Medico


def get_panel_url(user):
    """URL do painel principal do usuário logado (permanece na área autenticada)."""
    if not user.is_authenticated:
        return reverse('home')
    return reverse('dashboard')


def get_recordings_url(user):
    if not user.is_authenticated:
        return reverse('home')
    if user_has_medico(user):
        return reverse('doctor_recordings')
    return reverse('recorded_list')


def user_has_medico(user):
    """True se o usuário tem perfil de médico vinculado."""
    if not user.is_authenticated:
        return False
    try:
        user.medico
        return True
    except Medico.DoesNotExist:
        return False


def user_can_access_patient_area(user):
    """Pacientes e admin (superuser) podem usar a área do paciente."""
    return user.is_authenticated and (not user_has_medico(user) or user.is_superuser)


def user_can_access_consulta(user, consulta):
    if not user.is_authenticated:
        return False
    if consulta.usuario_id == user.id:
        return True
    if user_has_medico(user) and consulta.medico_id == user.medico.id:
        return True
    if user.is_superuser:
        return True
    return False


def user_can_access_room(user, room):
    if not user.is_authenticated:
        return False
    if room.created_by_id == user.id:
        return True
    if room.consulta_id and user_can_access_consulta(user, room.consulta):
        return True
    if user.is_superuser:
        return True
    return False


def user_can_access_recording(user, recording):
    if not user.is_authenticated:
        return False
    if recording.uploaded_by_id == user.id:
        return True
    if recording.room.consulta_id and user_can_access_consulta(user, recording.room.consulta):
        return True
    if user.is_superuser:
        return True
    return False


def get_or_create_room_for_consulta(consulta, created_by):
    room = ChatRoom.objects.filter(consulta=consulta, closed_at__isnull=True).first()
    if room:
        return room, False
    code = get_random_string(10)
    room = ChatRoom.objects.create(
        code=code,
        created_by=created_by,
        consulta=consulta,
    )
    return room, True
