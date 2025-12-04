# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, DateField, FloatField, IntegerField, PasswordField, BooleanField, RadioField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange, EqualTo, ValidationError, Optional, Email

from flask_wtf.file import FileField, FileAllowed

from wtforms_sqlalchemy.fields import QuerySelectField

# CORREÇÃO: Importar de app.models em vez de base_legacy
from app.models import Turma, Aluno, Atividade, db, User, Escola
from datetime import date

# --- FORMULÁRIOS DE AUTENTICAÇÃO ---
class RegisterForm(FlaskForm):
    username = StringField('Nome de Usuário', 
                           validators=[DataRequired(), Length(min=4, max=80)])
    
    email = StringField('Email', 
                        validators=[DataRequired(), Email(), Length(max=120)])
    
    tipo_conta = RadioField('Eu sou:', choices=[('professor', 'Professor'), ('aluno', 'Aluno')], default='professor', validators=[DataRequired()])
    escola = SelectField('Escola', coerce=int, validators=[Optional()])

    password = PasswordField('Senha', 
                             validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', 
                                     validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Este nome de usuário já existe. Por favor, escolha outro.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email_contato=email.data).first()
        if user:
            raise ValidationError('Este email já está cadastrado.')

class LoginForm(FlaskForm):
    login = StringField('Email ou Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Manter conectado')
    submit = SubmitField('Acessar Sistema')

# --- FUNÇÃO QUERY ---
def turmas_query():
    return Turma.query.order_by(Turma.nome).all()

# --- FORMULÁRIOS DE CADASTRO ---

class TurmaForm(FlaskForm):
    nome = StringField('Nome da Turma', validators=[DataRequired(), Length(max=100)])
    descricao = TextAreaField('Descrição (Ex: Perfil da turma, nível, curso)')
    
    turno = SelectField('Turno', choices=[
        ('Matutino', 'Matutino'), 
        ('Vespertino', 'Vespertino'), 
        ('Noturno', 'Noturno'), 
        ('Integral', 'Integral')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Salvar Turma')

class AlunoForm(FlaskForm):
    nome = StringField('Nome do Aluno', validators=[DataRequired(), Length(max=100)])
    matricula = StringField('Matrícula', validators=[Length(max=50)])
    submit = SubmitField('Salvar Aluno')

class EditarAlunoForm(FlaskForm):
    nome = StringField('Nome Completo do Aluno', validators=[DataRequired(), Length(max=100)])
    matricula = StringField('Matrícula', validators=[Length(max=50)])
    turma = QuerySelectField(
        'Turma', 
        query_factory=turmas_query, 
        get_label='nome',
        allow_blank=True,
        blank_text='-- Nenhuma Turma --'
    )
    submit = SubmitField('Atualizar Dados do Aluno')

# --- FORMULÁRIO DE ATIVIDADE ---
class AtividadeForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=100)])
    
    # SELETOR DE UNIDADE (NOVO)
    unidade = SelectField('Unidade Escolar', choices=[
        ('1ª Unidade', '1ª Unidade'),
        ('2ª Unidade', '2ª Unidade'),
        ('3ª Unidade', '3ª Unidade'),
        ('4ª Unidade', '4ª Unidade'),
        ('Recuperação', 'Recuperação'),
        ('Exame Final', 'Exame Final')  
    ], default='3ª Unidade', validators=[DataRequired()])

    TIPOS_ATIVIDADE = [
        ('Atividade', 'Exercícios / Tarefas'),
        ('Prova', 'Prova / Avaliação'),
        ('Seminario', 'Seminário / Apresentação'),
        ('Trabalho', 'Trabalho Escrito / Projeto'),
        ('Visto', 'Visto no Caderno'),
        ('Participacao', 'Participação')
    ]
    tipo = SelectField('Tipo de Atividade', choices=TIPOS_ATIVIDADE, validators=[DataRequired()])

    data = DateField('Data', default=date.today, validators=[DataRequired()])
    
    valor_total = FloatField('Valor Total da Atividade (Pontos)', 
                      validators=[InputRequired(message="O valor total é obrigatório."), 
                                  NumberRange(min=0.0, max=10.0, message="O valor deve estar entre 0.0 e 10.0.")], 
                      default=10.0)
    
    num_questoes = IntegerField('Número de Questões (Obrigatório para Prova)', 
                                 validators=[Optional(), NumberRange(min=1)], 
                                 render_kw={'placeholder': 'Obrigatório para Provas'})
    
    descricao = TextAreaField('Descrição (ou questões geradas por IA)')
    
    arquivo_anexo = FileField('Anexar Ficheiro da Atividade (.pdf, .docx, .txt)', validators=[
        FileAllowed(['pdf', 'docx', 'txt'], 'Apenas .pdf, .docx ou .txt!'),
        Optional()
    ])
    
    submit = SubmitField('Salvar Atividade')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        if self.tipo.data == 'Prova':
            if not self.num_questoes.data or self.num_questoes.data < 1:
                self.num_questoes.errors.append('Para Provas, o Número de Questões é obrigatório e deve ser no mínimo 1.')
                return False
        
        return True

