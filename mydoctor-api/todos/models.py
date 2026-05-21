from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Todo(models.Model):
	title = models.CharField(max_length=100, null=False, blank=False)
	created_at =models.DateField(auto_now_add=True,null=False,blank=False)
	deadline = models.DateField(null=False, blank=False)
	finished_at = models.DateField(null=True)

class Consulta(models.Model):
	usuario = models.ForeignKey(User, on_delete=models.CASCADE)
	especialidade = models.CharField(max_length=50)
	data = models.DateField()
	hora = models.TimeField()
	observacoes = models.TextField(blank=True)
	criada_em = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.especialidade} em {self.data} às {self.hora} ({self.usuario.username})"

	def label_especialidade(self):
		return dict(Medico.ESPECIALIDADES).get(self.especialidade, self.especialidade)

	def sala_chat_aberta(self):
		return self.salas.filter(closed_at__isnull=True).first()

	def status_agendamento(self):
		if self.sala_chat_aberta():
			return 'sala_aberta'
		if self.medico_id:
			return 'confirmada'
		return 'aguardando'


class ChatRoom(models.Model):
	"""Sala de chat entre paciente e médico."""
	code = models.CharField(max_length=64, unique=True)
	created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_created')
	created_at = models.DateTimeField(auto_now_add=True)
	# Opcionalmente vinculada a uma consulta específica
	consulta = models.ForeignKey('Consulta', on_delete=models.SET_NULL, null=True, blank=True, related_name='salas')
	# Quando preenchido, significa que a sala foi encerrada
	closed_at = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"Sala {self.code}"


class ChatMessage(models.Model):
	"""Mensagens de texto dentro da sala."""
	room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
	sender = models.ForeignKey(User, on_delete=models.CASCADE)
	text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['created_at']

	def __str__(self):
		return f"{self.sender.username}: {self.text[:30]}"


class ChatSignal(models.Model):
	"""Armazena sinalização WebRTC (offer/answer/candidate) com polling simples."""
	room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='signals')
	sender = models.ForeignKey(User, on_delete=models.CASCADE)
	signal_type = models.CharField(max_length=16)  # offer, answer, candidate
	content = models.TextField()  # JSON serializado
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['created_at']


class Recording(models.Model):
	"""Gravação de uma consulta (áudio/vídeo) vinculada a uma sala."""
	room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='recordings')
	uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
	file = models.FileField(upload_to='recordings/')
	duration_seconds = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"Gravação {self.id} - sala {self.room.code}"


class Medico(models.Model):
	"""Perfil de médico vinculado ao usuário."""
	ESPECIALIDADES = (
		('clinico', 'Clínico Geral'),
		('pediatria', 'Pediatria'),
		('ginecologia', 'Ginecologia'),
		('cardiologia', 'Cardiologia'),
		('dermatologia', 'Dermatologia'),
		('ortopedia', 'Ortopedia'),
		('otorrino', 'Otorrinolaringologia'),
		('oftalmo', 'Oftalmologia'),
		('neuro', 'Neurologia'),
		('psiquiatria', 'Psiquiatria'),
	)
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medico')
	crm = models.CharField(max_length=32, unique=True, blank=False)
	especialidade = models.CharField(max_length=64, blank=True, choices=ESPECIALIDADES)

	def __str__(self):
		nome = self.user.get_full_name() or self.user.username
		return f"Dr(a). {nome} ({self.especialidade})"


# Liga consulta a um médico (opcional para permitir fila/triagem)
Consulta.add_to_class('medico', models.ForeignKey(Medico, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultas'))


class Receita(models.Model):
	TIPO_CHOICES = (
		('receita', 'Receita'),
		('atestado', 'Atestado'),
	)
	consulta = models.ForeignKey(Consulta, on_delete=models.CASCADE, related_name='receitas')
	paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receitas')
	medico = models.ForeignKey(Medico, on_delete=models.CASCADE, related_name='receitas_emitidas')
	tipo = models.CharField(max_length=16, choices=TIPO_CHOICES, default='receita')
	destinatario = models.CharField(max_length=255, blank=True)
	conteudo = models.TextField()
	criado_em = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-criado_em']

	def __str__(self):
		return f"{self.get_tipo_display()} - {self.consulta.especialidade} - {self.criado_em.date()}"