import os
import secrets
from datetime import datetime, timedelta
from urllib.parse import urlsplit
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, Usuario, Receita, Favorito, Avaliacao, Comentario

app = Flask(__name__)
app.secret_key = '213SA210319KWIAOX0291'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///receitas.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'
app.config['MAIL_USERNAME'] = "receitasdavovoweb@gmail.com"
app.config['MAIL_PASSWORD'] = "fkuf yovj ofsm zgum"
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', os.environ.get('MAIL_USERNAME'))
UPLOAD_FOLDER = os.path.join('static', 'uploads')
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mail = Mail(app)
db.init_app(app)

def extensao_permitida(nome_arquivo):
    return ('.' in nome_arquivo and
            nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS)

def usuario_logado():
    return 'usuario_id' in session

@app.context_processor
def injetar_usuario_atual():
    if usuario_logado():
        return {'usuario_atual': Usuario.query.get(session['usuario_id'])}
    return {'usuario_atual': None}

def popular_banco():
    if Receita.query.filter_by(fixa=True).first():
        return
    receitas_da_vovo = [
        Receita(
            nome='Bolo de Cenoura da Vovó',
            descricao='O clássico bolo de cenoura com cobertura de chocolate derretido, receita de família.',
            ingredientes='3 cenouras médias\n3 ovos\n1 xícara de óleo\n2 xícaras de açúcar\n2 xícaras de farinha de trigo\n1 colher de sopa de fermento em pó\n\nCobertura:\n4 colheres de sopa de chocolate em pó\n4 colheres de sopa de açúcar\n1 colher de sopa de manteiga\n5 colheres de sopa de leite',
            modo_preparo='1. Preaqueça o forno a 180°C e unte uma forma.\n2. No liquidificador, bata as cenouras, os ovos e o óleo até ficar homogêneo.\n3. Numa tigela, misture o açúcar, a farinha e o fermento.\n4. Junte a mistura do liquidificador aos ingredientes secos e mexa bem.\n5. Despeje na forma e asse por 35 a 40 minutos.\n6. Para a cobertura, misture tudo numa panela e leve ao fogo até engrossar.\n7. Despeje a cobertura quente sobre o bolo ainda na forma.',
            tempo_preparo='50 minutos',
            tempo_minutos=50,
            porcoes='10 fatias',
            categoria='Doce',
            dificuldade='Fácil',
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
            tempo_minutos=90,
            porcoes='6 pessoas',
            categoria='Salgado',
            dificuldade='Médio',
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
            tempo_minutos=40,
            porcoes='8 porções',
            categoria='Sobremesa',
            dificuldade='Fácil',
            foto='arroz-doce.png',
            fixa=True,
            usuario_id=None
        ),
    ]
    db.session.add_all(receitas_da_vovo)
    db.session.commit()

@app.route('/')
def inicio():
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if usuario_logado():
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        if not email or not senha:
            flash('Preencha todos os campos.', 'erro')
            return render_template('login.html')
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            session['usuario_nome'] = usuario.nome
            destino = request.args.get('next', '')
            partes_destino = urlsplit(destino)
            if partes_destino.path.startswith('/') and not partes_destino.netloc and not partes_destino.scheme and '\\' not in partes_destino.path:
                return redirect(destino)
            return redirect(url_for('index'))
        flash('Email ou senha incorretos.', 'erro')
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if usuario_logado():
        return redirect(url_for('index'))
    if request.method == 'POST':
        nome  = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        senha2 = request.form.get('senha2', '')
        if not nome or not email or not senha or not senha2:
            flash('Preencha todos os campos.', 'erro')
            return render_template('cadastro.html')
        if senha != senha2:
            flash('As senhas não coincidem.', 'erro')
            return render_template('cadastro.html')
        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'erro')
            return render_template('cadastro.html')
        if Usuario.query.filter_by(email=email).first():
            flash('Este email já está cadastrado.', 'erro')
            return render_template('cadastro.html')
        novo = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha)
            
        )
        db.session.add(novo)
        db.session.commit()
        flash('Cadastro realizado! Faça seu login.', 'sucesso')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

