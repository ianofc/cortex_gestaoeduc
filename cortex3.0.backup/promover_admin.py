from app import app, db
from models import User

def promover_a_admin(username_alvo):
    """
    Busca um usuário pelo nome e define is_admin = True.
    """
    with app.app_context():
        print(f"--- Buscando usuário: {username_alvo} ---")
        
        user = User.query.filter_by(username=username_alvo).first()
        
        if not user:
            print(f"❌ Erro: Usuário '{username_alvo}' não encontrado no banco de dados.")
            return

        if user.is_admin:
            print(f"ℹ️ O usuário '{user.username}' JÁ É Administrador.")
        else:
            user.is_admin = True
            # Garante que ele também é professor para não perder acesso às turmas
            user.is_professor = True 
            
            try:
                db.session.commit()
                print(f"✅ SUCESSO! O usuário '{user.username}' foi promovido a Administrador.")
                print("Agora você pode acessar a Zona de Segurança e fazer Backups.")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Erro ao salvar no banco: {e}")

if __name__ == "__main__":
    # Defina aqui o usuário que você quer promover
    USUARIO = 'iansantos'
    promover_a_admin(USUARIO)