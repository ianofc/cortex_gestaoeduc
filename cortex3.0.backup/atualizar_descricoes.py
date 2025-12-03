# atualizar_descricoes.py

from app import app, db
from models import Turma, User

def atualizar_turmas():
    with app.app_context():
        print("--- ATUALIZANDO DESCRIÇÕES DAS TURMAS (DIRETRIZES PEDAGÓGICAS) ---")
        
        # Identifica o usuário (ajuste se necessário, busca o 'iansantos' ou o primeiro user)
        user = User.query.filter_by(username='iansantos').first()
        if not user:
            user = User.query.first()
            
        if not user:
            print("ERRO: Nenhum usuário encontrado.")
            return

        # Busca as turmas desse usuário
        turmas = Turma.query.filter_by(autor=user).all()
        print(f"Usuário: {user.username} | Total de turmas encontradas: {len(turmas)}\n")

        # Dicionário de palavras-chave -> Descrição da Coordenadora
        # A chave é um termo que identifica a turma no nome (ex: "1º ADM")
        diretrizes = {
            "2º INTEGRAL": "Estações dos Saberes 7: Trazer experiências práticas na área de Química e Física para ampliar o potencial científico.",
            "1º INTEGRAL": "Agroecologia: Seguir ementário oficial.",
            "1º ADM": "Estações dos Saberes: Utilizar ementário da apostila (Ciências Naturais) com foco em aplicabilidade.",
            "FLUXO": "Matemática Prática: Educação financeira e empreendedora utilizando materiais concretos.", # Serve para 2º e 3º Fluxo
            "2º DM": "Química: Seguir plano de curso.",
            "3º C": "Eletiva: Reforço de matemática básica com atividades 'mão na massa'."
        }

        atualizadas = 0
        
        for turma in turmas:
            nome_upper = turma.nome.upper()
            nova_descricao = None

            # Verifica qual diretriz se aplica a esta turma
            for chave, texto in diretrizes.items():
                if chave in nome_upper:
                    nova_descricao = texto
                    break # Para na primeira correspondência encontrada
            
            # Se encontrou uma diretriz, atualiza
            if nova_descricao:
                # Mantém a descrição antiga se quiser, ou substitui totalmente.
                # Aqui vamos substituir para ficar limpo com a diretriz oficial.
                print(f" -> Atualizando '{turma.nome}'...")
                print(f"    Antiga: {turma.descricao}")
                print(f"    Nova:   {nova_descricao}")
                
                turma.descricao = nova_descricao
                atualizadas += 1
            else:
                print(f" -> Nenhuma diretriz específica encontrada para '{turma.nome}'. Mantida original.")

        if atualizadas > 0:
            db.session.commit()
            print(f"\n✅ Sucesso! {atualizadas} turmas foram atualizadas com as diretrizes da coordenação.")
        else:
            print("\n⚠️ Nenhuma turma precisou ser atualizada (verifique se os nomes das turmas correspondem às chaves).")

if __name__ == "__main__":
    atualizar_turmas()