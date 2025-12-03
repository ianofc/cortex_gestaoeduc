# app/services/grade_service.py
# Centraliza cálculos matemáticos de notas e médias.

def calcular_media_ponderada(notas_com_pesos):
    """
    Recebe lista de tuplas (nota, peso).
    Ex: [(8.0, 2), (5.0, 1)]
    Retorna a média ponderada.
    """
    soma_notas = 0
    soma_pesos = 0
    
    for nota, peso in notas_com_pesos:
        if nota is not None:
            p = peso if peso else 1
            soma_notas += nota * p
            soma_pesos += p
            
    if soma_pesos == 0:
        return 0.0
        
    return round(soma_notas / soma_pesos, 2)