def enviar_email_redefinicao(usuario, link):
    if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
        print(f'Link de redefinição de senha: {link}')
        return True

    try:
        mensagem = Message(
            'Redefinição de senha - Receitas da Vovó',
            sender=app.config.get('MAIL_DEFAULT_SENDER') or app.config.get('MAIL_USERNAME'),
            recipients=[usuario.email]
        )
        mensagem.body = (
            'Você solicitou a redefinição da sua senha.\n\n'
            f'Clique no link abaixo para criar uma nova senha:\n{link}\n\n'
            'Se você não pediu esta alteração, ignore este e-mail.'
        )
        mensagem.html = (
            '<p>Você solicitou a redefinição da sua senha.</p>'
            f'<p><a href="{link}">Clique aqui para redefinir sua senha</a></p>'
            '<p>Se você não pediu esta alteração, ignore este e-mail.</p>'
        )
        mail.send(mensagem)
        return True
    except Exception as erro:
        print(f'Falha ao enviar e-mail de redefinição para {usuario.email}: {erro}')
        print(f'Link de redefinição de senha: {link}')
        return False

@app.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if usuario_logado():
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            usuario.token_redefinicao = secrets.token_urlsafe(32)
            usuario.token_expira_em = datetime.utcnow() + timedelta(minutes=30)
            db.session.commit()
            link = url_for('redefinir_senha', token=usuario.token_redefinicao, _external=True)
            enviar_email_redefinicao(usuario, link)
        flash('Se o e-mail existir, enviamos um link de redefinição.', 'sucesso')
        return render_template('esqueci_senha.html')
    return render_template('esqueci_senha.html')

