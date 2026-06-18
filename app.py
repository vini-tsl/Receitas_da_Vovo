import os
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, Usuario, Receita, Favorito, Comentario

# ─────────────────────────────────────────
#  CONFIGURAÇÃO DO APP
# ─────────────────────────────────────────
app = Flask(__name__)

app.secret_key = '213SA210319KWIAOX0291'  # Necessário para usar sessões

# Diz onde fica o banco de dados (pasta instance/)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///receitas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração de upload de fotos
UPLOAD_FOLDER = os.path.join('static', 'uploads')
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Liga o banco de dados ao app
db.init_app(app)


# ─────────────────────────────────────────
#  FUNÇÕES AUXILIARES
# ─────────────────────────────────────────
def extensao_permitida(nome_arquivo):
    """Verifica se o arquivo enviado tem uma extensão válida de imagem."""
    return ('.' in nome_arquivo and
            nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS)


def usuario_logado():
    """Retorna True se existe um usuário na sessão (ou seja, está logado)."""
    return 'usuario_id' in session


def popular_banco():
    """
    Adiciona receitas fixas (da vovó) ao banco quando ele é criado pela primeira vez.
    Só executa se ainda não houver receitas fixas cadastradas.
    """
    if Receita.query.filter_by(fixa=True).first():
        return  # Já tem receitas fixas, não precisa cadastrar de novo

    receitas_da_vovo = [
        Receita(
            nome='Bolo de Cenoura da Vovó',
            descricao='O clássico bolo de cenoura com cobertura de chocolate derretido, receita de família.',
            ingredientes='3 cenouras médias\n3 ovos\n1 xícara de óleo\n2 xícaras de açúcar\n2 xícaras de farinha de trigo\n1 colher de sopa de fermento em pó\n\nCobertura:\n4 colheres de sopa de chocolate em pó\n4 colheres de sopa de açúcar\n1 colher de sopa de manteiga\n5 colheres de sopa de leite',
            modo_preparo='1. Preaqueça o forno a 180°C e unte uma forma.\n2. No liquidificador, bata as cenouras, os ovos e o óleo até ficar homogêneo.\n3. Numa tigela, misture o açúcar, a farinha e o fermento.\n4. Junte a mistura do liquidificador aos ingredientes secos e mexa bem.\n5. Despeje na forma e asse por 35 a 40 minutos.\n6. Para a cobertura, misture tudo numa panela e leve ao fogo até engrossar.\n7. Despeje a cobertura quente sobre o bolo ainda na forma.',
            tempo_preparo='50 minutos',
            porcoes='10 fatias',
            categoria='Doce',
            foto='bolo-de-cenoura.png',
            fixa=True,
            usuario_id=None
        ),
        Receita(
            nome='Frango Assado de Domingo',
            descricao='Frango suculento temperado de véspera, assado lentamente até ficar dourado.',
            ingredientes='1 frango inteiro (cerca de 2kg)\n4 dentes de alho amassados\n1 limão (suco)\n1 colher de sopa de sal\n1 colher de chá de pimenta-do-reino\n1 colher de chá de páprica\n2 colheres de sopa de azeite\n1 ramo de alecrim (opcional)',
            modo_preparo='1. Na véspera, misture o alho, o suco de limão, o sal, a pimenta, a páprica e o azeite.\n2. Esfregue bem esse tempero por todo o frango, por dentro e por fora.\n3. Deixe na geladeira coberto por pelo menos 8 horas.\n4. No dia, preaqueça o forno a 200°C.\n5. Coloque o frango numa assadeira e cubra com papel alumínio.\n6. Asse por 1 hora coberto, depois retire o papel e deixe dourar por mais 30 minutos.',
            tempo_preparo='1h 30min (+ 8h de tempero)',
            porcoes='6 pessoas',
            categoria='Salgado',
            foto='frango-assado.png',
            fixa=True,
            usuario_id=None
        ),
        Receita(
            nome='Arroz Doce Cremoso',
            descricao='Sobremesa tradicional brasileira, cremosa e perfumada com canela.',
            ingredientes='1 xícara de arroz\n1 litro de leite\n1 lata de leite condensado\n2 paus de canela\n3 cravos-da-índia\nCanela em pó para polvilhar',
            modo_preparo='1. Cozinhe o arroz com 2 xícaras de água e os paus de canela e cravo até absorver toda a água.\n2. Adicione o leite e o leite condensado ao arroz cozido.\n3. Mexa em fogo médio por cerca de 20 minutos até engrossar e ficar cremoso.\n4. Retire os paus de canela e os cravos.\n5. Despeje em tigelas ou numa travessa.\n6. Polvilhe canela em pó por cima e deixe esfriar antes de servir.',
            tempo_preparo='40 minutos',
            porcoes='8 porções',
            categoria='Sobremesa',
            foto='arroz-doce.png',
            fixa=True,
            usuario_id=None
        ),
    ]

    db.session.add_all(receitas_da_vovo)
    db.session.commit()
    print('Receitas cadastradas!')


