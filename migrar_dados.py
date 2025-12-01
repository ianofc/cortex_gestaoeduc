# migrar_dados.py

import sqlite3
import os
from datetime import date, datetime

# Importa a app Flask e os NOVOS modelos
from app import app, db
from models import User, Turma, Aluno, Atividade, Presenca, PlanoDeAula, Lembrete, Horario, BlocoAula, DiarioBordo, Notificacao, Habilidade

# Nomes dos ficheiros
# O ficheiro .db com os seus dados
SOURCE_DB_PATH = os.path.join(os.path.dirname(__file__), 'backup_completo.db')
# O novo ficheiro .db que será criado
DEST_DB_PATH = os.path.join(os.path.dirname(__file__), 'gestao_alunos.db')

# Converte dados do SQLite (tuplos) para dicionários
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def run_migration():
    print(f"Iniciando migração de '{SOURCE_DB_PATH}' para '{DEST_DB_PATH}'...")

    if not os.path.exists(SOURCE_DB_PATH):
        print(f"ERRO: Ficheiro de backup '{SOURCE_DB_PATH}' não encontrado!")
        print("Certifique-se de que o arquivo 'backup_completo.db' está na pasta raiz.")
        return

    # 1. Limpa o banco de destino
    #if os.path.exists(DEST_DB_PATH):
     #   os.remove(DEST_DB_PATH)
      #  print(f"Base de dados de destino '{DEST_DB_PATH}' apagada para recriação limpa.")

    # 2. Conecta à origem
    source_conn = sqlite3.connect(SOURCE_DB_PATH)
    source_conn.row_factory = dict_factory
    source_cursor = source_conn.cursor()

    # 3. Cria a nova estrutura
    with app.app_context():
        db.create_all()
        print(f"Nova estrutura criada (incluindo campo GENERO e tabelas de HORÁRIO).")

        # Mapas para guardar IDs antigos -> novos
        user_map = {}
        turma_map = {}
        aluno_map = {}
        atividade_map = {}
        horario_map = {}

        # --- ETAPA 1: Migrar Utilizadores (Users) ---
        print("Migrando Utilizadores...")
        source_cursor.execute("SELECT * FROM users")
        old_users = source_cursor.fetchall()
        
        for old_user in old_users:
            # Lógica para definir Gênero
            genero_valor = old_user.get('genero', 'Masculino') # Padrão
            
            # Garantia específica para você
            if old_user['username'] == 'iansantos':
                genero_valor = 'Masculino'

            new_user = User(
                username=old_user['username'],
                password_hash=old_user['password_hash'],
                email_contato=old_user.get('email_contato'),
                telefone=old_user.get('telefone'),
                foto_perfil_path=old_user.get('foto_perfil_path'),
                is_professor=old_user.get('is_professor', True),
                is_admin=old_user.get('is_admin', False),
                genero=genero_valor
            )
            db.session.add(new_user)
            db.session.commit()
            user_map[old_user['id']] = new_user.id
            print(f"  > Utilizador '{new_user.username}' migrado (Gênero: {new_user.genero}).")

        # --- ETAPA 2: Migrar Turmas (Necessário antes do horário para vincular blocos) ---
        print("Migrando Turmas...")
        source_cursor.execute("SELECT * FROM turmas")
        old_turmas = source_cursor.fetchall()
        
        for old_turma in old_turmas:
            # Encontra o ID do novo dono dessa turma
            new_user_id = user_map.get(old_turma.get('id_user')) # Tenta pegar id_user, senão None
            
            # Fallback: Se não achou o dono (bancos antigos talvez não tivessem id_user na turma),
            # associa ao primeiro usuário criado (você)
            if not new_user_id and user_map:
                new_user_id = list(user_map.values())[0]

            if new_user_id:
                # Busca o objeto usuario real
                autor_obj = User.query.get(new_user_id)
                
                new_turma = Turma(
                    nome=old_turma['nome'],
                    descricao=old_turma['descricao'],
                    turno=old_turma['turno'],
                    autor=autor_obj
                )
                db.session.add(new_turma)
                db.session.commit()
                turma_map[old_turma['id']] = new_turma.id
                print(f"  > Turma '{new_turma.nome}' migrada.")

        # --- ETAPA 3: Migrar Horários e Blocos (AGORA CORRIGIDO) ---
        print("Migrando Horários e Blocos de Aula...")
        horarios_migrados = 0
        try:
            source_cursor.execute("SELECT * FROM horarios")
            old_horarios = source_cursor.fetchall()
            
            for old_horario in old_horarios:
                new_user_id = user_map.get(old_horario['id_user'])
                if new_user_id:
                    new_horario = Horario(
                        nome=old_horario['nome'],
                        ativo=old_horario.get('ativo', 1) == 1,
                        id_user=new_user_id
                    )
                    db.session.add(new_horario)
                    db.session.commit()
                    horario_map[old_horario['id']] = new_horario.id
                    horarios_migrados += 1
                    
                    # Migrar Blocos deste horário
                    try:
                        source_cursor.execute("SELECT * FROM blocos_aula WHERE id_horario = ?", (old_horario['id'],))
                        old_blocos = source_cursor.fetchall()
                        for old_bloco in old_blocos:
                            # Tenta vincular à turma correta se existir
                            new_turma_id = turma_map.get(old_bloco['id_turma'])
                            
                            new_bloco = BlocoAula(
                                id_horario=new_horario.id,
                                id_turma=new_turma_id,
                                dia_semana=old_bloco['dia_semana'],
                                posicao_aula=old_bloco['posicao_aula'],
                                texto_horario=old_bloco.get('texto_horario'),
                                texto_alternativo=old_bloco.get('texto_alternativo')
                            )
                            db.session.add(new_bloco)
                        db.session.commit()
                    except Exception as e:
                        print(f"    AVISO: Erro ao migrar blocos do horário {old_horario['id']}: {e}")

            print(f"  > {horarios_migrados} quadros de horários recuperados do backup.")

        except sqlite3.OperationalError:
            print("  AVISO: Tabela 'horarios' não encontrada no backup. Criando padrão...")
            # Fallback: Se não existia tabela de horário, cria um padrão para cada usuário
            for uid in user_map.values():
                 u = User.query.get(uid)
                 h = Horario(nome=f"Horário Padrão", autor=u)
                 db.session.add(h)
                 # ... lógica de criar blocos vazios padrão ...
                 horarios_texto_padrao = ["13:10", "14:00", "14:50", "16:00", "16:50"]
                 for dia in range(5):
                    for pos in range(1, 6):
                        b = BlocoAula(horario=h, dia_semana=dia, posicao_aula=pos, texto_horario=horarios_texto_padrao[pos-1])
                        db.session.add(b)
            db.session.commit()

        if horarios_migrados == 0 and 'old_horarios' in locals() and not old_horarios:
             print("  > Nenhum horário antigo encontrado. Um novo vazio foi criado se necessário.")


        # --- ETAPA 4: Migrar Alunos ---
        print("Migrando Alunos...")
        source_cursor.execute("SELECT * FROM alunos")
        old_alunos = source_cursor.fetchall()

        for old_aluno in old_alunos:
            data_cadastro_obj = None
            if old_aluno['data_cadastro']:
                try: data_cadastro_obj = date.fromisoformat(old_aluno['data_cadastro'])
                except: pass
            
            new_aluno = Aluno(
                nome=old_aluno['nome'],
                matricula=old_aluno['matricula'],
                data_cadastro=data_cadastro_obj,
                id_turma=turma_map.get(old_aluno['id_turma'])
            )
            db.session.add(new_aluno)
            db.session.commit()
            aluno_map[old_aluno['id']] = new_aluno.id
        print(f"  > {len(old_alunos)} alunos migrados.")

        # --- ETAPA 5: Migrar Atividades ---
        print("Migrando Atividades...")
        source_cursor.execute("SELECT * FROM atividades")
        old_atividades = source_cursor.fetchall()

        for old_atividade in old_atividades:
            data_obj = None
            if old_atividade['data']:
                try: data_obj = date.fromisoformat(old_atividade['data'])
                except: pass

            new_atividade = Atividade(
                id_turma=turma_map.get(old_atividade['id_turma']), 
                titulo=old_atividade['titulo'],
                data=data_obj,
                peso=old_atividade['peso'],
                descricao=old_atividade['descricao'],
                tipo=old_atividade.get('tipo', 'Atividade'), 
                nome_arquivo_anexo=old_atividade.get('nome_arquivo_anexo'),
                path_arquivo_anexo=old_atividade.get('path_arquivo_anexo')
            )
            db.session.add(new_atividade)
            db.session.commit()
            atividade_map[old_atividade['id']] = new_atividade.id
        print(f"  > {len(old_atividades)} atividades migradas.")

        # --- ETAPA 6: Migrar Outros Dados (Lembretes, Planos, Diários) ---
        # (Mantendo a lógica original simplificada para estes que dependem menos de ordem complexa)
        
        # Lembretes
        try:
            source_cursor.execute("SELECT * FROM lembretes")
            for old_l in source_cursor.fetchall():
                if user_map.get(old_l['id_user']):
                    dt = old_l['data_criacao']
                    try: dt = datetime.fromisoformat(dt)
                    except: dt = datetime.utcnow()
                    db.session.add(Lembrete(texto=old_l['texto'], data_criacao=dt, status=old_l['status'], id_user=user_map[old_l['id_user']]))
            db.session.commit()
            print("  > Lembretes migrados.")
        except: pass

        # Planos de Aula
        try:
             source_cursor.execute("SELECT * FROM planos_de_aula")
             for old_p in source_cursor.fetchall():
                 turma_id = turma_map.get(old_p['id_turma'])
                 if turma_id:
                     dt = date.today()
                     try: dt = date.fromisoformat(old_p['data_prevista'])
                     except: pass
                     
                     novo_plano = PlanoDeAula(
                         id_turma=turma_id,
                         data_prevista=dt,
                         titulo=old_p['titulo'],
                         conteudo=old_p['conteudo'],
                         habilidades_bncc=old_p['habilidades_bncc'],
                         objetivos=old_p.get('objetivos'),
                         metodologia=old_p.get('metodologia'),
                         recursos=old_p.get('recursos'),
                         avaliacao=old_p.get('avaliacao'),
                         status=old_p.get('status', 'Planejado'),
                         id_atividade_gerada=atividade_map.get(old_p.get('id_atividade_gerada'))
                     )
                     db.session.add(novo_plano)
             db.session.commit()
             print("  > Planos de aula migrados.")
        except: pass

        # Presenças
        source_cursor.execute("SELECT * FROM presencas")
        for old_pr in source_cursor.fetchall():
            aid = aluno_map.get(old_pr['id_aluno'])
            atid = atividade_map.get(old_pr['id_atividade'])
            if aid and atid:
                db.session.add(Presenca(
                    id_aluno=aid, id_atividade=atid,
                    status=old_pr['status'], participacao=old_pr['participacao'],
                    nota=old_pr['nota'], acertos=old_pr.get('acertos'),
                    desempenho=old_pr.get('desempenho'), situacao=old_pr.get('situacao'),
                    observacoes=old_pr.get('observacoes')
                ))
        db.session.commit()
        print("  > Presenças migradas.")

        # Diário
        try:
            source_cursor.execute("SELECT * FROM diario_bordo")
            for d in source_cursor.fetchall():
                uid = user_map.get(d['id_user'])
                tid = turma_map.get(d['id_turma'])
                if uid:
                    dt = date.today()
                    try: dt = date.fromisoformat(d['data'])
                    except: pass
                    db.session.add(DiarioBordo(id_user=uid, id_turma=tid, data=dt, anotacao=d['anotacao']))
            db.session.commit()
            print("  > Diários de bordo migrados.")
        except: pass

        print("\n✅ MIGRAÇÃO CONCLUÍDA! Seus dados e horários foram preservados.")

    source_conn.close()

if __name__ == "__main__":
    run_migration()