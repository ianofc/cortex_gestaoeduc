# seed.py
from app import create_app, db
from app.models.users import User, Role, Escola
from app.models.academic import Turma, Aluno
from datetime import datetime

app = create_app()

def seed_database():
    # CORREÇÃO CRÍTICA: Importar bcrypt dentro do contexto
    with app.app_context():
        from app.extensions import bcrypt 
        print("🌱 Iniciando o plantio de dados (Seeding)...")

        # 1. Garantir que as Roles existam
        roles_names = ['admin', 'diretor', 'coordenador', 'secretaria', 'professor', 'aluno', 'responsavel']
        roles_db = {}
        
        for name in roles_names:
            role = Role.query.filter_by(name=name).first()
            if not role:
                role = Role(name=name)
                db.session.add(role)
            roles_db[name] = role
        
        db.session.commit()
        print("✅ Roles verificadas.")

        # 2. Criar Escolas
        escola_privada = Escola.query.filter_by(nome="Colégio Cortex Elite").first()
        if not escola_privada:
            escola_privada = Escola(nome="Colégio Cortex Elite", tipo="privada", email_contato="contato@cortexelite.com")
            db.session.add(escola_privada)
        
        escola_publica = Escola.query.filter_by(nome="Escola Estadual Paulo Freire").first()
        if not escola_publica:
            escola_publica = Escola(nome="Escola Estadual Paulo Freire", tipo="publica", email_contato="admin@paulofreire.edu.br")
            db.session.add(escola_publica)
        
        db.session.commit()
        print("✅ Escolas verificadas.")

        # 3. Criar Usuários de Staff (Senhas serão 123456)
        senha_hash = bcrypt.generate_password_hash("123456").decode('utf-8') 

        users_data = [
            {"username": "diretor_elite", "email": "diretor@cortex.com", "nome": "Diretor Augusto", "role": "diretor", "escola": escola_privada, "matricula": "DIR-01"},
            {"username": "coord_mariana", "email": "coord@cortex.com", "nome": "Coord. Mariana", "role": "coordenador", "escola": escola_privada, "matricula": "COORD-01"},
            {"username": "sec_roberto", "email": "sec@cortex.com", "nome": "Sec. Roberto", "role": "secretaria", "escola": escola_privada, "matricula": "SEC-01"},
            {"username": "prof_claudio", "email": "prof.biologia@cortex.com", "nome": "Prof. Cláudio (Bio)", "role": "professor", "escola": escola_privada, "matricula": "PROF-01"},
            {"username": "diretora_lucia", "email": "diretor@publica.com", "nome": "Diretora Lúcia", "role": "diretor", "escola": escola_publica, "matricula": "DIR-PUB-01"},
        ]

        for u in users_data:
            user = User.query.filter((User.email == u["email"]) | (User.username == u["username"])).first()
            if not user:
                user = User(
                    username=u["username"], 
                    email=u["email"],
                    password_hash=senha_hash,
                    nome=u["nome"],
                    role_id=roles_db[u["role"]].id,
                    escola_id=u["escola"].id,
                    matricula=u["matricula"]
                )
                db.session.add(user)
        
        db.session.commit()
        print("✅ Staff criado/atualizado.")

        # 4. Atualizar SEU Usuário (iansantos) - CORREÇÃO DE CREDENCIAIS
        
        # 1. Busca por username, email antigo e novo
        meu_usuario = User.query.filter(
            (User.username == 'iansantos') | 
            (User.email == 'ianworktech@gmail.com') | 
            (User.email == 'iansantos@admin.com')
        ).first()

        if meu_usuario:
            # GERA NOVO HASH PARA A SENHA 134679
            nova_senha_hash = bcrypt.generate_password_hash("134679").decode('utf-8') 
            
            meu_usuario.role_id = roles_db['admin'].id
            meu_usuario.password_hash = nova_senha_hash 
            meu_usuario.email = "ianworktech@gmail.com" # Define o email definitivo
            meu_usuario.username = "iansantos" # Garante o username
            meu_usuario.nome = "Ian Santos (Admin)"
            
            if not meu_usuario.escola_id:
                meu_usuario.escola_id = escola_privada.id
            db.session.add(meu_usuario)
            db.session.commit()
            print(f"👑 Usuário {meu_usuario.nome} promovido a ADMIN supremo.")
            print(f"   Login: ianworktech@gmail.com | Senha: 134679")

        # 5. Criar Alunos de Teste
        alunos_data = [
            {"username": "baby_enzo", "email": "baby@cortex.com", "nome": "Baby Enzo", "escola": escola_privada, "matricula": "2025-INF-01"},
            {"username": "lucas_silva", "email": "medio@cortex.com", "nome": "Lucas Silva", "escola": escola_privada, "matricula": "2025-MED-01"},
            {"username": "ana_uni", "email": "uni@publica.com", "nome": "Ana Universitária", "escola": escola_publica, "matricula": "2025-SUP-01"},
        ]

        for a in alunos_data:
            user_aluno = User.query.filter((User.email == a["email"]) | (User.username == a["username"])).first()
            
            if not user_aluno:
                user_aluno = User(
                    username=a["username"],
                    email=a["email"],
                    password_hash=senha_hash,
                    nome=a["nome"],
                    role_id=roles_db['aluno'].id,
                    escola_id=a["escola"].id,
                    matricula=a["matricula"]
                )
                db.session.add(user_aluno)
                db.session.commit()

            # Cria Perfil Acadêmico (Aluno)
            perfil_existente = Aluno.query.filter_by(id_user_conta=user_aluno.id).first()
            if not perfil_existente:
                perfil_aluno = Aluno(
                    nome=a["nome"],
                    matricula=a["matricula"],
                    id_user_conta=user_aluno.id,
                    data_cadastro=datetime.today()
                )
                db.session.add(perfil_aluno)

        db.session.commit()
        print("✅ Alunos de teste verificados/criados.")
        print("🚀 Banco populado com sucesso!")

if __name__ == "__main__":
    seed_database()