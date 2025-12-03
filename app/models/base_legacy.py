from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin 
from datetime import datetime, date 

db = SQLAlchemy() 

# --- TABELAS DE ASSOCIAÇÃO (Muitos-para-Muitos) ---

atividade_habilidade = db.Table('atividade_habilidade',
    db.Column('id_atividade', db.Integer, db.ForeignKey('atividades.id'), primary_key=True),
    db.Column('id_habilidade', db.Integer, db.ForeignKey('habilidades.id'), primary_key=True)
)

plano_habilidade = db.Table('plano_habilidade',
    db.Column('id_plano', db.Integer, db.ForeignKey('planos_de_aula.id'), primary_key=True),
    db.Column('id_habilidade', db.Integer, db.ForeignKey('habilidades.id'), primary_key=True)
)

# --- MODELOS PRINCIPAIS ---

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

class Lembrete(db.Model):
    __tablename__ = 'lembretes'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='Ativo')
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Lembrete {self.id}>'
        
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