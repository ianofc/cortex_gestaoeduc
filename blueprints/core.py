import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from sqlalchemy import func, case
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user

# --- IMPORTS DE MODELOS E FORMS ---
# O bloco try/except garante compatibilidade se rodar direto ou via pacote
try:
    from models import db, User, Turma, Aluno, Atividade, Lembrete, Horario, BlocoAula, Presenca, DiarioBordo, Escola, Notificacao
    from forms import TurmaForm, LembreteForm, UserProfileForm, EscolaForm, CoordenadorForm, ProfessorForm
    # Tenta importar utils, se não existir define uma função dummy para não quebrar
    try:
        from utils import enviar_notificacao
    except ImportError:
        def enviar_notificacao(user_id, msg, link): pass
except ImportError:
    from ..models import db, User, Turma, Aluno, Atividade, Lembrete, Horario, BlocoAula, Presenca, DiarioBordo, Escola, Notificacao
    from ..forms import TurmaForm, LembreteForm, UserProfileForm, EscolaForm, CoordenadorForm, ProfessorForm
    try:
        from ..utils import enviar_notificacao
    except ImportError:
        def enviar_notificacao(user_id, msg, link): pass

# Definimos o Blueprint
core_bp = Blueprint('core', __name__)

# ------------------- SEGURANÇA: BLOQUEIO DE ALUNOS -------------------
@core_bp.before_request
def restrict_student_access():
    """
    Verifica se o usuário logado é um aluno. Se for, impede o acesso
    às rotas do 'core' (painel do professor/admin) e redireciona
    para o portal do aluno.
    """
    # Verifica se a rota atual é endpoint estático para não bloquear assets
    if request.endpoint and 'static' in request.endpoint:
        return

    if current_user.is_authenticated and getattr(current_user, 'is_aluno', False):
        # Evita loop de redirecionamento se já estiver indo para o portal
        if request.endpoint != 'portal.dashboard':
            flash('Acesso redirecionado para o Portal do Aluno.', 'info')
            # Certifique-se de que a rota 'portal.dashboard' existe no blueprint de aluno
            # Se não existir, redireciona para logout ou home segura
            return redirect(url_for('portal.dashboard'))

# ------------------- ROTAS PRINCIPAIS (DASHBOARD) -------------------

# 1. ROTA PÚBLICA (Landing Page)
@core_bp.route('/')
def index():
    # Se o usuário JÁ está logado -> Vai direto para o Dashboard
    if current_user.is_authenticated:
        return redirect(url_for('core.dashboard'))
    
    # Renderiza a Landing Page pública
    return render_template('landing.html') 

# 2. O DASHBOARD (Antigo Index - Painel Administrativo)
@core_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required 
def dashboard():
    lembrete_form = LembreteForm(prefix='lembrete')

    if lembrete_form.validate_on_submit() and request.form.get('submit_lembrete'):
        novo_lembrete = Lembrete(texto=lembrete_form.texto.data, 
                                 autor=current_user)
        db.session.add(novo_lembrete)
        db.session.commit()
        
        # Envia notificação
        enviar_notificacao(
            current_user.id, 
            f"Novo lembrete criado: {novo_lembrete.texto[:15]}...", 
            url_for('core.dashboard') 
        )
        
        flash('Lembrete salvo!', 'success')
        return redirect(url_for('core.dashboard'))

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

# ------------------- DASHBOARD GLOBAL (ESTATÍSTICAS) -------------------

@core_bp.route('/dashboard/global')
@login_required
def dashboard_global():
    # Rota renomeada para evitar conflito com a função dashboard() acima
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

# ------------------- GESTÃO DE NOTIFICAÇÕES -------------------

@core_bp.route('/notificacao/<int:id>/ler')
@login_required
def ler_notificacao(id):
    notificacao = Notificacao.query.get_or_404(id)
    if notificacao.destinatario != current_user:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('core.index'))
    
    notificacao.lida = True
    db.session.commit()
    
    if notificacao.link:
        return redirect(notificacao.link)
    return redirect(request.referrer or url_for('core.index'))

@core_bp.route('/notificacoes/ler_todas')
@login_required
def ler_todas_notificacoes():
    Notificacao.query.filter_by(destinatario=current_user, lida=False).update({'lida': True})
    db.session.commit()
    flash('Todas as notificações marcadas como lidas.', 'success')
    return redirect(request.referrer or url_for('core.index'))

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
            imgs_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'imgs')
            
            if not os.path.exists(imgs_folder):
                os.makedirs(imgs_folder)

            if current_user.foto_perfil_path:
                old_path = os.path.join(imgs_folder, current_user.foto_perfil_path)
                if os.path.exists(old_path):
                    os.remove(old_path)
                    
            filename_seguro = secure_filename(foto_upload.filename)
            _, ext_seguro = os.path.splitext(filename_seguro)
            filename_final = f"perfil_{current_user.id}_{int(datetime.now().timestamp())}{ext_seguro}"
            
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

# ------------------- ROTAS DE LISTAGEM -------------------

@core_bp.route('/turmas/listar')
@login_required
def listar_turmas():
    turmas = current_user.turmas 
    return render_template('list/listar_turmas.html', turmas=turmas)

@core_bp.route('/atividades/listar')
@login_required
def listar_atividades():
    turmas_ids = [t.id for t in current_user.turmas]
    
    if not turmas_ids:
        atividades = []
    else:
        atividades = Atividade.query.filter(Atividade.id_turma.in_(turmas_ids)).order_by(Atividade.data.desc()).all()
        
    return render_template('list/listar_atividades.html', atividades=atividades)

@core_bp.route('/professores')
@login_required
def listar_professores():
    professores = User.query.filter_by(is_professor=True).all()
    return render_template('list/listar_professores.html', professores=professores)

