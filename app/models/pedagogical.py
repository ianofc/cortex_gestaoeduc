from app.extensions import db
from datetime import datetime, date

class Atividade(db.Model):
    __tablename__ = 'atividades'
    id = db.Column(db.Integer, primary_key=True)
    id_turma = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=True) 
    titulo = db.Column(db.String(100))
    
    # Novos campos de classificação e valor
    tipo = db.Column(db.String(50), default='Atividade') # Ex: Prova, Trabalho, Caderno
    peso = db.Column(db.Float) # Representa o valor total (ex: 10.0)
    
    # NOVO CAMPO: UNIDADE
    unidade = db.Column(db.String(20), default='3ª Unidade') 
    
    data = db.Column(db.Date)
    descricao = db.Column(db.Text)
    
    # Anexos
    nome_arquivo_anexo = db.Column(db.String(255), nullable=True)
    path_arquivo_anexo = db.Column(db.String(255), nullable=True)
    
    # Relacionamentos
    presencas = db.relationship('Presenca', backref='atividade', lazy=True, cascade='all, delete-orphan')
    habilidades = db.relationship('Habilidade', secondary=atividade_habilidade, backref='atividades')

    def __repr__(self):
        return f'<Atividade {self.titulo}>'


class PlanoDeAula(db.Model):
    __tablename__ = 'planos_de_aula'
    id = db.Column(db.Integer, primary_key=True)
    id_turma = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    data_prevista = db.Column(db.Date, nullable=False)
    titulo = db.Column(db.String(100), nullable=False)
    
    conteudo = db.Column(db.Text, nullable=True)
    habilidades_bncc = db.Column(db.Text, nullable=True) # Mantido para texto livre/códigos simples
    
    # Novo sistema de tags para habilidades
    habilidades_tags = db.relationship('Habilidade', secondary=plano_habilidade, backref='planos')
    
    objetivos = db.Column(db.Text, nullable=True)
    duracao = db.Column(db.Text, nullable=True)
    recursos = db.Column(db.Text, nullable=True)
    metodologia = db.Column(db.Text, nullable=True)
    avaliacao = db.Column(db.Text, nullable=True)
    referencias = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(50), nullable=False, default='Planejado')
    
    # Ligação com a atividade criada a partir deste plano
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
    
    turma_diario = db.relationship('Turma', foreign_keys=[id_turma])
    nome_arquivo_anexo = db.Column(db.String(255), nullable=True)
    path_arquivo_anexo = db.Column(db.String(255), nullable=True)
