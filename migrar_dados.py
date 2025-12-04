# migrar_dados.py

import sqlite3
import os
from datetime import date, datetime
from sqlalchemy.exc import IntegrityError

# Importa a app Flask e os modelos corretos da nova estrutura
from app import create_app, db
from app.models.users import User, Role, Escola, Notificacao, Lembrete, Habilidade
from app.models.academic import Turma, Aluno, Horario, BlocoAula
from app.models.pedagogical import Atividade, Presenca, PlanoDeAula, DiarioBordo

app_flask = create_app()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- CORREÇÃO DE CAMINHO ---
caminho_instance = os.path.join(BASE_DIR, 'instance', 'site_backup.db')
caminho_raiz = os.path.join(BASE_DIR, 'site_backup.db')

if os.path.exists(caminho_instance):
    SOURCE_DB_PATH = caminho_instance
elif os.path.exists(caminho_raiz):
    SOURCE_DB_PATH = caminho_raiz
else:
    SOURCE_DB_PATH = None

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def run_migration():
    print(f"--- INICIANDO MIGRAÇÃO BLINDADA DE DADOS ---")
    
    if not SOURCE_DB_PATH:
        print(f"❌ ERRO CRÍTICO: O arquivo 'site_backup.db' não foi encontrado.")
        return

    print(f"Origem: {SOURCE_DB_PATH}")

    try:
        source_conn = sqlite3.connect(SOURCE_DB_PATH)
        source_conn.row_factory = dict_factory
        source_cursor = source_conn.cursor()
    except Exception as e:
        print(f"❌ Erro ao abrir banco antigo: {e}")
        return

    with app_flask.app_context():
        # --- ZERA O BANCO PARA GARANTIR NOVA ESTRUTURA ---
        print("1. Resetando banco de dados (Drop All)...")
        db.drop_all() 
        print("2. Criando nova estrutura de tabelas...")
        db.create_all()

        # Cria Infraestrutura Básica (Roles e Escola)
        roles_db = {}
        for role_name in ['admin', 'professor', 'aluno', 'coordenador', 'secretaria', 'diretor', 'responsavel']:
            r = Role(name=role_name)
            db.session.add(r)
            roles_db[role_name] = r
        
        escola_padrao = Escola(nome="Escola Padrão (Migrada)", tipo="privada")
        db.session.add(escola_padrao)
        db.session.commit()
        
        # Recarrega objetos para garantir IDs
        escola_padrao = Escola.query.first()
        for r_name in roles_db:
            roles_db[r_name] = Role.query.filter_by(name=r_name).first()

        map_users = {}   
        map_turmas = {}
        map_atividades = {}
        map_alunos = {}
        map_horarios = {}
        
        # --- ETAPA 3: Migrar USERS ---
        print("\n>> Migrando Usuários e Gerando Matrículas...")
        source_cursor.execute("SELECT * FROM users")
        old_users = source_cursor.fetchall()

        for u in old_users:
            role_to_assign = roles_db['aluno']
            if u.get('is_admin', 0): role_to_assign = roles_db['admin']
            elif u.get('is_professor', 0): role_to_assign = roles_db['professor']
            
            genero = u.get('genero', 'Masculino')
            if u['username'] == 'iansantos':
                genero = 'Masculino'
                role_to_assign = roles_db['admin']

            email_final = u.get('email') or u.get('email_contato') or f"{u['username']}@migracao.com"

            matricula_gerada = u.get('matricula') 
            if not matricula_gerada:
                if role_to_assign.name == 'admin': matricula_gerada = f"ADM-{u['id']}"
                elif role_to_assign.name == 'professor': matricula_gerada = f"PROF-{u['id']}"
                else: matricula_gerada = f"STU-{u['id']}"

            # data_nascimento para o User (pode ser None)
            data_nasc_user = None 

            new_user = User(
                username=u['username'],
                email=email_final,
                password_hash=u['password_hash'],
                nome=u.get('nome', u['username']),
                role=role_to_assign,
                escola=escola_padrao,
                matricula=matricula_gerada,
                telefone=u.get('telefone'),
                foto_perfil_path=u.get('foto_perfil_path'),
                genero=genero,
                data_nascimento=data_nasc_user 
            )
            db.session.add(new_user)
            db.session.flush() 
            map_users[u['id']] = new_user.id
            print(f"   + User {new_user.username} migrado.")

        db.session.commit()
        print("   ✅ Inserção em massa de usuários concluída.")


        # --- ETAPA 4: Migrar TURMAS ---
        print("\n>> Migrando Turmas...")
        source_cursor.execute("SELECT * FROM turmas")
        old_turmas = source_cursor.fetchall()
        
        for t in old_turmas:
            novo_autor_id = map_users.get(t.get('id_user')) or list(map_users.values())[0]
            
            new_turma = Turma(
                nome=t['nome'],
                descricao=t.get('descricao'),
                turno=t.get('turno', 'Matutino'),
                autor_id=novo_autor_id
            )
            db.session.add(new_turma)
            db.session.flush()
            map_turmas[t['id']] = new_turma.id
        
        db.session.commit()
        print(f"   + {len(map_turmas)} Turmas migrada.")

        # --- ETAPA 5: Migrar HORÁRIOS ---
        print("\n>> Migrando Horários (Apenas a estrutura)...")
        try:
            source_cursor.execute("SELECT * FROM horarios")
            for h in source_cursor.fetchall():
                dono_id = map_users.get(h['id_user'])
                if dono_id:
                    new_horario = Horario(
                        nome=h['nome'],
                        ativo=bool(h.get('ativo', 1)),
                        publico=bool(h.get('publico', 0)),
                        autor_id=dono_id
                    )
                    db.session.add(new_horario)
                    db.session.flush()
                    map_horarios[h['id']] = new_horario.id

                    # Blocos
                    source_cursor.execute("SELECT * FROM blocos_aula WHERE id_horario = ?", (h['id'],))
                    for b in source_cursor.fetchall():
                        new_bloco = BlocoAula(
                            horario=new_horario,
                            dia_semana=b['dia_semana'],
                            posicao_aula=b['posicao_aula'],
                            id_turma=map_turmas.get(b['id_turma']),
                            texto_horario=b.get('texto_horario'),
                            texto_alternativo=b.get('texto_alternativo')
                        )
                        db.session.add(new_bloco)
                    db.session.commit()
        except sqlite3.OperationalError:
            print("   (Tabela de horários não encontrada, pulando...)")

        # --- ETAPA 6: Migrar ALUNOS ---
        print("\n>> Migrando Alunos...")
        source_cursor.execute("SELECT * FROM alunos")
        old_alunos = source_cursor.fetchall()
        
        for a in old_alunos:
            dt_nasc = None
            if a.get('data_nascimento'): 
                try: dt_nasc = datetime.strptime(a['data_nascimento'], '%Y-%m-%d').date()
                except: pass
            
            id_user_conta_novo = map_users.get(a.get('id_user_conta'))

            new_aluno = Aluno(
                nome=a['nome'],
                matricula=str(a.get('matricula', '')),
                # CORREÇÃO: data_nascimento removida do construtor Aluno
                email_responsavel=a.get('email_responsavel'),
                telefone_responsavel=a.get('telefone_responsavel'),
                id_turma=map_turmas.get(a['id_turma']),
                id_user_conta=id_user_conta_novo,
                data_cadastro=datetime.utcnow()
            )
            
            # Lógica para CONSOLIDAR DATA DE NASCIMENTO (no User)
            if dt_nasc and id_user_conta_novo:
                user_associado = User.query.get(id_user_conta_novo)
                if user_associado and not user_associado.data_nascimento:
                    user_associado.data_nascimento = dt_nasc
                    db.session.add(user_associado) 

            db.session.add(new_aluno)
            db.session.flush()
            map_alunos[a['id']] = new_aluno.id
        
        db.session.commit()
        print(f"   + {len(map_alunos)} alunos migrados.")


        # --- ETAPA 7: Migrar ATIVIDADES ---
        print("\n>> Migrando Atividades...")
        source_cursor.execute("SELECT * FROM atividades")
        old_atividades = source_cursor.fetchall()
        
        for atv in old_atividades:
            tid = map_turmas.get(atv['id_turma'])
            if tid:
                dt_atv = None
                if atv.get('data'):
                    try: dt_atv = datetime.strptime(atv['data'], '%Y-%m-%d').date()
                    except: pass

                new_atv = Atividade(
                    id_turma=tid,
                    titulo=atv['titulo'],
                    descricao=atv.get('descricao'),
                    tipo=atv.get('tipo', 'Atividade'),
                    data=dt_atv,
                    peso=atv.get('peso', 1.0)
                )
                db.session.add(new_atv)
                db.session.flush()
                map_atividades[atv['id']] = new_atv.id
        
        db.session.commit()
        print(f"   + {len(map_atividades)} atividades migrada.")

        # --- ETAPA 8: Migrar PRESENÇAS ---
        print("\n>> Migrando Presenças...")
        source_cursor.execute("SELECT * FROM presencas")
        for p in source_cursor.fetchall():
            aid = map_alunos.get(p['id_aluno'])
            atid = map_atividades.get(p.get('id_atividade'))
            if aid and atid:
                new_p = Presenca(
                    id_aluno=aid,
                    id_atividade=atid,
                    status=p.get('status', 'Presente'),
                    nota=p.get('nota'),
                    # CORREÇÃO: Mapeia dados antigos para campos do novo modelo
                    desempenho=p.get('desempenho'), # O valor é nullable=True no modelo final
                    observacoes=p.get('observacoes')
                )
                db.session.add(new_p)
        
        db.session.commit()
        print("   + Registros de notas/presença sincronizados.")
        
        # --- ETAPA 9: Diários ---
        try:
            source_cursor.execute("SELECT * FROM diario_bordo")
            for d in source_cursor.fetchall():
                uid = map_users.get(d['id_user'])
                tid = map_turmas.get(d['id_turma'])
                if uid:
                    new_d = DiarioBordo(
                        id_user=uid,
                        id_turma=tid,
                        anotacao=d['anotacao'],
                        data=datetime.utcnow()
                    )
                    db.session.add(new_d)
            db.session.commit()
        except: pass


    source_conn.close()
    print("\n✅ MIGRAÇÃO FINALIZADA COM SUCESSO! (Rode o seed.py em seguida)")

if __name__ == "__main__":
    run_migration()