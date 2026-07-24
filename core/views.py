from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.utils import timezone
from .models import Cliente, OrdemServico, Notificacao


# ==================== FUNÇÕES AUXILIARES ====================

def criar_notificacao(usuario, tipo, titulo, mensagem, link=''):
    """Função auxiliar para criar notificações"""
    Notificacao.objects.create(
        usuario=usuario,
        tipo=tipo,
        titulo=titulo,
        mensagem=mensagem,
        link=link
    )


# ==================== AUTENTICAÇÃO ====================

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'Você saiu do sistema.')
    return redirect('login')


# ==================== DASHBOARD ====================

@login_required
def dashboard(request):
    total_clientes = Cliente.objects.filter(ativo=True).count()
    os_abertas = OrdemServico.objects.filter(status='aberta').count()
    os_andamento = OrdemServico.objects.filter(status='andamento').count()
    os_concluidas = OrdemServico.objects.filter(status='concluida').count()
    
    ultimas_os = OrdemServico.objects.select_related('cliente').order_by('-data_criacao')[:10]
    
    hoje = timezone.now()
    primeiro_dia = hoje.replace(day=1, hour=0, minute=0, second=0)
    faturamento_mes = OrdemServico.objects.filter(
        status='concluida',
        data_conclusao__gte=primeiro_dia
    ).aggregate(total=Sum('valor_total'))['total'] or 0
    
    context = {
        'total_clientes': total_clientes,
        'os_abertas': os_abertas,
        'os_andamento': os_andamento,
        'os_concluidas': os_concluidas,
        'ultimas_os': ultimas_os,
        'faturamento_mes': faturamento_mes,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


# ==================== CLIENTES ====================

@login_required
def cliente_lista(request):
    clientes = Cliente.objects.filter(ativo=True).order_by('nome')
    busca = request.GET.get('busca')
    
    if busca:
        clientes = clientes.filter(
            Q(nome__icontains=busca) | 
            Q(cpf_cnpj__icontains=busca) |
            Q(email__icontains=busca)
        )
    
    return render(request, 'clientes/lista.html', {'clientes': clientes, 'busca': busca})


@login_required
def cliente_criar(request):
    if request.method == 'POST':
        cliente = Cliente(
            nome=request.POST.get('nome'),
            cpf_cnpj=request.POST.get('cpf_cnpj'),
            email=request.POST.get('email'),
            telefone=request.POST.get('telefone'),
            celular=request.POST.get('celular', ''),
            endereco=request.POST.get('endereco'),
            cidade=request.POST.get('cidade'),
            estado=request.POST.get('estado'),
            cep=request.POST.get('cep'),
            observacoes=request.POST.get('observacoes', ''),
        )
        cliente.save()
        messages.success(request, f'Cliente {cliente.nome} cadastrado com sucesso!')
        return redirect('cliente_lista')
    
    return render(request, 'clientes/form.html', {'titulo': 'Novo Cliente'})


@login_required
def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        cliente.nome = request.POST.get('nome')
        cliente.cpf_cnpj = request.POST.get('cpf_cnpj')
        cliente.email = request.POST.get('email')
        cliente.telefone = request.POST.get('telefone')
        cliente.celular = request.POST.get('celular', '')
        cliente.endereco = request.POST.get('endereco')
        cliente.cidade = request.POST.get('cidade')
        cliente.estado = request.POST.get('estado')
        cliente.cep = request.POST.get('cep')
        cliente.observacoes = request.POST.get('observacoes', '')
        cliente.save()
        messages.success(request, f'Cliente {cliente.nome} atualizado com sucesso!')
        return redirect('cliente_lista')
    
    return render(request, 'clientes/form.html', {'cliente': cliente, 'titulo': 'Editar Cliente'})


@login_required
def cliente_detalhe(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    ordens = cliente.ordens.all().order_by('-data_abertura')
    return render(request, 'clientes/detalhe.html', {'cliente': cliente, 'ordens': ordens})


# ==================== ORDENS DE SERVIÇO ====================

@login_required
def ordem_lista(request):
    ordens = OrdemServico.objects.select_related('cliente').all()
    
    status = request.GET.get('status')
    busca = request.GET.get('busca')
    
    if status:
        ordens = ordens.filter(status=status)
    if busca:
        ordens = ordens.filter(
            Q(numero__icontains=busca) |
            Q(cliente__nome__icontains=busca) |
            Q(descricao_problema__icontains=busca)
        )
    
    return render(request, 'ordens/lista.html', {'ordens': ordens})


@login_required
def ordem_criar(request):
    if request.method == 'POST':
        # Trata valores vazios
        valor_servico_str = request.POST.get('valor_servico', '0')
        valor_pecas_str = request.POST.get('valor_pecas', '0')
        
        try:
            valor_servico = float(valor_servico_str)
        except (ValueError, TypeError):
            valor_servico = 0
        
        try:
            valor_pecas = float(valor_pecas_str)
        except (ValueError, TypeError):
            valor_pecas = 0
        
        ordem = OrdemServico(
            cliente_id=request.POST.get('cliente'),
            tecnico_id=request.POST.get('tecnico') or None,
            descricao_problema=request.POST.get('descricao_problema'),
            prioridade=request.POST.get('prioridade', 'media'),
            valor_servico=valor_servico,
            valor_pecas=valor_pecas,
            observacoes=request.POST.get('observacoes', ''),
            criado_por=request.user,
        )
        ordem.save()
        
        # 🔔 NOTIFICAÇÃO: Avisa administradores sobre nova OS
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            criar_notificacao(
                usuario=admin,
                tipo='nova_os',
                titulo=f'Nova OS: {ordem.numero}',
                mensagem=f'Ordem de serviço criada para {ordem.cliente.nome}',
                link=f'/ordens/{ordem.pk}/'
            )
        
        messages.success(request, f'OS {ordem.numero} criada com sucesso!')
        return redirect('ordem_detalhe', pk=ordem.pk)
    
    clientes = Cliente.objects.filter(ativo=True)
    tecnicos = User.objects.filter(is_staff=True)
    return render(request, 'ordens/form.html', {
        'titulo': 'Nova Ordem de Serviço',
        'clientes': clientes,
        'tecnicos': tecnicos,
    })


@login_required
def ordem_editar(request, pk):
    ordem = get_object_or_404(OrdemServico, pk=pk)
    
    if request.method == 'POST':
        # Trata valores vazios para não dar erro
        valor_servico_str = request.POST.get('valor_servico', '0')
        valor_pecas_str = request.POST.get('valor_pecas', '0')
        
        try:
            valor_servico = float(valor_servico_str)
        except (ValueError, TypeError):
            valor_servico = 0
        
        try:
            valor_pecas = float(valor_pecas_str)
        except (ValueError, TypeError):
            valor_pecas = 0
        
        ordem.cliente_id = request.POST.get('cliente')
        ordem.tecnico_id = request.POST.get('tecnico') or None
        ordem.descricao_problema = request.POST.get('descricao_problema')
        ordem.solucao = request.POST.get('solucao', '')
        ordem.status = request.POST.get('status')
        ordem.prioridade = request.POST.get('prioridade')
        ordem.valor_servico = valor_servico
        ordem.valor_pecas = valor_pecas
        ordem.observacoes = request.POST.get('observacoes', '')
        ordem.save()
        messages.success(request, f'OS {ordem.numero} atualizada!')
        return redirect('ordem_detalhe', pk=ordem.pk)
    
    clientes = Cliente.objects.filter(ativo=True)
    tecnicos = User.objects.filter(is_staff=True)
    return render(request, 'ordens/form.html', {
        'ordem': ordem,
        'titulo': f'Editar OS {ordem.numero}',
        'clientes': clientes,
        'tecnicos': tecnicos,
    })


@login_required
def ordem_detalhe(request, pk):
    ordem = get_object_or_404(OrdemServico, pk=pk)
    return render(request, 'ordens/detalhe.html', {'ordem': ordem})


@login_required
def ordem_excluir(request, pk):
    """Exclui uma ordem de serviço"""
    ordem = get_object_or_404(OrdemServico, pk=pk)
    
    if request.method == 'POST':
        numero = ordem.numero
        ordem.delete()
        messages.success(request, f'OS {numero} excluída com sucesso!')
        return redirect('ordem_lista')
    
    return render(request, 'ordens/excluir.html', {'ordem': ordem})


@login_required
def ordem_mudar_status(request, pk, novo_status):
    ordem = get_object_or_404(OrdemServico, pk=pk)
    status_antigo = ordem.get_status_display()
    
    if novo_status in ['aberta', 'andamento', 'concluida', 'cancelada']:
        ordem.status = novo_status
        ordem.save()
        
        # 🔔 NOTIFICAÇÃO: Avisa sobre mudança de status
        if ordem.tecnico:
            criar_notificacao(
                usuario=ordem.tecnico,
                tipo='status_os',
                titulo=f'Status Alterado: {ordem.numero}',
                mensagem=f'OS {ordem.numero} mudou de "{status_antigo}" para "{ordem.get_status_display()}"',
                link=f'/ordens/{ordem.pk}/'
            )
        
        messages.success(request, f'Status alterado para {ordem.get_status_display()}')
    
    return redirect('ordem_detalhe', pk=ordem.pk)


# ==================== PERFIL DO USUÁRIO ====================

@login_required
def perfil_view(request):
    """Visualiza e edita o perfil do usuário"""
    if request.method == 'POST':
        user = request.user
        
        # Atualiza dados básicos
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        
        # Atualiza senha (só se os campos foram preenchidos)
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if senha_atual and nova_senha:
            if user.check_password(senha_atual):
                if nova_senha == confirmar_senha:
                    user.set_password(nova_senha)
                    messages.success(request, 'Senha alterada com sucesso!')
                else:
                    messages.error(request, 'As senhas não coincidem!')
                    return render(request, 'perfil/perfil.html')
            else:
                messages.error(request, 'Senha atual incorreta!')
                return render(request, 'perfil/perfil.html')
        
        user.save()
        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('perfil')
    
    return render(request, 'perfil/perfil.html')


# ==================== NOTIFICAÇÕES ====================

@login_required
def notificacao_lista(request):
    """Lista todas as notificações do usuário"""
    # PRIMEIRO filtra, DEPOIS fatia
    notificacoes = request.user.notificacoes.all()
    nao_lidas = notificacoes.filter(lida=False).count()
    notificacoes = notificacoes[:50]
    
    return render(request, 'notificacoes/lista.html', {
        'notificacoes': notificacoes,
        'nao_lidas': nao_lidas,
    })


@login_required
def notificacao_marcar_lida(request, pk):
    """Marca uma notificação como lida"""
    notificacao = get_object_or_404(Notificacao, pk=pk, usuario=request.user)
    notificacao.lida = True
    notificacao.save()
    
    if notificacao.link:
        return redirect(notificacao.link)
    return redirect('notificacao_lista')


@login_required
def notificacao_marcar_todas(request):
    """Marca todas notificações como lidas"""
    request.user.notificacoes.filter(lida=False).update(lida=True)
    messages.success(request, 'Todas notificações marcadas como lidas!')
    return redirect('notificacao_lista')


# ==================== ÁREA DO CLIENTE ====================

def cliente_login(request):
    """Login específico para clientes"""
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        try:
            cliente = Cliente.objects.get(email=email, senha=senha, ativo=True)
            # Salva o cliente na sessão
            request.session['cliente_id'] = cliente.pk
            request.session['cliente_nome'] = cliente.nome
            messages.success(request, f'Bem-vindo, {cliente.nome}!')
            return redirect('cliente_area')
        except Cliente.DoesNotExist:
            messages.error(request, 'Email ou senha inválidos.')
    
    return render(request, 'clientes/login.html')


def cliente_logout(request):
    """Logout do cliente"""
    request.session.pop('cliente_id', None)
    request.session.pop('cliente_nome', None)
    messages.success(request, 'Você saiu da área do cliente.')
    return redirect('cliente_login')


def cliente_area(request):
    """Área do cliente - vê suas OS"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        messages.error(request, 'Faça login para acessar sua área.')
        return redirect('cliente_login')
    
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    ordens = cliente.ordens.all().order_by('-data_abertura')
    
    return render(request, 'clientes/area.html', {
        'cliente': cliente,
        'ordens': ordens,
    })


def cliente_os_detalhe(request, pk):
    """Cliente vê detalhes de uma OS específica"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        messages.error(request, 'Faça login para acessar.')
        return redirect('cliente_login')
    
    ordem = get_object_or_404(OrdemServico, pk=pk, cliente_id=cliente_id)
    
    return render(request, 'clientes/os_detalhe.html', {'ordem': ordem})


def cliente_criar_os(request):
    """Cliente cria sua própria OS"""
    cliente_id = request.session.get('cliente_id')
    
    if not cliente_id:
        messages.error(request, 'Faça login para acessar.')
        return redirect('cliente_login')
    
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    
    if request.method == 'POST':
        ordem = OrdemServico(
            cliente=cliente,
            descricao_problema=request.POST.get('descricao_problema'),
            prioridade=request.POST.get('prioridade', 'media'),
            observacoes=request.POST.get('observacoes', ''),
            criado_por=User.objects.first(),  # Admin como criador
        )
        ordem.save()
        
        # Notifica admins
        admins = User.objects.filter(is_staff=True)
        for admin in admins:
            criar_notificacao(
                usuario=admin,
                tipo='nova_os',
                titulo=f'Nova OS do Cliente: {ordem.numero}',
                mensagem=f'{cliente.nome} abriu uma nova OS: {ordem.descricao_problema[:100]}',
                link=f'/ordens/{ordem.pk}/'
            )
        
        messages.success(request, f'OS {ordem.numero} criada com sucesso!')
        return redirect('cliente_area')
    
    return render(request, 'clientes/criar_os.html', {'cliente': cliente})