@app.route('/redefinir-senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    usuario = Usuario.query.filter_by(token_redefinicao=token).first()
    if not usuario or not usuario.token_expira_em or usuario.token_expira_em < datetime.utcnow():
        flash('O link de redefinição é inválido ou expirou.', 'erro')
        return redirect(url_for('esqueci_senha'))
    if request.method == 'POST':
        nova_senha = request.form.get('nova_senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        if len(nova_senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'erro')
            return render_template('redefinir_senha.html')
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem.', 'erro')
            return render_template('redefinir_senha.html')
        usuario.senha = generate_password_hash(nova_senha)
        usuario.token_redefinicao = None
        usuario.token_expira_em = None
        db.session.commit()
        flash('Senha redefinida com sucesso! Faça seu login.', 'sucesso')
        return redirect(url_for('login'))
    return render_template('redefinir_senha.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

@app.route('/receitas')
def index():
    # ── Coleta todos os parâmetros da URL ──────────────────────────────
    # Pesquisa simples
    busca = request.args.get('busca', '').strip()

    # Filtros avançados
    categoria   = request.args.get('categoria', '').strip()
    dificuldade = request.args.get('dificuldade', '').strip()
    tempo_max   = request.args.get('tempo_max', '').strip()

    # ── Monta a query dinamicamente ────────────────────────────────────
    # Começa com todas as receitas e vai adicionando filtros conforme necessário
    query = Receita.query

    # Pesquisa simples: busca o termo no nome, ingredientes e descrição ao mesmo tempo
    if busca:
        termo = f'%{busca}%'
        query = query.filter(
            db.or_(
                Receita.nome.ilike(termo),
                Receita.ingredientes.ilike(termo),
                Receita.descricao.ilike(termo)
            )
        )

    # Filtro por categoria (ex: "Doce", "Salgado")
    if categoria:
        query = query.filter(Receita.categoria == categoria)

    # Filtro por dificuldade (ex: "Fácil", "Médio", "Difícil")
    if dificuldade:
        query = query.filter(Receita.dificuldade == dificuldade)

    # Filtro por tempo máximo em minutos (ex: até 30 minutos)
    if tempo_max:
        try:
            tempo_max_int = int(tempo_max)
            # Inclui receitas sem tempo_minutos cadastrado (nullable)
            query = query.filter(
                db.or_(
                    Receita.tempo_minutos <= tempo_max_int,
                    Receita.tempo_minutos == None
                )
            )
        except ValueError:
            pass  # Se o valor não for número, ignora o filtro

    # Executa a query ordenando: receitas fixas primeiro, depois por nome
    receitas = query.order_by(Receita.fixa.desc(), Receita.nome).all()
    medias_avaliacoes = {
        receita_id: {'media': float(media), 'total': total}
        for receita_id, media, total in db.session.query(
            Avaliacao.receita_id,
            db.func.avg(Avaliacao.nota),
            db.func.count(Avaliacao.id)
        ).group_by(Avaliacao.receita_id).all()
    }

    # Verifica se algum filtro avançado está ativo (para manter o painel aberto)
    filtros_ativos = any([categoria, dificuldade, tempo_max])

    # Busca as categorias distintas existentes no banco para popular o select
    categorias = db.session.query(Receita.categoria).distinct().order_by(Receita.categoria).all()
    categorias = [c[0] for c in categorias]

    return render_template(
        'index.html',
        receitas=receitas,
        busca=busca,
        categoria=categoria,
        dificuldade=dificuldade,
        tempo_max=tempo_max,
        filtros_ativos=filtros_ativos,
        categorias=categorias,
        medias_avaliacoes=medias_avaliacoes
    )

@app.route('/receita/<int:id>')
def ver_receita(id):
    receita = Receita.query.get_or_404(id)
    usuario_id = session.get('usuario_id')
    favoritado = usuario_id is not None and Favorito.query.filter_by(
        usuario_id=usuario_id, receita_id=id
    ).first() is not None
    avaliacao_usuario = None
    if usuario_id is not None:
        avaliacao_usuario = Avaliacao.query.filter_by(
            usuario_id=usuario_id, receita_id=id
        ).first()
    estatisticas = db.session.query(
        db.func.avg(Avaliacao.nota), db.func.count(Avaliacao.id)
    ).filter_by(receita_id=id).first()
    return render_template(
        'receita.html',
        receita=receita,
        favoritado=favoritado,
        avaliacao_usuario=avaliacao_usuario,
        media_avaliacoes=float(estatisticas[0]) if estatisticas[0] is not None else None,
        total_avaliacoes=estatisticas[1]
    )

@app.route('/avaliar/<int:receita_id>', methods=['POST'])
def avaliar_receita(receita_id):
    if not usuario_logado():
        return redirect(url_for('login', next=url_for('ver_receita', id=receita_id)))
    receita = Receita.query.get_or_404(receita_id)
    try:
        nota = int(request.form.get('nota', ''))
    except ValueError:
        nota = 0
    if nota < 1 or nota > 5:
        flash('Escolha uma nota entre 1 e 5 estrelas.', 'erro')
        return redirect(url_for('ver_receita', id=receita.id))
    avaliacao = Avaliacao.query.filter_by(
        usuario_id=session['usuario_id'], receita_id=receita.id
    ).first()
    if avaliacao:
        avaliacao.nota = nota
        flash('Sua avaliação foi atualizada.', 'sucesso')
    else:
        db.session.add(Avaliacao(
            nota=nota, usuario_id=session['usuario_id'], receita_id=receita.id
        ))
        flash('Avaliação registrada!', 'sucesso')
    db.session.commit()
    return redirect(url_for('ver_receita', id=receita.id))

@app.route('/receita/nova', methods=['GET', 'POST'])
def nova_receita():
    if not usuario_logado():
        return redirect(url_for('login'))
    if request.method == 'POST':
        nome=request.form.get('nome','').strip(); descricao=request.form.get('descricao','').strip()
        ingredientes=request.form.get('ingredientes','').strip(); modo_preparo=request.form.get('modo_preparo','').strip()
        tempo_preparo=request.form.get('tempo_preparo','').strip(); porcoes=request.form.get('porcoes','').strip()
        categoria=request.form.get('categoria','').strip()
        dificuldade=request.form.get('dificuldade','').strip() or None
        tempo_min_str=request.form.get('tempo_minutos','').strip()
        tempo_minutos=int(tempo_min_str) if tempo_min_str.isdigit() else None
        if not all([nome,descricao,ingredientes,modo_preparo,tempo_preparo,porcoes,categoria]):
            flash('Preencha todos os campos obrigatórios.', 'erro')
            return render_template('form_receita.html', receita=None)
        nome_foto = None
        foto = request.files.get('foto')
        if foto and foto.filename and extensao_permitida(foto.filename):
            nome_seguro = secure_filename(foto.filename)
            nome_foto = f"{session['usuario_id']}_{nome_seguro}"
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_foto))
        nova = Receita(nome=nome,descricao=descricao,ingredientes=ingredientes,modo_preparo=modo_preparo,tempo_preparo=tempo_preparo,tempo_minutos=tempo_minutos,porcoes=porcoes,categoria=categoria,dificuldade=dificuldade,foto=nome_foto,fixa=False,usuario_id=session['usuario_id'])
        db.session.add(nova); db.session.commit()
        flash('Receita adicionada! 🍽️', 'sucesso')
        return redirect(url_for('index'))
    return render_template('form_receita.html', receita=None)

@app.route('/receita/editar/<int:id>', methods=['GET', 'POST'])
def editar_receita(id):
    if not usuario_logado():
        return redirect(url_for('login'))
    receita = Receita.query.get_or_404(id)
    if receita.fixa or receita.usuario_id != session['usuario_id']:
        flash('Você não tem permissão para editar esta receita.', 'erro')
        return redirect(url_for('index'))
    if request.method == 'POST':
        receita.nome=request.form.get('nome','').strip(); receita.descricao=request.form.get('descricao','').strip()
        receita.ingredientes=request.form.get('ingredientes','').strip(); receita.modo_preparo=request.form.get('modo_preparo','').strip()
        receita.tempo_preparo=request.form.get('tempo_preparo','').strip(); receita.porcoes=request.form.get('porcoes','').strip()
        receita.categoria=request.form.get('categoria','').strip()
        receita.dificuldade=request.form.get('dificuldade','').strip() or None
        tempo_min_str=request.form.get('tempo_minutos','').strip()
        receita.tempo_minutos=int(tempo_min_str) if tempo_min_str.isdigit() else None
        foto = request.files.get('foto')
        if foto and foto.filename and extensao_permitida(foto.filename):
            if receita.foto:
                caminho_antigo = os.path.join(app.config['UPLOAD_FOLDER'], receita.foto)
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)
            nome_foto = f"{session['usuario_id']}_{secure_filename(foto.filename)}"
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_foto))
            receita.foto = nome_foto
        db.session.commit()
        flash('Receita atualizada!', 'sucesso')
        return redirect(url_for('ver_receita', id=receita.id))
    return render_template('form_receita.html', receita=receita)

