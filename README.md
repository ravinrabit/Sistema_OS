# Sistema OS

Sistema web para abertura, acompanhamento e gestão de Ordens de Serviço (OS), desenvolvido em Django.

## Funcionalidades

- Cadastro de clientes (dados pessoais, contato e endereço)
- Abertura de Ordens de Serviço com numeração automática sequencial por ano
- Controle de status (Aberta, Em Andamento, Concluída, Cancelada) e prioridade (Baixa, Média, Alta, Urgente)
- Atribuição de técnico responsável por OS
- Cálculo automático do valor total (serviço + peças)
- Notificações internas por usuário

## Stack

- Python / Django 4.2
- SQLite

## Como rodar

```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

O site sobe em `http://localhost:8000`, com o painel administrativo em `/admin/`.
