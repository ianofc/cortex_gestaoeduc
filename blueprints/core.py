# blueprints/core.py

import os
from datetime import date, datetime 
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from sqlalchemy import func, case
from werkzeug.utils import secure_filename 

# Imports de Módulos Locais
from models import db, User, Turma, Aluno, Atividade, Lembrete, Horario, BlocoAula, Presenca, DiarioBordo
from forms import TurmaForm, LembreteForm, UserProfileForm

from flask_login import login_required, current_user

core_bp = Blueprint('core', __name__, url_prefix='/')

# ------------------- ROTAS PRINCIPAIS (DASHBOARD) -------------------

@core_bp.route('/', methods=['GET', 'POST'])
@login_required 
def index():
    lembrete_form = LembreteForm(prefix='lembrete')

    if lembrete_form.validate_on_submit() and request.form.get('submit_lembrete'):
        novo_lembrete = Lembrete(texto=lembrete_form.texto.data, 
                                 autor=current_user)
        db.session.add(novo_lembrete)
        db.session.commit()
        flash('Lembrete salvo!', 'success')
        return redirect(url_for('core.index'))

    q = request.args.get('q', '') 
    
    turmas_query = Turma.query.filter_by(autor=current_user)
    if q:
        turmas_query = turmas_query.filter(Turma.nome.ilike(f'%{q}%'))
    turmas = turmas_query.order_by(Turma.nome).all()
    
    lembretes = Lembrete.query.filter_by(autor=current_user, status='Ativo').order_by(Lembrete.data_criacao.desc()).all()
    
    horario = Horario.query.filter_by(autor=current_user, ativo=True).first()
    blocos_map = {}
    horarios_texto = []
    dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

    if horario:
        blocos_db = BlocoAula.query.filter_by(id_horario=horario.id).order_by(BlocoAula.posicao_aula, BlocoAula.dia_semana).all()
        blocos_map = { (b.dia_semana, b.posicao_aula): b for b in blocos_db }
        
        horarios_texto_raw = sorted(list(set(
            b.texto_horario for b in blocos_db if b.posicao_aula <= 5 and b.texto_horario
        )), key=lambda x: int(x.split(':')[0] + x.split(':')[1]))
        
        horarios_texto = horarios_texto_raw[:5] 
        
        if len(horarios_texto) < 5:
            horarios_texto.extend(["--:--"] * (5 - len(horarios_texto)))
    else:
        horarios_texto = ["--:--"] * 5
    
    return render_template('main/index.html', 
                           turmas=turmas, 
                           lembrete_form=lembrete_form,
                           lembretes=lembretes,
                           q=q,
                           blocos_map_widget=blocos_map,
                           horarios_texto_widget=horarios_texto,
                           dias_semana_widget=dias_semana
                           )

# ------------------- GESTÃO DE TURMAS (CRUD) -------------------

@core_bp.route('/add_turma', methods=['GET', 'POST'])
@login_required
def add_turma():
    form = TurmaForm()
    if form.validate_on_submit():
        nova_turma = Turma(
            nome=form.nome.data, 
            descricao=form.descricao.data, 
            turno=form.turno.data,
            autor=current_user 
        )
        db.session.add(nova_turma)
        db.session.commit()
        flash('Turma criada com sucesso!', 'success')
        return redirect(url_for('core.index'))
    
    return render_template('add/add_turma.html', form=form, title="Adicionar Turma")

