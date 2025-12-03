import os
import zipfile
from datetime import datetime
from flask import Blueprint, send_file, request, flash, redirect, url_for, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

# Cria o Blueprint
backup_bp = Blueprint('backup', __name__, url_prefix='/backup')

def admin_required(f):
    """Decorator para garantir que apenas Admins acessem o backup."""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ajuste conforme sua lógica de admin. Aqui assume-se is_admin no modelo User.
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('Acesso negado. Apenas administradores podem realizar backups.', 'danger')
            return redirect(url_for('core.index'))
        return f(*args, **kwargs)
    return decorated_function

@backup_bp.route('/download', methods=['GET'])
@login_required
@admin_required
def download_backup():
    """Gera um ZIP contendo o Banco de Dados e a pasta de Uploads."""
    
    # 1. Configurar Caminhos
    # Pega o caminho do banco de dados
    db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
    else:
        flash('Backup automático suportado apenas para SQLite por enquanto.', 'danger')
        return redirect(url_for('core.index'))

    # Usa a pasta configurada no config.py
    uploads_folder = current_app.config['UPLOAD_FOLDER']
    
    # Nome do arquivo de backup
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    backup_filename = f"backup_cortex_{timestamp}.zip"
    # Salva temporariamente na raiz do projeto para enviar
    backup_path = os.path.join(current_app.root_path, backup_filename)

    try:
        # 2. Criar o ZIP
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            # Adiciona o Banco de Dados ao ZIP
            if os.path.exists(db_path):
                zipf.write(db_path, arcname='gestao_alunos.db')
            else:
                print(f"AVISO: Banco de dados não encontrado em {db_path}")
            
            # Adiciona a pasta de Uploads (Recursivamente)
            if os.path.exists(uploads_folder):
                for root, dirs, files in os.walk(uploads_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Caminho relativo dentro do zip (ex: static/uploads/imgs/foto.jpg)
                        # Calcula o caminho relativo baseado na raiz da app para manter estrutura
                        relative_path = os.path.relpath(file_path, os.path.dirname(uploads_folder))
                        zipf.write(file_path, arcname=relative_path)
            else:
                print(f"AVISO: Pasta de uploads não encontrada em {uploads_folder}")

        # 3. Enviar o arquivo para o usuário
        return send_file(
            backup_path,
            as_attachment=True,
            download_name=backup_filename,
            mimetype='application/zip'
        )

    except Exception as e:
        flash(f'Erro ao gerar backup: {str(e)}', 'danger')
        return redirect(url_for('core.index'))

@backup_bp.route('/restore', methods=['POST'])
@login_required
@admin_required
def restore_backup():
    """Recebe um ZIP e restaura o sistema."""
    
    if 'backup_file' not in request.files:
        flash('Nenhum arquivo selecionado.', 'danger')
        return redirect(url_for('core.edit_perfil'))
    
    file = request.files['backup_file']
    
    if file.filename == '':
        flash('Arquivo vazio.', 'danger')
        return redirect(url_for('core.edit_perfil'))

    if file and file.filename.endswith('.zip'):
        try:
            # 1. Salvar o ZIP temporariamente
            filename = secure_filename(file.filename)
            temp_zip_path = os.path.join(current_app.root_path, 'temp_restore.zip')
            file.save(temp_zip_path)
            
            # Caminhos de destino
            db_uri = current_app.config['SQLALCHEMY_DATABASE_URI']
            db_path = db_uri.replace('sqlite:///', '')
            
            # 2. Extrair e Restaurar
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                
                # Verificar integridade básica
                if 'gestao_alunos.db' not in zip_ref.namelist():
                    flash('Arquivo de backup inválido: gestao_alunos.db não encontrado no ZIP.', 'danger')
                    if os.path.exists(temp_zip_path):
                        os.remove(temp_zip_path)
                    return redirect(url_for('core.edit_perfil'))
                
                # A. Restaurar Banco de Dados (Sobrescreve o atual)
                zip_ref.extract('gestao_alunos.db', path=os.path.dirname(db_path) or '.')
                
                # B. Restaurar Uploads
                # Extrai tudo que começa com static/uploads
                for member in zip_ref.namelist():
                    if member.startswith('static/uploads') or member.startswith('uploads'):
                        zip_ref.extract(member, path=current_app.root_path)

            # Limpar temporário
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)
            
            flash('Sistema restaurado com sucesso! Por favor, faça login novamente.', 'success')
            return redirect(url_for('auth.logout'))

        except Exception as e:
            flash(f'Erro crítico na restauração: {str(e)}', 'danger')
            return redirect(url_for('core.edit_perfil'))
    
    flash('Formato de arquivo inválido. Use .zip', 'danger')
    return redirect(url_for('core.edit_perfil'))