# ─────────────────────────────────────────
#  ROTAS DE AUTENTICAÇÃO
# ─────────────────────────────────────────
@app.route('/')
def inicio():
    """Redireciona para login se não estiver logado, ou para a página principal."""
    if usuario_logado():
        return redirect(url_for('index'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Tela de login. GET mostra o formulário, POST processa os dados."""
    if usuario_logado():
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')

        # Valida campos obrigatórios
        if not email or not senha:
            flash('Preencha todos os campos.', 'erro')
            return render_template('login.html')

        # Busca o usuário pelo email
        usuario = Usuario.query.filter_by(email=email).first()

        # Verifica se o usuário existe e a senha está correta
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            flash(f'Bem-vindo(a), {usuario.nome}! 👋', 'sucesso')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'erro')

    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Tela de cadastro de novo usuário."""
    if usuario_logado():
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome  = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        senha2 = request.form.get('senha2', '')

        # Validações
        if not nome or not email or not senha or not senha2:
            flash('Preencha todos os campos.', 'erro')
            return render_template('cadastro.html')

        if senha != senha2:
            flash('As senhas não coincidem.', 'erro')
            return render_template('cadastro.html')

        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'erro')
            return render_template('cadastro.html')

        # Verifica se o email já está cadastrado
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'erro')
            return render_template('cadastro.html')

        # Cria o novo usuário com a senha criptografada
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha)  # Nunca salva a senha direta!
        )
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça seu login.', 'sucesso')
        return redirect(url_for('login'))

    return render_template('cadastro.html')


@app.route('/logout')
def logout():
    """Remove os dados da sessão e redireciona para o login."""
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))


# ─────────────────────────────────────────
#  ROTAS DAS RECEITAS
# ─────────────────────────────────────────
@app.route('/receitas')
def index():
    """Página principal: lista todas as receitas com busca por nome."""
    if not usuario_logado():
        return redirect(url_for('login'))

    busca = request.args.get('busca', '').strip()

    if busca:
        # LIKE '%termo%' busca o texto em qualquer parte do nome
        receitas = Receita.query.filter(
            Receita.nome.ilike(f'%{busca}%')
        ).order_by(Receita.fixa.desc(), Receita.nome).all()
    else:
        receitas = Receita.query.order_by(Receita.fixa.desc(), Receita.nome).all()

    return render_template('index.html', receitas=receitas, busca=busca)


@app.route('/receita/<int:id>')
def ver_receita(id):
    """Página de detalhes de uma receita."""
    if not usuario_logado():
        return redirect(url_for('login'))

    receita = Receita.query.get_or_404(id)

    # Verifica se o usuário logado já favoritou esta receita
    favoritado = Favorito.query.filter_by(
        usuario_id=session['usuario_id'],
        receita_id=id
    ).first() is not None

    return render_template('receita.html', receita=receita, favoritado=favoritado)