@core_bp.route('/turma/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_turma(id):
    turma = Turma.query.get_or_404(id)
    if turma.autor != current_user:
        flash('Não autorizado.', 'danger')
        return redirect(url_for('core.index'))

    form = TurmaForm(obj=turma)
    if form.validate_on_submit():
        turma.nome = form.nome.data
        turma.descricao = form.descricao.data
        turma.turno = form.turno.data
        db.session.commit()
        flash('Turma atualizada!', 'success')
        return redirect(url_for('core.listar_turmas'))
    
    return render_template('edit/edit_turma.html', form=form, turma=turma)

@core_bp.route('/turma/excluir/<int:id>')
@login_required
def excluir_turma(id):
    turma = Turma.query.get_or_404(id)
    if turma.autor != current_user:
        flash('Não autorizado.', 'danger')
        return redirect(url_for('core.index'))
        
    db.session.delete(turma)
    db.session.commit()
    flash('Turma excluída com sucesso.', 'success')
    return redirect(url_for('core.listar_turmas'))

# ROTA REMOVIDA: ver_turma (Causava loop de redirecionamento com alunos.turma)

# ------------------- DASHBOARD GLOBAL -------------------

@core_bp.route('/dashboard')
@login_required
def dashboard():
    total_turmas = Turma.query.filter_by(autor=current_user).count()
    
    total_alunos = db.session.query(func.count(Aluno.id))\
        .join(Turma)\
        .filter(Turma.id_user == current_user.id).scalar()
        
    total_atividades = db.session.query(func.count(Atividade.id))\
        .join(Turma)\
        .filter(Turma.id_user == current_user.id).scalar()

    desempenho_turmas_raw = db.session.query(
        Turma.nome,
        func.avg(Presenca.desempenho).label('media_desempenho')
    ).select_from(Turma).join(Turma.alunos, isouter=True).join(Aluno.presencas, isouter=True)\
     .filter(Turma.id_user == current_user.id)\
     .group_by(Turma.nome)\
     .order_by(Turma.nome).all()
     
    frequencia_turmas_raw = db.session.query(
        Turma.nome,
        func.avg(case((Presenca.status == 'Presente', 100.0), (Presenca.status == 'Justificado', 100.0), else_=0.0)).label('media_frequencia')
    ).select_from(Turma).join(Turma.alunos, isouter=True).join(Aluno.presencas, isouter=True)\
     .filter(Turma.id_user == current_user.id)\
     .group_by(Turma.nome).all()

    dados_combinados = {}
    for d in desempenho_turmas_raw:
        dados_combinados[d.nome] = {"desempenho": float(d.media_desempenho) if d.media_desempenho else 0}
        
    for f in frequencia_turmas_raw:
        if f.nome not in dados_combinados:
            dados_combinados[f.nome] = {}
        dados_combinados[f.nome]['frequencia'] = float(f.media_frequencia) if f.media_frequencia else 0

    dados_graficos = [
        {"turma": nome, **dados} 
        for nome, dados in dados_combinados.items()
    ]
    
    top_alunos_data = []
    
    alunos_scores = db.session.query(
        Aluno,
        func.sum(Presenca.nota).label('pontos_obtidos'),
        func.sum(Atividade.peso).label('pontos_max_aluno')
    ).select_from(Aluno).join(Turma)\
     .join(Presenca, isouter=True).join(Atividade, isouter=True)\
     .filter(Turma.id_user == current_user.id)\
     .group_by(Aluno.id, Aluno.nome)\
     .all()
     
    for aluno, pontos_obtidos, pontos_max_aluno in alunos_scores:
        pontos_obtidos = float(pontos_obtidos) if pontos_obtidos else 0.0
        pontos_max_aluno = float(pontos_max_aluno) if pontos_max_aluno and pontos_max_aluno > 0 else 0.0
        
        if pontos_max_aluno > 0:
            percentual = (pontos_obtidos / pontos_max_aluno) * 100
        else:
            percentual = 0.0
            
        top_alunos_data.append({
            "aluno": aluno,
            "pontos_obtidos": pontos_obtidos,
            "pontos_max_aluno": pontos_max_aluno,
            "percentual": percentual
        })
        
    top_alunos_data = [
        a for a in top_alunos_data if a['pontos_max_aluno'] > 0
    ]
    top_alunos_data.sort(key=lambda x: x['percentual'], reverse=True)
    top_alunos_data = top_alunos_data[:10]
    
    return render_template('geral/dashboard_global.html',
                           total_turmas=total_turmas,
                           total_alunos=total_alunos,
                           total_atividades=total_atividades,
                           dados_combinados=dados_graficos, 
                           top_alunos=top_alunos_data
                           )

# ------------------- PERFIL DE USUÁRIO -------------------

@core_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def edit_perfil():
    form = UserProfileForm(original_username=current_user.username)
    
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email_contato.data = current_user.email_contato
        form.telefone.data = current_user.telefone
        form.genero.data = current_user.genero 

    if form.validate_on_submit():
        foto_upload = request.files.get('foto_perfil')
        
        if foto_upload and foto_upload.filename != '':
            # Define a pasta de imagens dentro de static/uploads
            imgs_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'imgs')
            
            # Garante que a pasta existe
            if not os.path.exists(imgs_folder):
                os.makedirs(imgs_folder)

            # Remove a foto antiga se existir (procurando na pasta correta)
            if current_user.foto_perfil_path:
                old_path = os.path.join(imgs_folder, current_user.foto_perfil_path)
                if os.path.exists(old_path):
                    os.remove(old_path)
                    
            filename_seguro = secure_filename(foto_upload.filename)
            _, ext_seguro = os.path.splitext(filename_seguro)
            filename_final = f"perfil_{current_user.id}_{int(datetime.now().timestamp())}{ext_seguro}"
            
            # Caminho completo para salvar o arquivo
            filepath = os.path.join(imgs_folder, filename_final)
            
            foto_upload.save(filepath)
            
            current_user.foto_perfil_path = filename_final

        current_user.username = form.username.data
        current_user.email_contato = form.email_contato.data
        current_user.telefone = form.telefone.data
        current_user.genero = form.genero.data 
        
        db.session.commit()
        flash('Perfil e preferências atualizados com sucesso!', 'success')
        return redirect(url_for('core.edit_perfil'))

    return render_template('edit/edit_perfil.html', form=form, title="Editar Perfil")

