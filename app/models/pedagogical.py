from app.extensions import db
from datetime import datetime, date

# Tabelas de Associação
atividade_habilidade = db.Table('atividade_habilidade',
    db.Column('atividade_id', db.Integer, db.ForeignKey('atividades.id'), primary_key=True),
    db.Column('habilidade_id', db.Integer, db.ForeignKey('habilidades.id'), primary_key=True)
)

plano_habilidade = db.Table('plano_habilidade',
    db.Column('plano_id', db.Integer, db.ForeignKey('planos_de_aula.id'), primary_key=True),
    db.Column('habilidade_id', db.Integer, db.ForeignKey('habilidades.id'), primary_key=True)
)

class Atividade(db.Model):
    __tablename__ = 'atividades'
    id = db.Column(db.Integer, primary_key=True)
    id_turma = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=True) 
    titulo = db.Column(db.String(100))
    tipo = db.Column(db.String(50), default='Atividade') 
    peso = db.Column(db.Float) 
    valor = db.Column(db.Float, nullable=True) # Valor da nota se for diferente do peso
    unidade = db.Column(db.String(20), default='3ª Unidade') 
    data = db.Column(db.Date)
    descricao = db.Column(db.Text)
    nome_arquivo_anexo = db.Column(db.String(255), nullable=True)
    path_arquivo_anexo = db.Column(db.String(255), nullable=True)
    
    presencas = db.relationship('Presenca', backref='atividade', lazy=True, cascade='all, delete-orphan')
    habilidades = db.relationship('Habilidade', secondary=atividade_habilidade, backref='atividades')

    def __repr__(self):
        return f'<Atividade {self.titulo}>'


class Presenca(db.Model):
    __tablename__ = 'presencas'
    id = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('alunos.id'))
    id_atividade = db.Column(db.Integer, db.ForeignKey('atividades.id'))
    
    status = db.Column(db.String(20)) 
    participacao = db.Column(db.String(20)) 
    nota = db.Column(db.Float) 
    
    acertos = db.Column(db.Integer, nullable=True) 
    
    # CAMPO CRÍTICO: Garantido aqui para o cálculo em core.py
    desempenho = db.Column(db.Integer, nullable=True) # % estimada (0-100)
    situacao = db.Column(db.String(50))
    observacoes = db.Column(db.Text)

    # Relacionamento de volta para Aluno (feito via backref no Aluno)
    
    def __repr__(self):
        return f'<Presenca Aluno:{self.id_aluno} Ativ:{self.id_atividade}>'


class PlanoDeAula(db.Model):
    __tablename__ = 'planos_de_aula'
    id = db.Column(db.Integer, primary_key=True)
    id_turma = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    data_prevista = db.Column(db.Date, nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    
    conteudo = db.Column(db.Text, nullable=True)
    habilidades_bncc = db.Column(db.Text, nullable=True)
    
    habilidades_tags = db.relationship('Habilidade', secondary=plano_habilidade, backref='planos')
    
    objetivos = db.Column(db.Text, nullable=True)
    duracao = db.Column(db.Text, nullable=True)
    recursos = db.Column(db.Text, nullable=True)
    metodologia = db.Column(db.Text, nullable=True)
    avaliacao = db.Column(db.Text, nullable=True)
    referencias = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(50), nullable=False, default='Planejado')
    
    id_atividade_gerada = db.Column(db.Integer, db.ForeignKey('atividades.id'), nullable=True)
    atividade_gerada = db.relationship('Atividade', foreign_keys=[id_atividade_gerada])
    
    materiais = db.relationship('Material', backref='plano_de_aula', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<PlanoDeAula {self.titulo}>'


class Material(db.Model):
    __tablename__ = 'materiais'
    id = db.Column(db.Integer, primary_key=True)
    id_plano_aula = db.Column(db.Integer, db.ForeignKey('planos_de_aula.id'), nullable=False)
    nome_arquivo = db.Column(db.String(255), nullable=True)
    path_arquivo = db.Column(db.String(255), nullable=True)
    link_externo = db.Column(db.Text, nullable=True)
    nome_link = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Material {self.nome_arquivo or self.nome_link}>'


class DiarioBordo(db.Model):
    __tablename__ = 'diario_bordo'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    id_turma = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=True)
    data = db.Column(db.Date, nullable=False, default=date.today)
    anotacao = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(100), nullable=True)
    
    turma_diario = db.relationship('Turma', foreign_keys=[id_turma])
    nome_arquivo_anexo = db.Column(db.String(255), nullable=True)
    path_arquivo_anexo = db.Column(db.String(255), nullable=True)