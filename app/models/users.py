from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship('User', backref='role', lazy=True)

    def __repr__(self):
        return f'<Role {self.name}>'

class Escola(db.Model):
    __tablename__ = 'escolas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.String(255), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email_contato = db.Column(db.String(120), nullable=True)
    tipo = db.Column(db.String(50), default='privada') 
    
    usuarios = db.relationship('User', backref='escola', lazy=True)

    def __repr__(self):
        return f'<Escola {self.nome}>'

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False) 
    nome = db.Column(db.String(150), nullable=True)
    matricula = db.Column(db.String(50), unique=True, nullable=True)
    
    # --- NOVO CAMPO: DATA DE NASCIMENTO (PARA TODOS) ---
    data_nascimento = db.Column(db.Date, nullable=True)
    # ----------------------------------------------------
    
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=True)
    
    telefone = db.Column(db.String(20), nullable=True)
    foto_perfil_path = db.Column(db.String(255), nullable=True) 
    genero = db.Column(db.String(20), default='Masculino') 
    
    lembretes = db.relationship('Lembrete', backref='autor', lazy=True, cascade='all, delete-orphan') 
    turmas = db.relationship('Turma', backref='turma_autor_rel', lazy=True, cascade='all, delete-orphan') 
    horarios = db.relationship('Horario', backref='horario_autor_rel', lazy=True, cascade='all, delete-orphan')
    
    notificacoes = db.relationship('Notificacao', backref='destinatario', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'

    def has_role(self, role_name):
        return self.role and self.role.name == role_name

class Notificacao(db.Model):
    __tablename__ = 'notificacoes'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    texto = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255), nullable=True)
    lida = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

class Habilidade(db.Model):
    __tablename__ = 'habilidades'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    area = db.Column(db.String(50))

class Lembrete(db.Model):
    __tablename__ = 'lembretes'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Ativo')
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Lembrete {self.id}>'