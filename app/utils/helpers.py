import os
import requests 
import json     
from io import BytesIO
import docx
from datetime import datetime
from flask import current_app
# ATUALIZADO: Adicionei Presenca e Atividade aos imports
from app.models.base_legacy import db, Notificacao, Presenca, Atividade 

# Import condicional do PyPDF2, essencial para ler PDFs
try:
    from PyPDF2 import PdfReader
except ImportError:
    # Aviso para o desenvolvedor caso a biblioteca não esteja instalada
    print("AVISO: PyPDF2 não instalado. A leitura de PDF falhará. Instale com: pip install PyPDF2")
    PdfReader = None

# --- SISTEMA DE NOTIFICAÇÕES ---

def enviar_notificacao(id_user, texto, link=None):
    """
    Cria uma nova notificação para um usuário.
    Uso: enviar_notificacao(current_user.id, 'Backup realizado com sucesso!', '/backup')
    Retorna True se sucesso, False se erro.
    """
    try:
        nova_notificacao = Notificacao(
            id_user=id_user,
            texto=texto,
            link=link,
            lida=False,
            data_criacao=datetime.utcnow()
        )
        db.session.add(nova_notificacao)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Erro ao enviar notificação: {e}")
        db.session.rollback()
        return False

# --- FUNÇÃO HELPER DE VALIDAÇÃO DE FICHEIROS (allowed_file) ---

def allowed_file(filename):
    """
    Verifica se a extensão do ficheiro é permitida com base na lista de tipos
    definida nos formulários de upload.
    """
    # Extensões permitidas com base no forms.py (Atividade e Material)
    ALLOWED_EXTENSIONS = {
        'pdf', 'docx', 'pptx', 'jpg', 'png', 'txt', 'zip', 'xls', 'xlsx'
    }
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Funções de Extração de Texto (File I/O) ---

def extrair_texto_docx(file_stream):
    """Extrai texto de um ficheiro .docx a partir de um stream de bytes."""
    try:
        doc = docx.Document(file_stream)
        return "\n".join([para.text for para in doc.paragraphs if para.text])
    except Exception as e:
        print(f"Erro ao ler DOCX da memória: {e}")
        return ""

def extrair_texto_pdf(file_stream):
    """Extrai texto de um ficheiro .pdf a partir de um stream de bytes."""
    if PdfReader is None:
        print("Erro: PyPDF2 não está instalado, não é possível ler PDF.")
        return ""
    try:
        text = ""
        reader = PdfReader(file_stream)
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Erro ao ler PDF da memória: {e}")
        return ""

def extrair_texto_de_ficheiro(file_stream_or_path, filename):
    """
    Função principal que decide qual helper usar para extrair texto.
    Aceita um path (string) ou um stream de bytes (BytesIO).
    """
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    # Se for um path (string), abre como ficheiro
    if isinstance(file_stream_or_path, str):
        if not os.path.exists(file_stream_or_path):
            print(f"Ficheiro não encontrado: {file_stream_or_path}")
            return ""
        with open(file_stream_or_path, 'rb') as f:
            file_stream = BytesIO(f.read())
    else: # Se já for um stream (BytesIO)
        file_stream = file_stream_or_path

    if ext == '.docx':
        return extrair_texto_docx(file_stream)
    elif ext == '.pdf':
        return extrair_texto_pdf(file_stream)
    elif ext == '.txt':
        try:
            # Volta ao início do stream para ler o conteúdo de texto
            file_stream.seek(0)
            return file_stream.read().decode('utf-8')
        except Exception as e:
            print(f"Erro ao ler TXT da memória: {e}")
            return ""
    return ""


# --- Função de Assistente IA (Networking) ---

def obter_resumo_ia(texto_fonte, api_key, tipo_fonte):
    """
    Envia um texto grande para a IA e pede um resumo focado em avaliação.
    A api_key é passada como argumento para evitar dependência direta de app.config.
    """
    if not texto_fonte or not texto_fonte.strip():
        return ""

    # O prompt solicita um resumo focado em conceitos úteis para gerar questões.
    prompt = f"""
    Aja como um assistente pedagógico. Resuma o seguinte texto de um(a) '{tipo_fonte}'.
    O seu resumo deve focar-se APENAS nos principais tópicos, conceitos, e factos que seriam úteis para criar uma questão de prova.
    Seja conciso. Responda apenas com o resumo.

    TEXTO-FONTE:
    ---
    {texto_fonte[:8000]} 
    ---
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60) # 60s para resumir
        response.raise_for_status()
        resumo = response.json()['candidates'][0]['content']['parts'][0]['text']
        return resumo.strip()
    except Exception as e:
        print(f"Erro ao resumir: {e}")
        return f"(Erro ao resumir {tipo_fonte})"

# --- CÁLCULO ACADÊMICO (NOVO) ---

def calcular_boletim_aluno(aluno_id):
    """
    Calcula a média do aluno separada por Unidade/Etapa.
    Retorna um dicionário com as médias de cada unidade e a média final global.
    Estrutura de retorno:
    {
        'detalhe': {
            '1ª Unidade': {'media': 7.5, 'soma_notas': 15, ...},
            '2ª Unidade': {'media': 8.0, 'soma_notas': 8, ...}
        },
        'media_final': 7.7
    }
    """
    # 1. Buscar todas as notas lançadas para o aluno
    # Fazemos um JOIN com Atividade para saber a qual Unidade a nota pertence
    presencas = db.session.query(Presenca).join(Atividade).filter(
        Presenca.id_aluno == aluno_id,
        Presenca.nota != None  # Ignora atividades sem nota lançada
    ).all()

    boletim = {}

    # 2. Agrupar notas por Unidade
    for p in presencas:
        # Pega a unidade da atividade (ou define 'Geral' se estiver vazio)
        unidade = p.atividade.unidade if p.atividade.unidade else 'Geral'
        
        # Pega o peso (se não tiver peso, assume 1.0)
        peso = p.atividade.peso if p.atividade.peso else 1.0
        
        # Pega a nota
        nota = p.nota
        
        if unidade not in boletim:
            boletim[unidade] = {
                'soma_notas_ponderadas': 0, 
                'soma_pesos': 0, 
                'media': 0
            }
        
        # Acumula para o cálculo da média ponderada DAQUELA unidade
        boletim[unidade]['soma_notas_ponderadas'] += (nota * peso)
        boletim[unidade]['soma_pesos'] += peso

    # 3. Calcular a Média de cada Unidade individualmente
    soma_medias_unidades = 0
    total_unidades_calculadas = 0

    for unidade, dados in boletim.items():
        if dados['soma_pesos'] > 0:
            # Fórmula: Soma (Nota * Peso) / Soma (Pesos)
            media_unidade = dados['soma_notas_ponderadas'] / dados['soma_pesos']
            
            # Arredonda para 1 casa decimal (ex: 7.56 vira 7.6)
            dados['media'] = round(media_unidade, 1)
            
            # Adiciona ao acumulador para a média final
            soma_medias_unidades += dados['media']
            total_unidades_calculadas += 1

    # 4. Calcular a Média Final Global (Média das Médias das Unidades)
    media_final = 0
    if total_unidades_calculadas > 0:
        media_final = soma_medias_unidades / total_unidades_calculadas
        media_final = round(media_final, 1)

    return {
        'detalhe': boletim,
        'media_final': media_final
    }