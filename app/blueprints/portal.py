from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
# CORREÇÃO: app.models em vez de app.models.base_legacy
from app.models import Aluno, Presenca, Atividade, Turma, Notificacao, db
from sqlalchemy import func

portal_bp = Blueprint('portal', __name__, url_prefix='/portal')

@portal_bp.route('/')
@login_required
def dashboard():
    # 1. Verificar se o usuário logado é um aluno
    aluno = Aluno.query.filter_by(id_user_conta=current_user.id).first()

    if not aluno:
        # Se não for aluno, mas for admin/professor, manda para o dashboard principal
        if current_user.is_admin or current_user.is_professor:
            return redirect(url_for('core.dashboard'))
        
        flash('Este usuário não está vinculado a nenhum perfil de aluno.', 'warning')
        return render_template('aluno/sem_acesso.html')

    # 2. Coletar Dados da Turma
    turma = aluno.turma
    
    # 3. Calcular Frequência
    total_presencas = Presenca.query.filter_by(id_aluno=aluno.id, status='Presente').count()
    total_faltas = Presenca.query.filter_by(id_aluno=aluno.id, status='Ausente').count()
    total_aulas = total_presencas + total_faltas
    freq_percent = round((total_presencas / total_aulas * 100), 1) if total_aulas > 0 else 100

    # 4. Buscar Atividades e Notas
    atividades_realizadas = db.session.query(Atividade, Presenca)\
        .join(Presenca, Presenca.id_atividade == Atividade.id)\
        .filter(Presenca.id_aluno == aluno.id)\
        .order_by(Atividade.data.desc()).all()

    # 5. Próximas Atividades
    atividades_feitas_ids = [p.id_atividade for p in aluno.presencas]
    if turma:
        proximas_atividades = Atividade.query.filter(
            Atividade.id_turma == turma.id,
            Atividade.id.notin_(atividades_feitas_ids)
        ).order_by(Atividade.data).all()
    else:
        proximas_atividades = []

    # 6. Calcular Média Geral (Simples)
    notas = [p.nota for p in aluno.presencas if p.nota is not None]
    media_geral = round(sum(notas) / len(notas), 1) if notas else 0.0

    return render_template('aluno/dashboard.html', 
                           aluno=aluno,
                           turma=turma,
                           freq_percent=freq_percent,
                           media_geral=media_geral,
                           atividades_realizadas=atividades_realizadas,
                           proximas_atividades=proximas_atividades)