# ------------------- LEMBRETES -------------------

@core_bp.route('/lembrete/<int:id>/concluir', methods=['POST'])
@login_required
def concluir_lembrete(id):
    lembrete = Lembrete.query.get_or_404(id)
    if lembrete.autor != current_user:
        flash('Não autorizado.', 'danger')
        return redirect(url_for('core.index'))
    
    lembrete.status = 'Concluido'
    db.session.commit()
    flash('Lembrete concluído.', 'info')
    return redirect(url_for('core.index'))

@core_bp.route('/lembrete/<int:id>/deletar', methods=['POST'])
@login_required
def deletar_lembrete(id):
    lembrete = Lembrete.query.get_or_404(id)
    if lembrete.autor != current_user:
        flash('Não autorizado.', 'danger')
        return redirect(url_for('core.index'))
        
    db.session.delete(lembrete)
    db.session.commit()
    flash('Lembrete deletado.', 'info')
    return redirect(url_for('core.index'))

# ------------------- ROTAS DE LISTAGEM (NOVAS) -------------------

# 1. LISTAR TURMAS
@core_bp.route('/turmas/listar')
@login_required
def listar_turmas():
    turmas = current_user.turmas 
    return render_template('list/listar_turmas.html', turmas=turmas)

# 2. LISTAR ATIVIDADES
@core_bp.route('/atividades/listar')
@login_required
def listar_atividades():
    # Obtém IDs das turmas do professor atual
    turmas_ids = [t.id for t in current_user.turmas]
    
    if not turmas_ids:
        atividades = []
    else:
        # Usamos Atividade.id_turma.in_(...) para filtrar
        atividades = Atividade.query.filter(Atividade.id_turma.in_(turmas_ids)).order_by(Atividade.data.desc()).all()
        
    return render_template('list/listar_atividades.html', atividades=atividades)

# 3. LISTAR PROFESSORES
@core_bp.route('/professores')
@login_required
def listar_professores():
    # Lista todos os usuários marcados como professor
    professores = User.query.filter_by(is_professor=True).all()
    return render_template('list/listar_professores.html', professores=professores)

# 4. EXCLUIR ATIVIDADE (Ação)
@core_bp.route('/atividade/excluir/<int:id>')
@login_required
def excluir_atividade(id):
    atividade = Atividade.query.get_or_404(id)
    
    # Verifica se a turma da atividade pertence ao usuário atual
    if not atividade.turma or atividade.turma.autor != current_user:
        flash('Não autorizado.', 'danger')
        return redirect(url_for('core.index'))

    db.session.delete(atividade)
    db.session.commit()
    flash('Atividade removida com sucesso.', 'success')
    return redirect(url_for('core.listar_atividades'))

# 5. EXCLUIR USUÁRIO (Admin/Coordenador)
@core_bp.route('/usuario/excluir/<int:id>')
@login_required
def excluir_usuario(id):
    # Proteção simples: Apenas Admin pode excluir (se houver essa flag)
    if not current_user.is_admin:
         flash('Acesso negado. Apenas administradores podem excluir usuários.', 'danger')
         return redirect(url_for('core.index'))

    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('Você não pode excluir a si mesmo!', 'danger')
        return redirect(request.referrer)
        
    db.session.delete(user)
    db.session.commit()
    flash('Usuário removido com sucesso.', 'success')
    return redirect(request.referrer)

# ------------------- ROTAS PARA ESCOLAS E COORDENADORES (NOVAS) -------------------

@core_bp.route('/escolas/listar')
@login_required
def listar_escolas():
    # Apenas admins podem ver todas as escolas
    if not current_user.is_admin:
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('core.index'))
        
    from models import Escola # Import tardio para evitar ciclo se necessário
    escolas = Escola.query.all()
    return render_template('list/listar_escola.html', escolas=escolas)

@core_bp.route('/coordenadores/listar')
@login_required
def listar_coordenadores():
    # Apenas admins
    if not current_user.is_admin:
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('core.index'))
        
    coordenadores = User.query.filter_by(is_coordenador=True).all()
    return render_template('list/listar_coordenadores.html', coordenadores=coordenadores)