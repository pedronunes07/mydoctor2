from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Todo, Consulta, ChatRoom, ChatMessage, ChatSignal, Recording, Medico, Receita
from .utils import (
    user_has_medico,
    user_can_access_patient_area,
    user_can_access_consulta,
    user_can_access_room,
    get_or_create_room_for_consulta,
    user_can_access_recording,
)
from django.contrib.auth.decorators import login_required
from django.urls import reverse, reverse_lazy
from django.db.models import Q
import os

from django.core.files.base import ContentFile
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, Http404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.utils.crypto import get_random_string
import json
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from django.shortcuts import render
from django.views.generic import CreateView, ListView
from django.urls import reverse, reverse_lazy

def voltar_para_index(request):
    return redirect('home')

class TodoListView(ListView):
    model = Todo
    template_name = 'todos/todo_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voltar_url'] = reverse('home')
        return context

class TodoCreateView(CreateView):
    model = Todo
    fields = ["title", "deadline"]
    success_url = reverse_lazy("todo_list")
    template_name = 'todos/todo_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['voltar_url'] = reverse('home')
        return context

class HomeView(TemplateView):
    template_name = 'todos/index.html'

def health_view(request):
    return JsonResponse({'status': 'ok'})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard_view(request):
    context = {'voltar_url': reverse('home')}
    if user_can_access_patient_area(request.user):
        context['consultas_recentes'] = Consulta.objects.filter(
            usuario=request.user,
        ).select_related('medico', 'medico__user').order_by('-data', '-hora')[:5]
    return render(request, 'todos/dashboard.html', context)

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        crm = request.POST.get('crm')
        password = request.POST.get('password')
        user = None
        if crm:
            try:
                med = Medico.objects.select_related('user').get(crm=crm)
                user = authenticate(request, username=med.user.username, password=password)
            except Medico.DoesNotExist:
                user = None
        elif email:
            try:
                u = User.objects.get(email=email)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                user = None
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('dashboard')
            if user_has_medico(user):
                return redirect('doctor_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, 'Email/CRM ou senha incorretos!')
    else:
        # Limpa mensagens pendentes (ex.: avisos de outras páginas)
        list(messages.get_messages(request))
    context = {'voltar_url': reverse('home')}
    return render(request, 'todos/login.html', context)

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        full_name = request.POST.get('full_name', '')
        phone = request.POST.get('phone', '')
        birthdate = request.POST.get('birthdate', '')
        is_medico = request.POST.get('is_medico') == 'on'
        crm = request.POST.get('crm', '').strip()
        especialidade = request.POST.get('especialidade', '').strip()
        if password != password2:
            messages.error(request, 'As senhas não coincidem!')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Nome de usuário já existe!')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'E-mail já cadastrado!')
        elif is_medico and not crm:
            messages.error(request, 'CRM é obrigatório para cadastro de médico!')
        elif is_medico and Medico.objects.filter(crm=crm).exists():
            messages.error(request, 'CRM já cadastrado!')
        elif is_medico and not especialidade:
            messages.error(request, 'Selecione a especialidade do médico!')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = full_name
            user.last_name = f"{phone} / {birthdate}"
            user.save()
            if is_medico:
                Medico.objects.create(user=user, crm=crm, especialidade=especialidade)
            messages.success(request, 'Cadastro realizado com sucesso! Faça login.')
            return redirect('login')
    context = {'voltar_url': reverse('home')}
    return render(request, 'todos/register.html', context)

@login_required
def ver_consultas_view(request):
    consultas = Consulta.objects.filter(usuario=request.user).select_related('medico', 'medico__user').order_by('-data', '-hora')
    context = {
        'consultas': consultas,
        'voltar_url': reverse('home')
    }
    return render(request, 'todos/ver_consultas.html', context)

@login_required
def agendar_consulta_view(request):
    if request.method == 'POST':
        especialidade = (request.POST['especialidade'] or '').strip()
        data = request.POST['data']
        hora = request.POST['hora']
        observacoes = request.POST.get('obs', '')
        consulta = Consulta.objects.create(
            usuario=request.user,
            especialidade=especialidade,
            data=data,
            hora=hora,
            observacoes=observacoes
        )
        # Tenta atribuir automaticamente a um médico da mesma especialidade
        try:
            medico_match = Medico.objects.filter(especialidade__iexact=especialidade.strip()).first()
            if medico_match:
                consulta.medico = medico_match
                consulta.save(update_fields=['medico'])
        except Exception:
            pass
        messages.success(request, 'Consulta agendada! Aguarde o médico assumir ou entre na ligação em Ver Consultas.')
        return redirect('ver_consultas')
    context = {'voltar_url': reverse('home')}
    return render(request, 'todos/agendar_consulta.html', context)


@login_required
def entrar_consulta_view(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)
    if not user_can_access_consulta(request.user, consulta):
        messages.error(request, 'Você não tem permissão para esta consulta.')
        return redirect('dashboard')
    room, created = get_or_create_room_for_consulta(consulta, request.user)
    if created:
        messages.info(request, 'Sala de atendimento criada. Aguarde o outro participante e inicie a ligação.')
    return redirect('chat_room', code=room.code)


# CHAT: criação e acesso à sala
@login_required
def create_chat_room_view(request):
    # POST: apenas médicos podem criar sala
    if request.method == 'POST':
        if not user_has_medico(request.user):
            return redirect('dashboard')
        consulta_id = request.POST.get('consulta_id')
        consulta = None
        if consulta_id:
            consulta = get_object_or_404(Consulta, id=consulta_id)
            if consulta.medico_id != request.user.medico.id:
                messages.error(request, 'Esta consulta não está atribuída a você.')
                return redirect('doctor_dashboard')
        if consulta:
            room, _ = get_or_create_room_for_consulta(consulta, request.user)
        else:
            room = ChatRoom.objects.create(
                code=get_random_string(10),
                created_by=request.user,
            )
        return redirect('chat_room', code=room.code)
    if user_has_medico(request.user):
        consultas = Consulta.objects.filter(medico=request.user.medico).order_by('-data', '-hora')
        voltar = reverse('doctor_dashboard')
        consultas_paciente = []
        salas_paciente = []
    else:
        consultas = []
        voltar = reverse('dashboard')
        consultas_paciente = Consulta.objects.filter(usuario=request.user).select_related('medico', 'medico__user').order_by('-data', '-hora')
        salas_paciente = ChatRoom.objects.filter(
            consulta__usuario=request.user,
            closed_at__isnull=True,
        ).select_related('consulta').order_by('-created_at')
    context = {
        'voltar_url': voltar,
        'consultas_do_medico': consultas,
        'consultas_paciente': consultas_paciente,
        'chat_rooms_do_paciente': salas_paciente,
    }
    return render(request, 'todos/chat.html', context)


# Dashboard do médico
@login_required
def doctor_dashboard_view(request):
    if not user_has_medico(request.user):
        return redirect('dashboard')
    medico = request.user.medico
    consultas = Consulta.objects.filter(medico=medico).order_by('data', 'hora')
    pendentes = Consulta.objects.filter(medico__isnull=True)
    if medico.especialidade:
        pendentes = pendentes.filter(especialidade__iexact=medico.especialidade.strip())
    pendentes = pendentes.order_by('data', 'hora')
    context = {
        'consultas': consultas,
        'pendentes': pendentes,
        'voltar_url': reverse('home')
    }
    return render(request, 'todos/doctor_dashboard.html', context)


@login_required
def doctor_accept_consulta_view(request, consulta_id):
    if not user_has_medico(request.user):
        return redirect('dashboard')
    consulta = get_object_or_404(Consulta, id=consulta_id)
    consulta.medico = request.user.medico
    consulta.save(update_fields=['medico'])
    get_or_create_room_for_consulta(consulta, request.user)
    messages.success(request, 'Consulta assumida. Sala de ligação pronta — clique em Entrar na ligação.')
    return redirect('doctor_dashboard')


@login_required
def create_receita_view(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)
    if not user_has_medico(request.user) or consulta.medico != request.user.medico:
        messages.error(request, 'Apenas o médico responsável pode emitir receita/atestado desta consulta.')
        return redirect('doctor_dashboard')
    if request.method == 'POST':
        tipo = request.POST.get('tipo', 'receita')
        destinatario = request.POST.get('destinatario', '').strip()
        conteudo = request.POST.get('conteudo', '').strip()
        if not conteudo:
            messages.error(request, 'Conteúdo é obrigatório.')
        else:
            Receita.objects.create(
                consulta=consulta,
                paciente=consulta.usuario,
                medico=request.user.medico,
                tipo=tipo,
                destinatario=destinatario,
                conteudo=conteudo
            )
            messages.success(request, 'Documento emitido com sucesso.')
            return redirect('doctor_dashboard')
    context = {'consulta': consulta, 'voltar_url': reverse('doctor_dashboard')}
    return render(request, 'todos/receita_form.html', context)


@login_required
def minhas_receitas_view(request):
    receitas = Receita.objects.filter(paciente=request.user).select_related('consulta', 'medico', 'medico__user')
    context = {
        'receitas': receitas,
        'voltar_url': reverse('dashboard')
    }
    return render(request, 'todos/receitas_paciente.html', context)


@login_required
def chat_room_view(request, code):
    room = get_object_or_404(ChatRoom, code=code)
    if not user_can_access_room(request.user, room):
        messages.error(request, 'Você não tem acesso a esta sala.')
        return redirect('dashboard')
    voltar = reverse('doctor_dashboard') if user_has_medico(request.user) else reverse('dashboard')
    context = {
        'room_code': room.code,
        'voltar_url': voltar,
        'invite_url': request.build_absolute_uri()
    }
    return render(request, 'todos/chat.html', context)


# CHAT: mensagens de texto
@login_required
@require_http_methods(["GET", "POST"])
def chat_messages_api(request, code):
    room = get_object_or_404(ChatRoom, code=code)
    if not user_can_access_room(request.user, room):
        return HttpResponseBadRequest('sem permissão')
    if request.method == 'GET':
        last_id = request.GET.get('last_id')
        qs = room.messages.all()
        if last_id:
            try:
                last_id_int = int(last_id)
                qs = qs.filter(id__gt=last_id_int)
            except ValueError:
                return HttpResponseBadRequest('last_id inválido')
        data = [
            {
                'id': m.id,
                'sender': m.sender.username,
                'text': m.text,
                'created_at': m.created_at.isoformat()
            }
            for m in qs
        ]
        return JsonResponse({'messages': data})
    # POST cria mensagem
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('JSON inválido')
    text = body.get('text', '').strip()
    if not text:
        return HttpResponseBadRequest('Texto obrigatório')
    msg = ChatMessage.objects.create(room=room, sender=request.user, text=text)
    return JsonResponse({'ok': True, 'id': msg.id})


# CHAT: sinalização WebRTC (polling simples)
@login_required
@require_http_methods(["GET", "POST"])
def chat_signals_api(request, code):
    room = get_object_or_404(ChatRoom, code=code)
    if not user_can_access_room(request.user, room):
        return HttpResponseBadRequest('sem permissão')
    if request.method == 'GET':
        last_id = request.GET.get('last_id')
        qs = room.signals.exclude(sender=request.user)
        if last_id:
            try:
                last_id_int = int(last_id)
                qs = qs.filter(id__gt=last_id_int)
            except ValueError:
                return HttpResponseBadRequest('last_id inválido')
        data = [
            {
                'id': s.id,
                'type': s.signal_type,
                'content': json.loads(s.content),
                'created_at': s.created_at.isoformat()
            }
            for s in qs
        ]
        return JsonResponse({'signals': data})
    # POST cria sinal
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('JSON inválido')
    signal_type = body.get('type')
    content = body.get('content')
    if signal_type not in ['offer', 'answer', 'candidate', 'decline', 'end']:
        return HttpResponseBadRequest('type inválido')
    ChatSignal.objects.create(
        room=room,
        sender=request.user,
        signal_type=signal_type,
        content=json.dumps(content)
    )
    return JsonResponse({'ok': True})


# UPLOAD de gravação
@login_required
@require_http_methods(["POST"])
def upload_recording_api(request, code):
    room = get_object_or_404(ChatRoom, code=code)
    if not user_can_access_room(request.user, room):
        return JsonResponse({'ok': False, 'error': 'sem permissão'}, status=403)
    f = request.FILES.get('file')
    try:
        duration = int(request.POST.get('duration', '0') or 0)
    except ValueError:
        duration = 0
    if not f:
        return JsonResponse({'ok': False, 'error': 'Arquivo ausente'}, status=400)
    if f.size > 45 * 1024 * 1024:
        return JsonResponse({'ok': False, 'error': 'Arquivo muito grande (máx. 45 MB)'}, status=400)

    mime = f.content_type or 'video/webm'
    raw = f.read()
    if not raw:
        return JsonResponse({'ok': False, 'error': 'Arquivo vazio'}, status=400)

    rec = Recording(
        room=room,
        uploaded_by=request.user,
        duration_seconds=duration,
        mime_type=mime,
    )
    on_vercel = bool(os.environ.get('VERCEL') or os.environ.get('VERCEL_ENV'))
    if on_vercel:
        rec.file_blob = raw
        rec.save()
    else:
        rec.save()
        rec.file.save(f.name or f'gravacao_{rec.pk}.webm', ContentFile(raw), save=True)

    return JsonResponse({
        'ok': True,
        'id': rec.id,
        'playback_url': reverse('recording_playback', args=[rec.id]),
        'list_url': reverse('recorded_list'),
    })


@login_required
def recording_playback_view(request, rec_id):
    rec = get_object_or_404(Recording, id=rec_id)
    if not user_can_access_recording(request.user, rec):
        raise Http404()
    if rec.file_blob:
        return HttpResponse(rec.file_blob, content_type=rec.mime_type or 'video/webm')
    if rec.file:
        try:
            with rec.file.open('rb') as fh:
                return HttpResponse(fh.read(), content_type=rec.mime_type or 'video/webm')
        except FileNotFoundError:
            raise Http404()
    raise Http404()


# Lista de gravações
@login_required
def recorded_list_view(request):
    recs = Recording.objects.filter(
        Q(uploaded_by=request.user) | Q(room__consulta__usuario=request.user)
    ).select_related('room', 'uploaded_by').distinct().order_by('-created_at')
    context = { 'recordings': recs, 'voltar_url': reverse('dashboard') }
    return render(request, 'todos/recorded_list.html', context)


# Gravações do médico
@login_required
def doctor_recordings_view(request):
    if not user_has_medico(request.user):
        return redirect('dashboard')
    recs = Recording.objects.select_related('room', 'room__consulta', 'uploaded_by')
    recs = recs.filter(room__consulta__medico=request.user.medico) | recs.filter(room__created_by=request.user)
    recs = recs.order_by('-created_at')
    context = { 'recordings': recs, 'voltar_url': reverse('doctor_dashboard') }
    return render(request, 'todos/recorded_list.html', context)


@login_required
@require_http_methods(["POST"])
def delete_recording_view(request, rec_id):
    rec = get_object_or_404(Recording, id=rec_id)
    if request.user == rec.uploaded_by or request.user.is_superuser:
        if rec.file:
            rec.file.delete(save=False)
        rec.delete()
        messages.success(request, 'Gravação excluída com sucesso.')
    else:
        messages.error(request, 'Você não tem permissão para excluir esta gravação.')
    return redirect('recorded_list')

@login_required
@require_http_methods(["POST"])
def close_chat_room_api(request, code):
    room = get_object_or_404(ChatRoom, code=code)
    # Apenas o criador da sala (médico) pode encerrar
    if room.created_by != request.user:
        return HttpResponseBadRequest('sem permissão')
    if room.closed_at is None:
        room.closed_at = timezone.now()
        room.save(update_fields=['closed_at'])
    return JsonResponse({'ok': True, 'closed_at': room.closed_at.isoformat()})