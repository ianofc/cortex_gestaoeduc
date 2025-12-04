# app/blueprints/coordenacao.py

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

# Define o Blueprint 'coordenacao'. template_folder não é necessário
# se os templates estiverem em app/templates/coordenacao.
coordenacao_bp = Blueprint('coordenacao', __name__) 

@coordenacao_bp.before_request
@login_required
def check_permission():
    # Middleware de segurança: Garante que users com role certa (ou admin) acessem
    if not current_user.has_role('coordenador') and not current_user.has_role('diretor') and not current_user.has_role('admin'):
        # Se não for autorizado, redireciona para a home
        return redirect(url_for('core.index'))
    pass

# Rota simples: o prefixo '/coordenacao' será dado no registro em __init__.py
@coordenacao_bp.route('/dashboard') 
def dashboard():
    # O template já existe em app/templates/coordenacao/dashboard/visao_geralcoord.html
    return render_template('coordenacao/dashboard/visao_geralcoord.html', title='Painel da Coordenação')