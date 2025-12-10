# app/services/io_id.py
import requests
import uuid
from flask import current_app

class IOIDService:
    """
    Serviço para gerenciar a comunicação com o IO ID (IO LIFE).
    """
    
    # URL base da API do IO LIFE (defina isso no seu .env futuramente)
    API_URL = "https://api.iolife.com.br/v1/auth" 

    @staticmethod
    def register_user(username, email, password, role="student"):
        """
        Registra um usuário no IO ID e retorna o ID único (io_id).
        """
        payload = {
            "username": username,
            "email": email,
            "password": password,
            "service": "cortex_lumina", # Identifica que o registro veio do Cortex
            "role": role
        }

        try:
            # SIMULAÇÃO: Se não houver URL configurada ou para testes locais
            # No futuro, descomente a chamada requests.post abaixo
            if current_app.config.get('IO_ID_MOCK_MODE', True):
                print(f"[IO ID LOG] Criando usuário simulado para {email}")
                return {
                    "success": True,
                    "io_id": str(uuid.uuid4()), # Gera um UUID simulando o IO ID
                    "message": "Usuário criado no IO ID (Mock)"
                }

            # CHAMADA REAL (Descomentar quando tiver a API real)
            # response = requests.post(f"{IOIDService.API_URL}/register", json=payload)
            # response.raise_for_status()
            # return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"[IO ID ERROR] Falha ao conectar: {e}")
            return {"success": False, "message": "Erro de conexão com IO ID"}

    @staticmethod
    def login_user(email, password):
        """
        Verifica credenciais no IO ID.
        """
        # Lógica similar para login...
        pass