# --- FORMULÁRIO DE PRESENÇA ---
class PresencaForm(FlaskForm):
    STATUS_CHOICES = [('Presente', 'Presente'), ('Ausente', 'Ausente'), ('Justificado', 'Justificado')]
    PARTICIPACAO_CHOICES = [('Sim', 'Sim'), ('Parcial', 'Parcial'), ('Não', 'Não')]
    SITUACAO_CHOICES = [('Excelente', 'Excelente'), ('Bom', 'Bom'), ('Reforço', 'Reforço'), ('Insatisfatório', 'Insatisfatório')]
    
    status = SelectField('Status', choices=STATUS_CHOICES, validators=[DataRequired()])
    participacao = SelectField('Participação', choices=PARTICIPACAO_CHOICES, validators=[DataRequired()])
    
    acertos = IntegerField('Acertos (Preencha para calcular nota)', 
                           validators=[Optional(), NumberRange(min=0)], 
                           render_kw={'placeholder': 'Ex: 6'})
                           
    nota = FloatField('Nota Obtida (Manual)', 
                      validators=[Optional(), NumberRange(min=0.0, max=10.0)], 
                      default=0.0)
    
    desempenho = IntegerField('Desempenho Estimado (%)', 
                              validators=[InputRequired(message="Por favor, insira um desempenho (pode ser 0)."), 
                                          NumberRange(min=0, max=100)], 
                              default=0)
    
    situacao = SelectField('Situação', choices=SITUACAO_CHOICES, validators=[DataRequired()])
    observacoes = TextAreaField('Observações')
    submit = SubmitField('Registrar Presença')
    
    def validate_on_submit(self, extra_validators=None):
        if not super().validate_on_submit(extra_validators):
            return False
            
        if self.acertos.data is None and self.nota.data is None:
            self.nota.errors.append('É necessário preencher a Nota Manual ou o campo Acertos para registrar a pontuação.')
            return False
            
        return True


class PlanoDeAulaForm(FlaskForm):
    data_prevista = DateField('Data Prevista', default=date.today, validators=[DataRequired()])
    duracao = StringField('Duração (ex: 2 aulas, 50 min)')
    titulo = StringField('Tema da Aula', validators=[DataRequired(), Length(max=100)])
    conteudo = TextAreaField('Conteúdo (Tópicos a abordar)', render_kw={"rows": 4})
    habilidades_bncc = StringField('Habilidades BNCC (ex: EF08LP08)')
    objetivos = TextAreaField('Objetivos de Aprendizagem', render_kw={"rows": 3})
    metodologia = TextAreaField('Metodologia (ex: Aula expositiva, debate)', render_kw={"rows": 3})
    recursos = TextAreaField('Recursos Didáticos (ex: Projetor, livro)', render_kw={"rows": 2})
    avaliacao = TextAreaField('Avaliação (ex: Exercícios, participação)', render_kw={"rows": 2})
    referencias = TextAreaField('Referências', render_kw={"rows": 2})
    submit = SubmitField('Salvar Plano de Aula')

class LembreteForm(FlaskForm):
    texto = TextAreaField('Novo Lembrete', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Salvar')

class MaterialForm(FlaskForm):
    arquivo_upload = FileField('Enviar Ficheiro', validators=[
        FileAllowed(['pdf', 'docx', 'pptx', 'jpg', 'png', 'txt', 'zip', 'xls', 'xlsx'], 'Tipo de ficheiro não suportado!')
    ])
    nome_link = StringField('Nome do Link')
    link_externo = StringField('Link Externo (http://...)')
    submit_material = SubmitField('Adicionar Material')

class DiarioForm(FlaskForm):
    anotacao = TextAreaField('Anotação', validators=[DataRequired(), Length(min=2)])
    data = DateField('Data', default=date.today, validators=[DataRequired()])
    
    arquivo_anexo = FileField('Anexar Atividade Aplicada (.pdf, .docx, .txt)', validators=[
        FileAllowed(['pdf', 'docx', 'txt'], 'Apenas .pdf, .docx ou .txt!'),
        Optional()
    ])

    submit = SubmitField('Salvar no Diário')

# --- FORMULÁRIOS DE PERFIL ---
class UserProfileForm(FlaskForm):
    username = StringField('Nome de Usuário', 
                           validators=[DataRequired(), Length(min=4, max=80)])
    
    email_contato = StringField('Email de Contato', 
                                validators=[Optional(), Length(max=120), Email()])
    telefone = StringField('Telefone/WhatsApp', 
                           validators=[Optional(), Length(max=20)])
                           
    foto_perfil = FileField('Foto de Perfil (.jpg, .png)', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Apenas imagens JPG ou PNG são permitidas!'),
        Optional()
    ])
    
    genero = SelectField('Tema do Sistema (Gênero)', choices=[
        ('Masculino', 'Masculino (Azul/Roxo)'), 
        ('Feminino', 'Feminino (Rosa/Vermelho)')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Salvar Perfil')

    def __init__(self, original_username, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Este nome de usuário já está em uso.')
            
# --- FORMULÁRIOS NOVOS (SaaS / ADMIN) ---

class EscolaForm(FlaskForm):
    nome = StringField('Nome da Escola', validators=[DataRequired(), Length(max=150)])
    endereco = StringField('Endereço', validators=[Length(max=255)])
    telefone = StringField('Telefone', validators=[Length(max=20)])
    email_contato = StringField('Email de Contato', validators=[Email(), Length(max=120)])
    submit = SubmitField('Cadastrar Escola')

class CoordenadorForm(FlaskForm):
    nome = StringField('Nome (Usuário)', validators=[DataRequired(), Length(max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    escola_id = SelectField('Escola', coerce=int) 
    submit = SubmitField('Cadastrar Coordenador')

class ProfessorForm(FlaskForm):
    nome = StringField('Nome (Usuário)', validators=[DataRequired(), Length(max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Cadastrar Professor')