@core_bp.route('/atividade/excluir/<int:id>')
@login_required
def excluir_atividade(id):
    atividade = Atividade.query.get_or_404(id)
    if not atividade.turma or atividade.turma.autor != current_user:
        flash('Não autorizado.', 'danger')
        return redirect(url_for('core.index'))

    db.session.delete(atividade)
    db.session.commit()
    flash('Atividade removida com sucesso.', 'success')
    return redirect(url_for('core.listar_atividades'))

@core_bp.route('/usuario/excluir/<int:id>')
@login_required
def excluir_usuario(id):
    if not getattr(current_user, 'is_admin', False):
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

# ------------------- ESCOLAS E COORDENADORES (NOVAS) -------------------

@core_bp.route('/escolas/listar')
@login_required
def listar_escolas():
    if not getattr(current_user, 'is_admin', False):
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('core.index'))
        
    escolas = Escola.query.all()
    return render_template('list/listar_escola.html', escolas=escolas)

@core_bp.route('/escola/adicionar', methods=['GET', 'POST'])
@login_required
def add_escola():
    if not getattr(current_user, 'is_admin', False):
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('core.index'))
        
    form = EscolaForm()
    if form.validate_on_submit():
        escola = Escola(
            nome=form.nome.data,
            endereco=form.endereco.data,
            telefone=form.telefone.data,
            email_contato=form.email_contato.data
        )
        db.session.add(escola)
        db.session.commit()
        flash('Escola cadastrada com sucesso!', 'success')
        return redirect(url_for('core.listar_escolas'))
        
    return render_template('add/add_escola.html', form=form)

@core_bp.route('/escola/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_escola(id):
    if not getattr(current_user, 'is_admin', False):
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('core.index'))
        
    escola = Escola.query.get_or_404(id)
    form = EscolaForm(obj=escola)
    
    if form.validate_on_submit():
        form.populate_obj(escola)
        db.session.commit()
        flash('Escola atualizada com sucesso!', 'success')
        return redirect(url_for('core.listar_escolas'))
        
    return render_template('edit/edit_escola.html', form=form, escola=escola)

@core_bp.route('/escola/excluir/<int:id>')
@login_required
def excluir_escola(id):
    if not getattr(current_user, 'is_admin', False):
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('core.index'))
        
    escola = Escola.query.get_or_404(id)
    db.session.delete(escola)
    db.session.commit()
    flash('Escola excluída.', 'success')
    return redirect(url_for('core.listar_escolas'))

# --- COORDENADORES ---

@core_bp.route('/coordenadores/listar')
@login_required
def listar_coordenadores():
    if not getattr(current_user, 'is_admin', False):
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('core.index'))
        
    coordenadores = User.query.filter_by(is_coordenador=True).all()
    return render_template('list/listar_coordenadores.html', coordenadores=coordenadores)

@core_bp.route('/coordenador/adicionar', methods=['GET', 'POST'])
@login_required
def add_coordenador():
    if not getattr(current_user, 'is_admin', False):
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('core.index'))
        
    form = CoordenadorForm()
    # Popula o select de escolas
    form.escola_id.choices = [(e.id, e.nome) for e in Escola.query.all()]
    
    if form.validate_on_submit():
        from app import bcrypt # Import tardio para evitar circularidade se necessário
        hashed_pw = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        
        novo_coord = User(
            username=form.nome.data,
            email_contato=form.email.data,
            password_hash=hashed_pw,
            is_coordenador=True,
            is_professor=False, # Coordenador não dá aula por padrão
            escola_id=form.escola_id.data
        )
        db.session.add(novo_coord)
        db.session.commit()
        flash('Coordenador cadastrado!', 'success')
        return redirect(url_for('core.listar_coordenadores'))
        
    return render_template('add/add_coordenador.html', form=form)

@core_bp.route('/coordenador/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_coordenador(id):
    if not getattr(current_user, 'is_admin', False):
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('core.index'))
        
    coord = User.query.get_or_404(id)
    form = CoordenadorForm(obj=coord)
    form.escola_id.choices = [(e.id, e.nome) for e in Escola.query.all()]
    form.senha.validators = [] # Senha opcional na edição
    
    if request.method == 'GET':
        form.nome.data = coord.username
        form.email.data = coord.email_contato
        form.escola_id.data = coord.escola_id

    if form.validate_on_submit():
        coord.username = form.nome.data
        coord.email_contato = form.email.data
        coord.escola_id = form.escola_id.data
        
        if form.senha.data:
            from app import bcrypt
            coord.password_hash = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
            
        db.session.commit()
        flash('Coordenador atualizado!', 'success')
        return redirect(url_for('core.listar_coordenadores'))
        
    return render_template('edit/edit_coordenador.html', form=form, coord=coord)

@core_bp.route('/professor/adicionar', methods=['GET', 'POST'])
@login_required
def add_professor():
    # Qualquer admin ou coordenador pode adicionar professor
    if not (getattr(current_user, 'is_admin', False) or getattr(current_user, 'is_coordenador', False)):
        flash('Acesso restrito.', 'danger')
        return redirect(url_for('core.index'))
    
    form = ProfessorForm()
    
    if form.validate_on_submit():
        from app import bcrypt
        hashed_pw = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        
        novo_prof = User(
            username=form.nome.data,
            email_contato=form.email.data,
            password_hash=hashed_pw,
            is_professor=True,
            # Vincula à mesma escola do coordenador se quem cria for coordenador
            escola_id=current_user.escola_id if getattr(current_user, 'is_coordenador', False) else None
        )
        db.session.add(novo_prof)
        db.session.commit()
        flash('Professor cadastrado!', 'success')
        return redirect(url_for('core.listar_professores'))
        
    return render_template('add/add_professor.html', form=form)