@app.route('/receita/excluir/<int:id>', methods=['POST'])
def excluir_receita(id):
    if not usuario_logado():
        return redirect(url_for('login'))
    receita = Receita.query.get_or_404(id)
    if receita.fixa or receita.usuario_id != session['usuario_id']:
        flash('Você não tem permissão para excluir esta receita.', 'erro')
        return redirect(url_for('index'))
    if receita.foto:
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], receita.foto)
        if os.path.exists(caminho):
            os.remove(caminho)
    db.session.delete(receita); db.session.commit()
    flash('Receita excluída.', 'info')
    return redirect(url_for('index'))

@app.route('/favoritar/<int:id>', methods=['POST'])
def favoritar(id):
    if not usuario_logado():
        return redirect(url_for('login'))
    receita = Receita.query.get_or_404(id)
    ja = Favorito.query.filter_by(usuario_id=session['usuario_id'], receita_id=receita.id).first()
    if ja:
        db.session.delete(ja); db.session.commit()
        flash('Removido dos favoritos.', 'info')
    else:
        db.session.add(Favorito(usuario_id=session['usuario_id'], receita_id=receita.id))
        db.session.commit()
        flash('Adicionado aos favoritos!', 'sucesso')
    return redirect(url_for('ver_receita', id=receita.id))

@app.route('/comentar/<int:receita_id>', methods=['POST'])
def comentar(receita_id):
    if not usuario_logado():
        return redirect(url_for('login'))
    receita = Receita.query.get_or_404(receita_id)
    texto = request.form.get('texto', '').strip()
    if not texto:
        flash('O comentário não pode estar vazio.', 'erro')
        return redirect(url_for('ver_receita', id=receita_id))
    resposta_de_id = request.form.get('resposta_de_id', '').strip()
    comentario_pai = None
    if resposta_de_id:
        try:
            comentario_pai = Comentario.query.filter_by(
                id=int(resposta_de_id), receita_id=receita.id
            ).first()
        except ValueError:
            comentario_pai = None
        if not comentario_pai or comentario_pai.resposta_de_id is not None:
            flash('Só é possível responder comentários principais desta receita.', 'erro')
            return redirect(url_for('ver_receita', id=receita_id))
    db.session.add(Comentario(
        texto=texto,
        usuario_id=session['usuario_id'],
        receita_id=receita.id,
        resposta_de_id=comentario_pai.id if comentario_pai else None
    ))
    db.session.commit()
    flash('Comentário adicionado!', 'sucesso')
    return redirect(url_for('ver_receita', id=receita_id))

@app.route('/comentario/excluir/<int:id>', methods=['POST'])
def excluir_comentario(id):
    if not usuario_logado():
        return redirect(url_for('login'))
    comentario = Comentario.query.get_or_404(id)
    receita_id = comentario.receita_id
    eh_autor = comentario.usuario_id == session['usuario_id']
    eh_dono  = comentario.receita.usuario_id == session['usuario_id']
    if not eh_autor and not eh_dono:
        flash('Sem permissão.', 'erro')
        return redirect(url_for('ver_receita', id=receita_id))
    if comentario.resposta_de_id is None:
        for resposta in comentario.respostas:
            db.session.delete(resposta)
    db.session.delete(comentario); db.session.commit()
    flash('Comentário excluído.', 'info')
    return redirect(url_for('ver_receita', id=receita_id))

