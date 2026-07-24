from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Cliente, OrdemServico
from django.utils import timezone

class Command(BaseCommand):
    help = 'Cria dados de teste para o sistema'

    def handle(self, *args, **kwargs):
        self.stdout.write('Criando dados de teste...')
        
        # Criar técnicos
        if not User.objects.filter(username='tecnico1').exists():
            tecnico1 = User.objects.create_user(
                username='tecnico1',
                password='123456',
                first_name='João',
                last_name='Silva',
                is_staff=True
            )
            self.stdout.write(f'Técnico {tecnico1.username} criado!')
        
        # Criar clientes
        clientes_data = [
            {'nome': 'Maria Santos', 'cpf_cnpj': '123.456.789-00', 'email': 'maria@email.com', 
             'telefone': '(11) 2345-6789', 'endereco': 'Rua A, 123', 'cidade': 'São Paulo', 'estado': 'SP', 'cep': '01234-567'},
            {'nome': 'João Pereira', 'cpf_cnpj': '987.654.321-00', 'email': 'joao@email.com', 
             'telefone': '(21) 3456-7890', 'endereco': 'Av B, 456', 'cidade': 'Rio de Janeiro', 'estado': 'RJ', 'cep': '20000-000'},
            {'nome': 'Empresa ABC Ltda', 'cpf_cnpj': '12.345.678/0001-90', 'email': 'abc@email.com', 
             'telefone': '(31) 4567-8901', 'endereco': 'Rua C, 789', 'cidade': 'Belo Horizonte', 'estado': 'MG', 'cep': '30000-000'},
        ]
        
        for data in clientes_data:
            if not Cliente.objects.filter(cpf_cnpj=data['cpf_cnpj']).exists():
                Cliente.objects.create(**data)
                self.stdout.write(f'Cliente {data["nome"]} criado!')
        
        self.stdout.write(self.style.SUCCESS('Dados de teste criados com sucesso!'))