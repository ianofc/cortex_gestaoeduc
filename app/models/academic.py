from app.extensions import db
from datetime import datetime, date

class Turma(db.Model):
    __tablename__ = 'turmas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    turno = db.Column(db.String(50)) 
    autor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    
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
    
    email_responsavel = db.Column(db.String(120), nullable=True)
    telefone_responsavel = db.Column(db.String(20), nullable=True)

    id_turma = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=True) 
    id_user_conta = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) 

    # --- ADICIONE ESTA LINHA ABAIXO PARA CORRIGIR O ERRO ---
    presencas = db.relationship('Presenca', backref='aluno', lazy=True, cascade='all, delete-orphan')
    # -------------------------------------------------------
    
    def __repr__(self):
        return f'<Aluno {self.nome}>'


class Horario(db.Model):
    __tablename__ = 'horarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, default="Horário Padrão")
    autor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ativo = db.Column(db.Boolean, default=True) 
    
    publico = db.Column(db.Boolean, default=False)
    
    blocos = db.relationship('BlocoAula', backref='horario', lazy=True, cascade='all, delete-orphan')


class BlocoAula(db.Model):
    __tablename__ = 'blocos_aula'
    id = db.Column(db.Integer, primary_key=True)
    id_horario = db.Column(db.Integer, db.ForeignKey('horarios.id'), nullable=False)
    id_turma = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=True)
    turma_bloco = db.relationship('Turma', foreign_keys=[id_turma])
    
    dia_semana = db.Column(db.Integer, nullable=False) 
    posicao_aula = db.Column(db.Integer, nullable=False) 
    texto_horario = db.Column(db.String(50), nullable=True) 
    texto_alternativo = db.Column(db.String(100), nullable=True)