@app.route('/receita/nova', methods=['GET', 'POST'])
def nova_receita():
    """Formulário para adicionar uma nova receita."""
    if not usuario_logado():
        return redirect(url_for('login'))

    if request.method == 'POST':
        nome         = request.form.get('nome', '').strip()
        descricao    = request.form.get('descricao', '').strip()
        ingredientes = request.form.get('ingredientes', '').strip()
        modo_preparo = request.form.get('modo_preparo', '').strip()
        tempo_preparo= request.form.get('tempo_preparo', '').strip()
        porcoes      = request.form.get('porcoes', '').strip()
        categoria    = request.form.get('categoria', '').strip()

        if not all([nome, descricao, ingredientes, modo_preparo, tempo_preparo, porcoes, categoria]):
            flash('Preencha todos os campos obrigatórios.', 'erro')
            return render_template('form_receita.html', receita=None)

        # Processa o upload da foto
        nome_foto = None
        foto = request.files.get('foto')
        if foto and foto.filename and extensao_permitida(foto.filename):
            nome_seguro = secure_filename(foto.filename)
            # Adiciona o id da sessão para evitar conflito de nomes
            nome_foto = f"{session['usuario_id']}_{nome_seguro}"
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_foto))

        nova = Receita(
            nome=nome,
            descricao=descricao,
            ingredientes=ingredientes,
            modo_preparo=modo_preparo,
            tempo_preparo=tempo_preparo,
            porcoes=porcoes,
            categoria=categoria,
            foto=nome_foto,
            fixa=False,
            usuario_id=session['usuario_id']
        )
        db.session.add(nova)
        db.session.commit()

        flash('Receita adicionada com sucesso! 🍽️', 'sucesso')
        return redirect(url_for('index'))

    return render_template('form_receita.html', receita=None)


@app.route('/receita/editar/<int:id>', methods=['GET', 'POST'])
def editar_receita(id):
    """Formulário para editar uma receita existente."""
    if not usuario_logado():
        return redirect(url_for('login'))

    receita = Receita.query.get_or_404(id)

    # Bloqueia edição de receitas fixas ou de outros usuários
    if receita.fixa or receita.usuario_id != session['usuario_id']:
        flash('Você não tem permissão para editar esta receita.', 'erro')
        return redirect(url_for('index'))

    if request.method == 'POST':
        receita.nome         = request.form.get('nome', '').strip()
        receita.descricao    = request.form.get('descricao', '').strip()
        receita.ingredientes = request.form.get('ingredientes', '').strip()
        receita.modo_preparo = request.form.get('modo_preparo', '').strip()
        receita.tempo_preparo= request.form.get('tempo_preparo', '').strip()
        receita.porcoes      = request.form.get('porcoes', '').strip()
        receita.categoria    = request.form.get('categoria', '').strip()

        if not all([receita.nome, receita.descricao, receita.ingredientes,
                    receita.modo_preparo, receita.tempo_preparo,
                    receita.porcoes, receita.categoria]):
            flash('Preencha todos os campos obrigatórios.', 'erro')
            return render_template('form_receita.html', receita=receita)

        # Atualiza foto se uma nova foi enviada
        foto = request.files.get('foto')
        if foto and foto.filename and extensao_permitida(foto.filename):
            # Remove a foto antiga se existir
            if receita.foto:
                caminho_antigo = os.path.join(app.config['UPLOAD_FOLDER'], receita.foto)
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)

            nome_seguro = secure_filename(foto.filename)
            nome_foto = f"{session['usuario_id']}_{nome_seguro}"
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_foto))
            receita.foto = nome_foto

        db.session.commit()
        flash('Receita atualizada com sucesso! ✏️', 'sucesso')
        return redirect(url_for('ver_receita', id=receita.id))

    return render_template('form_receita.html', receita=receita)


@app.route('/receita/excluir/<int:id>', methods=['POST'])
def excluir_receita(id):
    """Exclui uma receita. Só o dono pode excluir."""
    if not usuario_logado():
        return redirect(url_for('login'))

    receita = Receita.query.get_or_404(id)

    if receita.fixa or receita.usuario_id != session['usuario_id']:
        flash('Você não tem permissão para excluir esta receita.', 'erro')
        return redirect(url_for('index'))

    # Remove a foto do disco se existir
    if receita.foto:
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], receita.foto)
        if os.path.exists(caminho):
            os.remove(caminho)

    db.session.delete(receita)
    db.session.commit()

    flash('Receita excluída.', 'info')
    return redirect(url_for('index'))


