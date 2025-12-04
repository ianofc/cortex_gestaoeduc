import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

from app.extensions import bcrypt, db
from app.models.users import User, Role, Escola
from app.models.academic import Aluno, Horario, BlocoAula
from app.forms.forms_legacy import RegisterForm, LoginForm

from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('core.index')) 
    
    form = RegisterForm()
    
    try:
        escolas = Escola.query.all()
        form.escola.choices = [(e.id, e.nome) for e in escolas]
    except:
        form.escola.choices = [(1, 'Escola Padrão')]

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        role_name = form.tipo_conta.data 
        role = Role.query.filter_by(name=role_name).first()
        if not role: role = Role.query.filter_by(name='aluno').first()

        # Gerar matrícula provisória se não informada
        # Formato ex: 2025 + ID (será atualizado no commit)
        
        user = User(
            username=form.username.data, 
            email=form.email.data,
            password_hash=hashed_password,
            nome=form.username.data,
            role=role,
            escola_id=form.escola.data if form.escola.data != 0 else None
        )
        db.session.add(user)
        db.session.commit()
        
        # ATUALIZA MATRÍCULA PÓS-COMMIT (Para usar o ID)
        if role.name == 'aluno':
            user.matricula = f"{datetime.now().year}{user.id}"
        else:
            # Matrícula de Staff: PROF-123, DIR-123
            prefixo = role.name[:3].upper()
            user.matricula = f"{prefixo}-{user.id}"
        
        db.session.commit()
        
        # Pós-Cadastro
        if role.name == 'aluno':
            novo_aluno = Aluno(
                nome=user.nome,
                matricula=user.matricula, # Sincroniza
                id_user_conta=user.id
            )
            db.session.add(novo_aluno)
            db.session.commit()
            flash(f'Conta criada! Sua matrícula é: {user.matricula}', 'success')
            
        elif role.name == 'professor':
            novo_horario = Horario(nome=f"Horário de {user.username}", autor=user)
            db.session.add(novo_horario)
            db.session.commit()
            flash(f'Professor cadastrado. Matrícula funcional: {user.matricula}', 'success')
            
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.has_role('aluno'): return redirect(url_for('portal.dashboard'))
        elif current_user.has_role('professor'): return redirect(url_for('professor.dashboard'))
        return redirect(url_for('core.index')) 
        
    form = LoginForm()
    if form.validate_on_submit():
        login_input = form.login.data.strip()
        
        # QUERY SIMPLIFICADA: Tudo na tabela User
        user = User.query.filter(
            or_(
                User.email == login_input,       # Email
                User.username == login_input,    # Username
                User.matricula == login_input    # Matrícula (Agora funciona p/ todos)
            )
        ).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Bem-vindo, {user.nome or user.username}!', 'success')
            
            next_page = request.args.get('next')
            if next_page: return redirect(next_page)
                
            if user.has_role('aluno'): return redirect(url_for('portal.dashboard'))
            elif user.has_role('professor'): return redirect(url_for('professor.dashboard'))
            elif user.has_role('coordenador'): return redirect(url_for('coordenacao.dashboard'))
            else: return redirect(url_for('core.index'))
        else:
            flash('Credenciais inválidas.', 'danger')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Até logo!', 'info')
    return redirect(url_for('auth.login'))