CORES_TEMA_PERFIL = {
    'laranja': {'nome': 'Laranja', 'cor1': '#E07A2F', 'cor2': '#8B5E3C'},
    'verde':   {'nome': 'Verde',   'cor1': '#5A8F3C', 'cor2': '#2F5C21'},
    'azul':    {'nome': 'Azul',    'cor1': '#2980B9', 'cor2': '#1B4F72'},
    'rosa':    {'nome': 'Rosa',    'cor1': '#D65A8F', 'cor2': '#93315C'},
    'roxo':    {'nome': 'Roxo',    'cor1': '#8E5CB0', 'cor2': '#54306B'},
    'vermelho':{'nome': 'Vermelho','cor1': '#C0392B', 'cor2': '#7B241C'},
}

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if not usuario_logado():
        return redirect(url_for('login'))
    usuario = Usuario.query.get_or_404(session['usuario_id'])

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        bio  = request.form.get('bio', '').strip()
        cor_tema = request.form.get('cor_tema', '').strip()

        if nome:
            usuario.nome = nome
            session['usuario_nome'] = nome
        usuario.bio = bio or None
        if cor_tema in CORES_TEMA_PERFIL:
            usuario.cor_tema = cor_tema

        foto = request.files.get('foto')
        if foto and foto.filename and extensao_permitida(foto.filename):
            if usuario.foto:
                caminho_antigo = os.path.join(app.config['UPLOAD_FOLDER'], usuario.foto)
                if os.path.exists(caminho_antigo):
                    os.remove(caminho_antigo)
            nome_foto = f"perfil_{usuario.id}_{secure_filename(foto.filename)}"
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], nome_foto))
            usuario.foto = nome_foto

        db.session.commit()
        flash('Perfil atualizado!', 'sucesso')
        return redirect(url_for('perfil'))

    receitas_publicadas = Receita.query.filter_by(usuario_id=usuario.id).order_by(Receita.nome).all()
    favoritos = Favorito.query.filter_by(usuario_id=usuario.id).all()
    ids_fav = [f.receita_id for f in favoritos]
    receitas_favoritas = Receita.query.filter(Receita.id.in_(ids_fav)).all() if ids_fav else []
    comentarios = Comentario.query.filter_by(usuario_id=usuario.id).order_by(Comentario.data_criacao.desc()).all()
    return render_template(
        'perfil.html',
        usuario=usuario,
        receitas_publicadas=receitas_publicadas,
        receitas_favoritas=receitas_favoritas,
        comentarios=comentarios,
        cores_tema=CORES_TEMA_PERFIL
    )

@app.route('/sobre')
def sobre():
    if not usuario_logado():
        return redirect(url_for('login'))
    return render_template('sobre.html')

def migrar_colunas_perfil():
    """Adiciona as colunas novas de perfil (foto, bio, cor_tema) em bancos
    já existentes, sem apagar os dados de usuários já cadastrados."""
    from sqlalchemy import text
    colunas_existentes = {
        linha[1] for linha in db.session.execute(text("PRAGMA table_info(usuario)"))
    }
    novas_colunas = {
        'foto': "ALTER TABLE usuario ADD COLUMN foto VARCHAR(200)",
        'bio': "ALTER TABLE usuario ADD COLUMN bio VARCHAR(300)",
        'cor_tema': "ALTER TABLE usuario ADD COLUMN cor_tema VARCHAR(20) DEFAULT 'laranja'",
    }
    for coluna, comando in novas_colunas.items():
        if coluna not in colunas_existentes:
            db.session.execute(text(comando))
    db.session.commit()

def migrar_colunas_novas():
    """Adiciona campos de redefinição de senha e respostas sem apagar dados."""
    from sqlalchemy import text
    tabelas = {
        'usuario': {
            'token_redefinicao': "ALTER TABLE usuario ADD COLUMN token_redefinicao VARCHAR(200)",
            'token_expira_em': "ALTER TABLE usuario ADD COLUMN token_expira_em DATETIME",
        },
        'comentario': {
            'resposta_de_id': "ALTER TABLE comentario ADD COLUMN resposta_de_id INTEGER",
        },
    }
    for tabela, colunas in tabelas.items():
        existentes = {linha[1] for linha in db.session.execute(text(f"PRAGMA table_info({tabela})"))}
        for coluna, comando in colunas.items():
            if coluna not in existentes:
                db.session.execute(text(comando))
    db.session.commit()

with app.app_context():
    db.create_all()
    migrar_colunas_perfil()
    migrar_colunas_novas()
    popular_banco()

if __name__ == '__main__':
    app.run(debug=True)
