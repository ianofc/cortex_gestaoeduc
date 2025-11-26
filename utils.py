# utils.py

import os
import requests 
import json     
from io import BytesIO
import docx

# Import condicional do PyPDF2, essencial para ler PDFs
try:
    from PyPDF2 import PdfReader
except ImportError:
    # Aviso para o desenvolvedor caso a biblioteca não esteja instalada
    print("AVISO: PyPDF2 não instalado. A leitura de PDF falhará. Instale com: pip install PyPDF2")
    PdfReader = None

# --- FUNÇÃO HELPER DE VALIDAÇÃO DE FICHEIROS (allowed_file) ---
# Adicionada para resolver o ImportError

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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
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