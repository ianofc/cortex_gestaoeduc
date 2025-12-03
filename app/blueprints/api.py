from flask import Blueprint, jsonify
from flask_login import login_required, current_user

# Blueprint para API (JSON)
# Prefixo /api/v1 permite versionamento futuro sem quebrar apps antigos
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

@api_bp.route('/status', methods=['GET'])
def status():
    """Health Check: Verifica se a API está online."""
    return jsonify({"status": "online", "service": "Cortex API"})

@api_bp.route('/user/me', methods=['GET'])
@login_required
def me():
    """Retorna dados do usuário logado (para App Mobile futuramente)."""
    return jsonify({
        "id": current_user.id,
        "nome": current_user.nome,
        "email": current_user.email,
        "role": current_user.role
    })

# Aqui entraremos futuramente com rotas como:
# @api_bp.route('/alunos/sync', methods=['POST']) -> Para sincronizar SQLite offline