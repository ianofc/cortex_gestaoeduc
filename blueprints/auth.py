# blueprints/auth.py

from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required 
from sqlalchemy import or_ # Importante para a lógica OU

# Tenta importar bcrypt
try:
    from app import bcrypt 
except ImportError:
    bcrypt = None 

# Imports Locais
from models import db, User, Horario, BlocoAula
from forms import RegisterForm, LoginForm, ProfessorForm

auth_bp = Blueprint('auth', __name__, url_prefix='/')

# --- ROTAS DE AUTENTICAÇÃO ---

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.index')) 
    
    form = RegisterForm()
    if form.validate_on_submit():
        bcrypt_instance = bcrypt if bcrypt else current_app.extensions['bcrypt']
        hashed_password = bcrypt_instance.generate_password_hash(form.password.data).decode('utf-8')
        
        user = User(
            username=form.username.data, 
            email_contato=form.email.data, 
            password_hash=hashed_password
        )
        db.session.add(user)
        
        # Cria horário padrão
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
        flash('Sua conta foi criada! Você já pode fazer o login.', 'success')
        return redirect(url_for('auth.login'))
    
    # CORREÇÃO: Caminho atualizado para 'main/register.html'
    return render_template('main/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('core.index')) 
        
    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.login.data # Pega o dado digitado (email ou user)
        
        # LÓGICA HÍBRIDA: Busca por email_contato OU username
        user = User.query.filter(
            or_(
                User.email_contato == login_input,
                User.username == login_input
            )
        ).first()
        
        bcrypt_instance = bcrypt if bcrypt else current_app.extensions['bcrypt']
        
        if user and bcrypt_instance.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            
            flash(f'Bem-vindo de volta, {user.username}!', 'success')
            
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('core.index'))
        else:
            flash('Login falhou. Verifique suas credenciais.', 'danger')
            
    # CORREÇÃO: Caminho atualizado para 'main/login.html'
    return render_template('main/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/professor/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_professor(id):
    professor = User.query.get_or_404(id)
    form = ProfessorForm(obj=professor)
    
    form.senha.validators = [] 

    if form.validate_on_submit():
        professor.username = form.nome.data
        professor.email_contato = form.email.data
        
        if form.senha.data:
            bcrypt_instance = bcrypt if bcrypt else current_app.extensions['bcrypt']
            hashed_password = bcrypt_instance.generate_password_hash(form.senha.data).decode('utf-8')
            professor.password_hash = hashed_password
            
        db.session.commit()
        flash('Professor atualizado com sucesso!', 'success')
        return redirect(url_for('core.index'))
        
    return render_template('edit/edit_professor.html', form=form, professor=professor)