from django.contrib import admin
from .models import Cliente, OrdemServico, Notificacao

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cpf_cnpj', 'email', 'telefone', 'cidade', 'ativo', 'data_cadastro']
    search_fields = ['nome', 'cpf_cnpj', 'email', 'telefone']
    list_filter = ['ativo', 'cidade', 'estado', 'data_cadastro']
    list_per_page = 20

@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'tecnico', 'status', 'prioridade', 'valor_total', 'data_abertura']
    search_fields = ['numero', 'cliente__nome', 'descricao_problema']
    list_filter = ['status', 'prioridade', 'data_abertura']
    date_hierarchy = 'data_abertura'
    list_per_page = 20
    readonly_fields = ['numero', 'valor_total', 'data_criacao', 'data_atualizacao']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero', 'cliente', 'tecnico', 'status', 'prioridade')
        }),
        ('Descrições', {
            'fields': ('descricao_problema', 'solucao', 'observacoes')
        }),
        ('Valores', {
            'fields': ('valor_servico', 'valor_pecas', 'valor_total')
        }),
        ('Datas', {
            'fields': ('data_abertura', 'data_conclusao', 'data_criacao', 'data_atualizacao')
        }),
    )

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'tipo', 'lida', 'data_criacao']
    list_filter = ['tipo', 'lida', 'data_criacao']
    search_fields = ['titulo', 'mensagem', 'usuario__username']