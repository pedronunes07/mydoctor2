import re

from django import forms
from django.contrib.auth.models import User

from .models import Consulta, Medico, Receita


def only_digits(value):
    return re.sub(r'\D', '', value or '')


class LoginForm(forms.Form):
    email = forms.EmailField(required=False)
    crm = forms.CharField(required=False, max_length=12)
    password = forms.CharField()

    def clean_crm(self):
        return only_digits(self.cleaned_data.get('crm'))

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('email') and not cleaned.get('crm'):
            raise forms.ValidationError('Informe e-mail ou CRM.')
        return cleaned


class RegisterForm(forms.Form):
    full_name = forms.CharField(max_length=150)
    phone = forms.CharField(max_length=15)
    username = forms.CharField(max_length=150)
    birthdate = forms.DateField()
    email = forms.EmailField()
    is_medico = forms.BooleanField(required=False)
    crm = forms.CharField(required=False, max_length=12)
    especialidade = forms.ChoiceField(required=False, choices=(('', 'Especialidade'),) + Medico.ESPECIALIDADES)
    password = forms.CharField()
    password2 = forms.CharField()

    def clean_phone(self):
        phone = only_digits(self.cleaned_data.get('phone'))
        if not phone:
            raise forms.ValidationError('Telefone deve conter apenas números!')
        return phone

    def clean_crm(self):
        return only_digits(self.cleaned_data.get('crm'))

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Nome de usuário já existe!')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('E-mail já cadastrado!')
        return email

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError('As senhas não coincidem!')
        if cleaned.get('is_medico'):
            crm = cleaned.get('crm')
            if not crm:
                raise forms.ValidationError('CRM é obrigatório para cadastro de médico!')
            if Medico.objects.filter(crm=crm).exists():
                raise forms.ValidationError('CRM já cadastrado!')
            if not cleaned.get('especialidade'):
                raise forms.ValidationError('Selecione a especialidade do médico!')
        return cleaned


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['especialidade', 'data', 'hora', 'observacoes']


class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['tipo', 'destinatario', 'conteudo']
