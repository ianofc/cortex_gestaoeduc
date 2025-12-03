# alimentar_sistema.py

from app import app, db
from models import User, Turma, Atividade, Lembrete, PlanoDeAula, DiarioBordo
from datetime import date, datetime

def alimentar():
    with app.app_context():
        print("--- INICIANDO ALIMENTAÇÃO DO SISTEMA ---")
        
        # 1. Identificar o Usuário (Assume que é o seu usuário, o primeiro criado ou 'iansantos')
        user = User.query.filter_by(username='iansantos').first()
        if not user:
            user = User.query.first()
        
        if not user:
            print("ERRO: Nenhum usuário encontrado para vincular os dados.")
            return

        print(f"Vinculando dados ao usuário: {user.username}")
        
        # Busca todas as turmas deste usuário
        turmas = Turma.query.filter_by(autor=user).all()
        
        if not turmas:
            print("AVISO: Nenhuma turma encontrada. Crie as turmas no painel primeiro (ex: '3º ADM', '1º Integral').")
            return

        # ==============================================================================
        # ETAPA 1: CRIAR ATIVIDADES (NOTAS)
        # Baseado na sua mensagem: Simulado (3.0), Gincana (1.0), Consciência Negra (A critério - pus 2.0)
        # ==============================================================================
        print("\n>> Gerando Atividades Avaliativas...")
        
        for turma in turmas:
            nome_turma = turma.nome.upper()
            
            # 1.1 Simulado (Para todos - Adaptado se não fizeram)
            # Verifica se já existe para não duplicar
            if not Atividade.query.filter_by(id_turma=turma.id, titulo="Simulado III Unidade").first():
                obs_simulado = "Avaliação oficial."
                # Lógica para turmas que não fizeram (assumindo que não sejam 3º ano, baseado na sua mensagem)
                if "3" not in nome_turma:
                    obs_simulado = "Nota atribuída via Prova/Atividade (Adaptação)."
                
                ativ_simulado = Atividade(
                    id_turma=turma.id,
                    titulo="Simulado III Unidade",
                    tipo="Prova",
                    peso=3.0,
                    data=date(2025, 12, 5), # Data aproximada do fechamento
                    descricao=f"Conteúdo Geral. {obs_simulado}"
                )
                db.session.add(ativ_simulado)
                print(f"   + Simulado criado para {turma.nome}")

            # 1.2 Gincana / Jogos Interclasse (Extra)
            if not Atividade.query.filter_by(id_turma=turma.id, titulo="Gincana Interclasse").first():
                ativ_gincana = Atividade(
                    id_turma=turma.id,
                    titulo="Gincana Interclasse",
                    tipo="Atividade",
                    peso=1.0, # Ponto Extra
                    data=date(2025, 12, 10), # Data dos jogos (09 a 11/12)
                    descricao="Participação e desempenho nos jogos interclasse."
                )
                db.session.add(ativ_gincana)
                print(f"   + Gincana criada para {turma.nome}")

            # 1.3 Projeto Novembro Negro
            if not Atividade.query.filter_by(id_turma=turma.id, titulo="Proj. Consciência Negra").first():
                ativ_negra = Atividade(
                    id_turma=turma.id,
                    titulo="Proj. Consciência Negra",
                    tipo="Trabalho",
                    peso=2.0, # Valor sugerido (já que é 'a critério')
                    data=date(2025, 11, 25), # Data da Culminância
                    descricao="Atividades desenvolvidas durante o mês de novembro."
                )
                db.session.add(ativ_negra)
                print(f"   + Proj. Consciência Negra criado para {turma.nome}")

            # 1.4 SABE / SAEB (Apenas 3º Ano)
            if "3" in nome_turma or "TERCEIR" in nome_turma:
                if not Atividade.query.filter_by(id_turma=turma.id, titulo="Avaliação SAEB/SABE").first():
                    ativ_saeb = Atividade(
                        id_turma=turma.id,
                        titulo="Avaliação SAEB/SABE",
                        tipo="Prova",
                        peso=1.0,
                        data=date(2025, 11, 1), # Data fictícia passada
                        descricao="Pontuação exclusiva para terceiros anos."
                    )
                    db.session.add(ativ_saeb)
                    print(f"   + SAEB criado para {turma.nome}")

        db.session.commit()

        # ==============================================================================
        # ETAPA 2: LEMBRETES E PRAZOS (Baseado no PDF)
        # ==============================================================================
        print("\n>> Criando Lembretes do Calendário...")
        
        lembretes_pdf = [
            "24-25/11: Culminância Consciência Negra (Aula normal manhã, tarde até 15h).",
            "02/12: Apresentação 'Vidas Secas' (3º ADM/C) e Seminário Afro.",
            "05/12: PRAZO FINAL - Resultados III Unidade (3ºs Anos).",
            "09-11/12: Jogos Interclasse (Gincana).",
            "11/12: Conselho de Classe (3º ADM) e Entrega Resultados (1º/2º).",
            "17-18/12: Formaturas."
        ]

        for texto in lembretes_pdf:
            # Verifica duplicidade simples
            if not Lembrete.query.filter_by(texto=texto, id_user=user.id).first():
                novo_lembrete = Lembrete(texto=texto, autor=user)
                db.session.add(novo_lembrete)
                print(f"   + Lembrete adicionado: {texto[:30]}...")
        
        db.session.commit()

        # ==============================================================================
        # ETAPA 3: CONTEÚDO PEDAGÓGICO (Planos de Aula Automáticos)
        # Baseado nas msgs da Coordenadora Ania
        # ==============================================================================
        print("\n>> Inserindo Planejamentos Específicos...")

        # Mapeamento: Termo no nome da turma -> Conteúdo
        mapa_conteudo = {
            "2º INTEGRAL": {
                "tema": "Estações dos Saberes 7 (Química/Física)",
                "conteudo": "Experiências práticas na área de química e física para ampliar potencial científico."
            },
            "1º INTEGRAL": {
                "tema": "Agroecologia",
                "conteudo": "Seguir ementário oficial de Agroecologia."
            },
            "1º ADM": {
                "tema": "Estações dos Saberes (Ciências Naturais)",
                "conteudo": "Utilizar ementário da apostila. Foco em aplicabilidade das ciências naturais."
            },
            "FLUXO": { # Pega 2º e 3º Fluxo
                "tema": "Matemática Prática",
                "conteudo": "Matemática para a vida: educação financeira e empreendedora. Uso de materiais concretos."
            },
            "2º DM": {
                "tema": "Química Geral",
                "conteudo": "Seguir plano de curso regular."
            },
            "3º C": {
                "tema": "Eletiva: Reforço Matemática",
                "conteudo": "Reforço de matemática básica com atividades 'mão na massa'."
            }
        }

        for turma in turmas:
            nome = turma.nome.upper()
            dados_plano = None

            # Tenta encontrar a regra correspondente
            for chave, dados in mapa_conteudo.items():
                if chave in nome:
                    dados_plano = dados
                    break
            
            if dados_plano:
                # Cria o plano se não existir
                if not PlanoDeAula.query.filter_by(id_turma=turma.id, titulo=dados_plano['tema']).first():
                    novo_plano = PlanoDeAula(
                        id_turma=turma.id,
                        data_prevista=date.today(),
                        titulo=dados_plano['tema'],
                        conteudo=dados_plano['conteudo'],
                        objetivos="Cumprir diretrizes da coordenação (Ania).",
                        metodologia="Aula prática / Exposicao dialogada",
                        status="Planejado"
                    )
                    db.session.add(novo_plano)
                    print(f"   + Plano '{dados_plano['tema']}' criado para {turma.nome}")

        db.session.commit()
        print("\n--- PROCESSO CONCLUÍDO COM SUCESSO! ---")

if __name__ == "__main__":
    alimentar()