# ─────────────────────────────────────────
#  ROTAS DE FAVORITOS
# ─────────────────────────────────────────
@app.route('/favoritar/<int:id>', methods=['POST'])
def favoritar(id):
    """Adiciona ou remove uma receita dos favoritos do usuário logado."""
    if not usuario_logado():
        return redirect(url_for('login'))

    receita = Receita.query.get_or_404(id)

    # Verifica se já existe esse favorito no banco
    ja_favoritou = Favorito.query.filter_by(
        usuario_id=session['usuario_id'],
        receita_id=receita.id
    ).first()

    if ja_favoritou:
        # Se já favoritou, remove (desfavorita)
        db.session.delete(ja_favoritou)
        db.session.commit()
        flash('Receita removida dos favoritos.', 'info')
    else:
        # Se ainda não favoritou, adiciona
        novo_favorito = Favorito(
            usuario_id=session['usuario_id'],
            receita_id=receita.id
        )
        db.session.add(novo_favorito)
        db.session.commit()
        flash('Receita adicionada aos favoritos! ⭐', 'sucesso')

    return redirect(url_for('ver_receita', id=receita.id))


# ─────────────────────────────────────────
#  ROTAS DE COMENTÁRIOS
# ─────────────────────────────────────────
@app.route('/comentar/<int:receita_id>', methods=['POST'])
def comentar(receita_id):
    """Adiciona um comentário em uma receita."""
    if not usuario_logado():
        return redirect(url_for('login'))

    receita = Receita.query.get_or_404(receita_id)
    texto = request.form.get('texto', '').strip()

    if not texto:
        flash('O comentário não pode estar vazio.', 'erro')
        return redirect(url_for('ver_receita', id=receita_id))

    if len(texto) > 500:
        flash('O comentário deve ter no máximo 500 caracteres.', 'erro')
        return redirect(url_for('ver_receita', id=receita_id))

    novo_comentario = Comentario(
        texto=texto,
        usuario_id=session['usuario_id'],
        receita_id=receita.id
    )
    db.session.add(novo_comentario)
    db.session.commit()

    flash('Comentário adicionado! 💬', 'sucesso')
    return redirect(url_for('ver_receita', id=receita_id))


@app.route('/comentario/excluir/<int:id>', methods=['POST'])
def excluir_comentario(id):
    """Exclui um comentário. Permitido para o autor ou o dono da receita."""
    if not usuario_logado():
        return redirect(url_for('login'))

    comentario = Comentario.query.get_or_404(id)
    receita_id = comentario.receita_id

    # Verifica se quem está tentando excluir é o autor do comentário
    # ou o dono da receita onde o comentário foi feito
    eh_autor     = comentario.usuario_id == session['usuario_id']
    eh_dono      = comentario.receita.usuario_id == session['usuario_id']

    if not eh_autor and not eh_dono:
        flash('Você não tem permissão para excluir este comentário.', 'erro')
        return redirect(url_for('ver_receita', id=receita_id))

    db.session.delete(comentario)
    db.session.commit()

    flash('Comentário excluído.', 'info')
    return redirect(url_for('ver_receita', id=receita_id))


# ─────────────────────────────────────────
#  ROTA DO PERFIL
# ─────────────────────────────────────────
@app.route('/perfil')
def perfil():
    """Página de perfil do usuário logado."""
    if not usuario_logado():
        return redirect(url_for('login'))

    usuario = Usuario.query.get_or_404(session['usuario_id'])

    # Receitas publicadas pelo usuário (excluindo as fixas da vovó)
    receitas_publicadas = Receita.query.filter_by(
        usuario_id=usuario.id
    ).order_by(Receita.nome).all()

    # Receitas favoritas: busca os favoritos do usuário e carrega as receitas
    favoritos   = Favorito.query.filter_by(usuario_id=usuario.id).all()
    ids_favoritos = [f.receita_id for f in favoritos]
    receitas_favoritas = Receita.query.filter(
        Receita.id.in_(ids_favoritos)
    ).all() if ids_favoritos else []

    # Comentários feitos pelo usuário, do mais recente para o mais antigo
    comentarios = Comentario.query.filter_by(
        usuario_id=usuario.id
    ).order_by(Comentario.data_criacao.desc()).all()

    return render_template(
        'perfil.html',
        usuario=usuario,
        receitas_publicadas=receitas_publicadas,
        receitas_favoritas=receitas_favoritas,
        comentarios=comentarios
    )


# ─────────────────────────────────────────
#  INICIALIZAÇÃO
# ─────────────────────────────────────────
with app.app_context():
    db.create_all()       # Cria as tabelas no banco se não existirem
    popular_banco()       # Adiciona as receitas fixas da vovó

if __name__ == '__main__':
    app.run(debug=True)
