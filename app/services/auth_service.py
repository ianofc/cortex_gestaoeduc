# app/services/auth_service.py
# Centraliza lógica de login, permissões e verificação de senha.

def verificar_permissao(user, role_necessaria):
    """
    Verifica se o usuário tem a role necessária.
    Ex: verificar_permissao(current_user, 'admin')
    """
    if not user.is_authenticated:
        return False
    
    # Lógica hierárquica (ex: Admin pode tudo)
    if user.role == 'admin':
        return True
        
    return user.role == role_necessaria