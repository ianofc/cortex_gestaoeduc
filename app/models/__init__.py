from .users import User, Role, Escola, Notificacao, Habilidade, Lembrete
from .academic import Turma, Aluno, Horario, BlocoAula
from .pedagogical import Atividade, Presenca, PlanoDeAula, Material, DiarioBordo
from .financial import * # Deixamos o financeiro genérico por simplicidade
from app.extensions import db