from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Cliente(models.Model):
    nome = models.CharField('Nome', max_length=200)
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=18, unique=True)
    email = models.EmailField('E-mail', max_length=100)
    telefone = models.CharField('Telefone', max_length=20)
    celular = models.CharField('Celular', max_length=20, blank=True)
    endereco = models.CharField('Endereço', max_length=200)
    cidade = models.CharField('Cidade', max_length=100)
    estado = models.CharField('Estado', max_length=2)
    cep = models.CharField('CEP', max_length=9)
    observacoes = models.TextField('Observações', blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    senha = models.CharField('Senha', max_length=128, default='123456')  # ← NOVO CAMPO
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    
    class Meta:
        ordering = ['nome']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        return f"{self.nome} - {self.cpf_cnpj}"


class Notificacao(models.Model):
    """Notificações do sistema"""
    
    TIPO_CHOICES = [
        ('nova_os', 'Nova OS'),
        ('status_os', 'Status Alterado'),
        ('os_atribuida', 'OS Atribuída'),
        ('info', 'Informação'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    tipo = models.CharField('Tipo', max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField('Título', max_length=200)
    mensagem = models.TextField('Mensagem')
    link = models.CharField('Link', max_length=200, blank=True)
    lida = models.BooleanField('Lida', default=False)
    data_criacao = models.DateTimeField('Data', auto_now_add=True)
    
    class Meta:
        ordering = ['-data_criacao']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"


class OrdemServico(models.Model):
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('andamento', 'Em Andamento'),
        ('concluida', 'Concluída'),
        ('cancelada', 'Cancelada'),
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    numero = models.CharField('Número OS', max_length=20, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, verbose_name='Cliente', related_name='ordens')
    tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Técnico', related_name='ordens_tecnico')
    
    descricao_problema = models.TextField('Descrição do Problema')
    solucao = models.TextField('Solução', blank=True)
    
    status = models.CharField('Status', max_length=15, choices=STATUS_CHOICES, default='aberta')
    prioridade = models.CharField('Prioridade', max_length=10, choices=PRIORIDADE_CHOICES, default='media')
    data_abertura = models.DateTimeField('Data de Abertura', default=timezone.now)
    data_conclusao = models.DateTimeField('Data de Conclusão', null=True, blank=True)
    
    valor_servico = models.DecimalField('Valor do Serviço', max_digits=10, decimal_places=2, default=0)
    valor_pecas = models.DecimalField('Valor das Peças', max_digits=10, decimal_places=2, default=0)
    valor_total = models.DecimalField('Valor Total', max_digits=10, decimal_places=2, default=0)
    
    criado_por = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Criado por', related_name='ordens_criadas')
    observacoes = models.TextField('Observações Internas', blank=True)
    data_criacao = models.DateTimeField('Data de Criação', auto_now_add=True)
    data_atualizacao = models.DateTimeField('Data de Atualização', auto_now=True)
    
    class Meta:
        ordering = ['-data_abertura']
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'
    
    def __str__(self):
        return f"OS {self.numero} - {self.cliente.nome}"
    
    def save(self, *args, **kwargs):
        if not self.numero:
            ano = timezone.now().year
            ultima_os = OrdemServico.objects.filter(numero__contains=str(ano)).order_by('numero').last()
            if ultima_os:
                try:
                    numero = int(ultima_os.numero.split('/')[0]) + 1
                except:
                    numero = 1
            else:
                numero = 1
            self.numero = f"{numero:06d}/{ano}"
        
        self.valor_total = self.valor_servico + self.valor_pecas
        
        if self.status == 'concluida' and not self.data_conclusao:
            self.data_conclusao = timezone.now()
        
        super().save(*args, **kwargs)