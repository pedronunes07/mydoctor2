from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import ChatRoom, Medico, Recording
from .utils import get_panel_url
from .views import get_medico_by_numeric_crm, only_digits


class NumericInputTests(TestCase):
    def test_only_digits_removes_non_numeric_characters(self):
        self.assertEqual(only_digits('(22) 99999-0000'), '22999990000')
        self.assertEqual(only_digits('CRM-12345'), '12345')

    def test_register_rejects_empty_numeric_phone(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Paciente Teste',
            'phone': 'abc',
            'username': 'paciente',
            'birthdate': '2000-01-01',
            'email': 'paciente@example.com',
            'password': 'SenhaForte123',
            'password2': 'SenhaForte123',
        }, follow=True)

        self.assertContains(response, 'Telefone deve conter apenas')
        self.assertFalse(User.objects.filter(username='paciente').exists())

    def test_register_stores_numeric_phone_and_crm(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Medico Teste',
            'phone': '(22) 98888-7777',
            'username': 'medico',
            'birthdate': '1990-01-01',
            'email': 'medico@example.com',
            'is_medico': 'on',
            'crm': 'CRM-12345',
            'especialidade': 'clinico',
            'password': 'SenhaForte123',
            'password2': 'SenhaForte123',
        })

        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(username='medico')
        self.assertTrue(user.last_name.startswith('22988887777 /'))
        self.assertEqual(Medico.objects.get(user=user).crm, '12345')

    def test_numeric_crm_lookup_supports_old_formatted_records(self):
        user = User.objects.create_user(username='doctor', password='SenhaForte123')
        Medico.objects.create(user=user, crm='CRM-12345', especialidade='clinico')

        self.assertEqual(get_medico_by_numeric_crm('12345').user, user)

    def test_logged_patient_back_button_points_to_dashboard(self):
        user = User.objects.create_user(username='paciente', password='SenhaForte123')
        self.client.force_login(user)

        response = self.client.get(reverse('recorded_list'))

        self.assertContains(response, f'href="{reverse("dashboard")}"')
        self.assertContains(response, 'Voltar')

    def test_logged_user_does_not_return_to_public_pages(self):
        user = User.objects.create_user(username='paciente', password='SenhaForte123')
        self.client.force_login(user)

        for url_name in ('home', 'login', 'register'):
            response = self.client.get(reverse(url_name))
            self.assertRedirects(response, reverse('dashboard'))

    def test_logged_users_return_to_services_dashboard(self):
        doctor = User.objects.create_user(username='doctor-user', password='SenhaForte123')
        Medico.objects.create(user=doctor, crm='8888', especialidade='clinico')

        self.assertEqual(get_panel_url(doctor), reverse('dashboard'))

        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='SenhaForte123',
        )
        Medico.objects.create(user=user, crm='9999', especialidade='clinico')

        self.assertEqual(get_panel_url(user), reverse('dashboard'))

    def test_recording_upload_saves_media(self):
        user = User.objects.create_user(username='paciente', password='SenhaForte123')
        room = ChatRoom.objects.create(code='abc123', created_by=user)
        self.client.force_login(user)
        media = SimpleUploadedFile('consulta.webm', b'webm-data', content_type='video/webm')

        response = self.client.post(reverse('upload_recording_api', args=[room.code]), {
            'file': media,
            'duration': '12',
        })

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['ok'])
        recording = Recording.objects.get(room=room)
        self.assertEqual(recording.duration_seconds, 12)
        self.assertTrue(recording.has_media())
