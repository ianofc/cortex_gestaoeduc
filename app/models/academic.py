from app.extensions import db
from datetime import datetime, date

class Turma(db.Model):
    __tablename__ = 'turmas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    turno = db.Column(db.String(50)) # Ex: Matutino, Vespertino, Noturno
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    
    alunos = db.relationship('Aluno', backref='turma', lazy=True)
    atividades = db.relationship('Atividade', backref='turma', lazy=True, cascade='all, delete-orphan')
    planos_de_aula = db.relationship('PlanoDeAula', backref='turma', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Turma {self.nome}>'


class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    matricula = db.Column(db.String(50))
    data_cadastro = db.Column(db.Date, default=date.today)
    id_turma = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=True) 
    
    # Portal do Aluno: Link para a conta de usuário
    id_user_conta = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 

    presencas = db.relationship('Presenca', backref='aluno', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Aluno {self.nome}>'


class Presenca(db.Model):
    __tablename__ = 'presencas'
    id = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('alunos.id'))
    id_atividade = db.Column(db.Integer, db.ForeignKey('atividades.id'))
    
    status = db.Column(db.String(20)) # Presente, Ausente, Justificado
    participacao = db.Column(db.String(20)) 
    nota = db.Column(db.Float) # Nota final calculada ou manual
    
    acertos = db.Column(db.Integer, nullable=True) # NOVO: Número de questões corretas (Para cálculo automático)
    
    desempenho = db.Column(db.Integer) # % estimada
    situacao = db.Column(db.String(50))
    observacoes = db.Column(db.Text)


class Horario(db.Model):
    __tablename__ = 'horarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, default="Horário Padrão")
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True) 
    blocos = db.relationship('BlocoAula', backref='horario', lazy=True, cascade='all, delete-orphan')


class BlocoAula(db.Model):
    __tablename__ = 'blocos_aula'
    id = db.Column(db.Integer, primary_key=True)
    id_horario = db.Column(db.Integer, db.ForeignKey('horarios.id'), nullable=False)
    id_turma = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=True)
    turma_bloco = db.relationship('Turma', foreign_keys=[id_turma])
    
    dia_semana = db.Column(db.Integer, nullable=False) # 0=Segunda, 4=Sexta
    posicao_aula = db.Column(db.Integer, nullable=False) # 1 a 5 (ou mais)
    texto_horario = db.Column(db.String(50), nullable=True) # Ex: "13:10"
    texto_alternativo = db.Column(db.String(100), nullable=True) # Ex: "Reunião", "Planejamento"


