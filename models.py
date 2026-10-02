from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = 'usuario'
    id       = db.Column(db.Integer, primary_key=True)
    nome     = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(150), unique=True, nullable=False)
    senha    = db.Column(db.String(200), nullable=False)
    foto      = db.Column(db.String(200), nullable=True)
    bio       = db.Column(db.String(300), nullable=True)
    cor_tema  = db.Column(db.String(20), nullable=True, default='laranja')
    token_redefinicao = db.Column(db.String(200), nullable=True, unique=True)
    token_expira_em = db.Column(db.DateTime, nullable=True)
    receitas  = db.relationship('Receita', backref='dono', lazy=True)
    favoritos = db.relationship('Favorito', backref='usuario', lazy=True)
    avaliacoes = db.relationship('Avaliacao', backref='usuario', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nome}>'


class Receita(db.Model):
    __tablename__ = 'receita'
    id            = db.Column(db.Integer, primary_key=True)
    nome          = db.Column(db.String(150), nullable=False)
    descricao     = db.Column(db.Text, nullable=False)
    ingredientes  = db.Column(db.Text, nullable=False)
    modo_preparo  = db.Column(db.Text, nullable=False)
    tempo_preparo = db.Column(db.String(50), nullable=False)
    tempo_minutos = db.Column(db.Integer, nullable=True)
    porcoes       = db.Column(db.String(50), nullable=False)
    categoria     = db.Column(db.String(50), nullable=False)
    dificuldade   = db.Column(db.String(20), nullable=True)
    foto          = db.Column(db.String(200), nullable=True)
    fixa          = db.Column(db.Boolean, default=False, nullable=False)
    usuario_id    = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    avaliacoes    = db.relationship('Avaliacao', backref='receita', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Receita {self.nome}>'


class Favorito(db.Model):
    __tablename__ = 'favorito'
    id         = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=False)


class Avaliacao(db.Model):
    __tablename__ = 'avaliacao'
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'receita_id', name='uq_avaliacao_usuario_receita'),
        db.CheckConstraint('nota >= 1 AND nota <= 5', name='ck_avaliacao_nota'),
    )
    id         = db.Column(db.Integer, primary_key=True)
    nota       = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=False)


class Comentario(db.Model):
    __tablename__ = 'comentario'
    id           = db.Column(db.Integer, primary_key=True)
    texto        = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    usuario_id   = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    receita_id   = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=False)
    resposta_de_id = db.Column(db.Integer, db.ForeignKey('comentario.id'), nullable=True)
    autor        = db.relationship('Usuario', backref='comentarios')
    receita      = db.relationship('Receita', backref='comentarios')
    comentario_pai = db.relationship(
        'Comentario',
        remote_side=[id],
        backref=db.backref('respostas', lazy=True)
    )
