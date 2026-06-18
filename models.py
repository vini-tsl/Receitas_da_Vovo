from flask_sqlalchemy import SQLAlchemy

# Criamos o objeto db aqui.
# Ele vai ser usado tanto aqui no models.py quanto no app.py
db = SQLAlchemy()


class Usuario(db.Model):
    """
    Tabela que guarda os usuários do sistema.
    Cada linha é uma pessoa cadastrada.
    """
    __tablename__ = 'usuario'

    id       = db.Column(db.Integer, primary_key=True)   # Número único de cada usuário
    nome     = db.Column(db.String(100), nullable=False)  # Nome completo
    email    = db.Column(db.String(150), unique=True, nullable=False)  # Email (único no sistema)
    senha    = db.Column(db.String(200), nullable=False)  # Senha já criptografada (hash)

    # Relacionamento: um usuário pode ter várias receitas
    # "backref='dono'" permite acessar o dono de uma receita com: receita.dono
    receitas  = db.relationship('Receita', backref='dono', lazy=True)

    # Relacionamento: um usuário pode ter vários favoritos
    favoritos = db.relationship('Favorito', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.nome}>'


class Receita(db.Model):
    """
    Tabela que guarda todas as receitas do sistema.
    Cada linha é uma receita diferente.
    """
    __tablename__ = 'receita'

    id           = db.Column(db.Integer, primary_key=True)
    nome         = db.Column(db.String(150), nullable=False)       # Nome da receita
    descricao    = db.Column(db.Text, nullable=False)               # Descrição curta
    ingredientes = db.Column(db.Text, nullable=False)               # Lista de ingredientes
    modo_preparo = db.Column(db.Text, nullable=False)               # Passo a passo
    tempo_preparo= db.Column(db.String(50), nullable=False)         # Ex: "45 minutos"
    porcoes      = db.Column(db.String(50), nullable=False)         # Ex: "4 pessoas"
    categoria    = db.Column(db.String(50), nullable=False)         # Ex: doce, salgado...
    foto         = db.Column(db.String(200), nullable=True)         # Nome do arquivo da foto

    # Se fixa=True, é uma receita da vovó: ninguém pode editar ou excluir
    fixa         = db.Column(db.Boolean, default=False, nullable=False)

    # Chave estrangeira: guarda o id do usuário que criou a receita
    # nullable=True porque receitas fixas não têm dono
    usuario_id   = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    def __repr__(self):
        return f'<Receita {self.nome}>'


class Favorito(db.Model):
    """
    Tabela que guarda as receitas favoritas de cada usuário.
    Cada linha representa um usuário que favoritou uma receita.
    Ex: usuario_id=2 e receita_id=5 significa que o usuário 2 favoritou a receita 5.
    """
    __tablename__ = 'favorito'

    id         = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    receita_id = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=False)

    def __repr__(self):
        return f'<Favorito usuario={self.usuario_id} receita={self.receita_id}>'


class Comentario(db.Model):
    """
    Tabela que guarda os comentários feitos nas receitas.
    Cada linha é um comentário de um usuário em uma receita.
    """
    __tablename__ = 'comentario'

    id           = db.Column(db.Integer, primary_key=True)
    texto        = db.Column(db.Text, nullable=False)                         # O texto do comentário
    data_criacao = db.Column(db.DateTime, default=db.func.now(), nullable=False)  # Data e hora automáticas
    usuario_id   = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Quem comentou
    receita_id   = db.Column(db.Integer, db.ForeignKey('receita.id'), nullable=False)  # Em qual receita

    # Atalhos para acessar os dados relacionados
    # Ex: comentario.autor.nome  →  retorna o nome de quem comentou
    autor   = db.relationship('Usuario', backref='comentarios')
    receita = db.relationship('Receita', backref='comentarios')

    def __repr__(self):
        return f'<Comentario de usuario={self.usuario_id} na receita={self.receita_id}>'
