import os
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, Usuario, Receita

app = Flask(__name__)

app.secret_key = '213SA210319KWIAOX0291'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///receitas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join('static', 'uploads')
EXTENSOES_PERMITIDAS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)


def extensao_permitida(nome_arquivo):
    return ('.' in nome_arquivo and
            nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS)


def usuario_logado():
    return 'usuario_id' in session


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


@app.route('/')
def inicio():
    if usuario_logado():
        return redirect(url_for('index'))
    return redirect(url_for('login'))


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
            flash(f'Bem-vindo(a), {usuario.nome}! 👋', 'sucesso')
            return redirect(url_for('index'))
        else:
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

        novo_usuario = Usuario(
            nome=nome,
            email=email,
            senha=generate_password_hash(senha)
        )
        db.session.add(novo_usuario)
        db.session.commit()

        flash('Cadastro realizado com sucesso! Faça seu login.', 'sucesso')
        return redirect(url_for('login'))

    return render_template('cadastro.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))


@app.route('/receitas')
def index():
    if not usuario_logado():
        return redirect(url_for('login'))

    busca = request.args.get('busca', '').strip()

    if busca:
        receitas = Receita.query.filter(
            Receita.nome.ilike(f'%{busca}%')
        ).order_by(Receita.fixa.desc(), Receita.nome).all()
    else:
        receitas = Receita.query.order_by(Receita.fixa.desc(), Receita.nome).all()

    return render_template('index.html', receitas=receitas, busca=busca)


@app.route('/receita/<int:id>')
def ver_receita(id):
    if not usuario_logado():
        return redirect(url_for('login'))

    receita = Receita.query.get_or_404(id)
    return render_template('receita.html', receita=receita)


@app.route('/receita/nova', methods=['GET', 'POST'])
def nova_receita():
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

        nome_foto = None
        foto = request.files.get('foto')
        if foto and foto.filename and extensao_permitida(foto.filename):
            nome_seguro = secure_filename(foto.filename)
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
    if not usuario_logado():
        return redirect(url_for('login'))

    receita = Receita.query.get_or_404(id)

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

        foto = request.files.get('foto')
        if foto and foto.filename and extensao_permitida(foto.filename):
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

    db.session.delete(receita)
    db.session.commit()

    flash('Receita excluída.', 'info')
    return redirect(url_for('index'))


with app.app_context():
    db.create_all()
    popular_banco()

if __name__ == '__main__':
    app.run(debug=True)
