import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

# --- IMPORTAÇÃO DA EXTENSÃO (CORREÇÃO) ---
from app.extensions import bcrypt  # Importa o bcrypt diretamente do arquivo novo

# Imports Locais
from app.models.base_legacy import db, User, Horario, BlocoAula, Aluno, Escola
from app.forms.forms_legacy import RegisterForm, LoginForm, ProfessorForm

# Definindo prefixo /auth para organizar as rotas (ex: /auth/login)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- ROTAS DE AUTENTICAÇÃO ---

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.index')) 
    
    form = RegisterForm()
    
    # Popula as escolas dinamicamente no SelectField do formulário
    escolas = Escola.query.all()
    form.escola.choices = [(e.id, e.nome) for e in escolas]
    if not escolas:
        form.escola.choices = [(0, 'Nenhuma escola cadastrada')]

    if form.validate_on_submit():
        # Acesso seguro ao Bcrypt (CORRIGIDO: usa o objeto importado diretamente)
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Determina o papel do usuário
        tipo = form.tipo_conta.data # 'professor' ou 'aluno'
        escola_id = form.escola.data if form.escola.data != 0 else None
        
        user = User(
            username=form.username.data, 
            email_contato=form.email.data, 
            password_hash=hashed_password,
            # Define as flags com base na escolha
            is_professor=(tipo == 'professor'),
            is_student=(tipo == 'aluno'),
            escola_id=escola_id
        )
        db.session.add(user)
        db.session.commit() # Commit para gerar o ID do User
        
        # --- LÓGICA ESPECÍFICA POR TIPO ---
        
        if user.is_student:
            # Se for ALUNO: Cria a ficha acadêmica automaticamente
            novo_aluno = Aluno(
                nome=user.username,
                matricula=f"AUTO-{user.id}", # Matrícula provisória
                id_user_conta=user.id,       # Vínculo com o login
                id_turma=None                # Sem turma inicialmente
            )
            db.session.add(novo_aluno)
            db.session.commit()
            flash('Conta de aluno criada! Aguarde a enturmação pela secretaria.', 'success')
            
        elif user.is_professor:
            # Se for PROFESSOR: Cria o horário padrão (Lógica original mantida)
            novo_horario = Horario(nome=f"Horário de {user.username}", autor=user)
            db.session.add(novo_horario)
            
            horarios_texto_padrao = ["13:10", "14:00", "14:50", "16:00", "16:50"]
            for dia in range(5): 
                for pos in range(1, 6):
                    bloco = BlocoAula(
                        horario=novo_horario, 
                        dia_semana=dia, 
                        posicao_aula=pos,
                        texto_horario=horarios_texto_padrao[pos-1]
                    )
                    db.session.add(bloco)
            
            db.session.commit()
            flash('Conta de professor criada! Você já pode fazer o login.', 'success')
            
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Se já estiver logado, redireciona baseado no tipo
        if getattr(current_user, 'is_student', False):
            return redirect(url_for('portal.dashboard'))
        return redirect(url_for('core.index')) 
        
    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.login.data # Pode ser email ou username
        
        # Busca por email OU username
        user = User.query.filter(
            or_(
                User.email_contato == login_input,
                User.username == login_input
            )
        ).first()
        
        # Acesso seguro ao Bcrypt (CORRIGIDO: usa o objeto importado diretamente)
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            
            # Redirecionamento Inteligente pós-login
            if getattr(user, 'is_student', False):
                return redirect(url_for('portal.dashboard'))
            
            flash(f'Bem-vindo de volta, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('core.index'))
        else:
            flash('Login falhou. Verifique suas credenciais.', 'danger')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/professor/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_professor(id):
    # Rota administrativa para editar professores
    # Apenas admin ou o próprio professor
    if not current_user.is_admin and current_user.id != id:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('core.index'))

    professor = User.query.get_or_404(id)
    form = ProfessorForm(obj=professor)
    
    form.senha.validators = [] # Senha opcional na edição

    if form.validate_on_submit():
        professor.username = form.nome.data
        professor.email_contato = form.email.data
        
        if form.senha.data:
            # Acesso seguro ao Bcrypt (CORRIGIDO: usa o objeto importado diretamente)
            hashed_password = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
            professor.password_hash = hashed_password
            
        db.session.commit()
        flash('Professor atualizado com sucesso!', 'success')
        # Redireciona para lista se for admin, ou home se for o próprio
        if current_user.is_admin:
            return redirect(url_for('core.listar_professores'))
        return redirect(url_for('core.index'))
        
    return render_template('admin/usuarios/editar_professor.html', form=form, professor=professor)