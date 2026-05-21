from .models import Medico


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
