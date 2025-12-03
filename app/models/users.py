from app.extensions import db
from datetime import datetime, date

class Escola(db.Model):
    __tablename__ = 'escolas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.String(255), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email_contato = db.Column(db.String(120), nullable=True)
    
    # Relacionamentos
    usuarios = db.relationship('User', backref='escola', lazy=True)

    def __repr__(self):
        return f'<Escola {self.nome}>'


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) 
    
    # Controle de Acesso (Roles)
    is_professor = db.Column(db.Boolean, default=False)   # Alterado padrão para False
    is_student = db.Column(db.Boolean, default=False)     # NOVO: Identifica Aluno
    is_coordenador = db.Column(db.Boolean, default=False) # NOVO: Coordenador de Escola
    is_admin = db.Column(db.Boolean, default=False)      # Admin Geral do Sistema
    
    # Relacionamento com Escola (SaaS/Multi-Escola)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=True)
    
    # CAMPOS DE PERFIL
    email_contato = db.Column(db.String(120), nullable=True) 
    telefone = db.Column(db.String(20), nullable=True)
    foto_perfil_path = db.Column(db.String(255), nullable=True) 
    
    # Gênero para personalização de tema (Masculino/Feminino)
    genero = db.Column(db.String(20), default='Masculino') 
    
    # Relacionamentos
    lembretes = db.relationship('Lembrete', backref='autor', lazy=True, cascade='all, delete-orphan')
    turmas = db.relationship('Turma', backref='autor', lazy=True, cascade='all, delete-orphan')
    horarios = db.relationship('Horario', backref='autor', lazy=True, cascade='all, delete-orphan')
    entradas_diario = db.relationship('DiarioBordo', backref='autor_diario', lazy=True, cascade='all, delete-orphan', foreign_keys='DiarioBordo.id_user')
    notificacoes = db.relationship('Notificacao', backref='destinatario', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class Notificacao(db.Model):
    __tablename__ = 'notificacoes'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    texto = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=True) # Link opcional para redirecionamento
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)


class Habilidade(db.Model):
    __tablename__ = 'habilidades'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False) # Ex: EF08LP08
    descricao = db.Column(db.Text, nullable=False)
    area = db.Column(db.String(50)) # Ex: Linguagens, Matemática


class Lembrete(db.Model):
    __tablename__ = 'lembretes'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Ativo')
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Lembrete {self.id}>'
        

