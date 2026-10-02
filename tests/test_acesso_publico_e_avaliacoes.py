import os
import tempfile
import unittest
from pathlib import Path

_DIRETORIO_TESTE = tempfile.TemporaryDirectory(prefix='receitas-testes-')
_BANCO_TESTE = Path(_DIRETORIO_TESTE.name, 'receitas.db').as_posix()
os.environ['DATABASE_URL'] = f'sqlite:///{_BANCO_TESTE}'

from app import app
from models import db, Usuario, Receita, Avaliacao
from werkzeug.security import generate_password_hash


class TesteAcessoPublicoEAvaliacoes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
        _DIRETORIO_TESTE.cleanup()

    def setUp(self):
        with app.app_context():
            db.drop_all()
            db.create_all()
            self.usuario1 = Usuario(
                nome='Pessoa um',
                email='pessoa1@example.test',
                senha=generate_password_hash('senha123')
            )
            self.usuario2 = Usuario(
                nome='Pessoa dois',
                email='pessoa2@example.test',
                senha=generate_password_hash('senha123')
            )
            self.receita = Receita(
                nome='Bolo de teste',
                descricao='Uma receita para testes.',
                ingredientes='Farinha e água',
                modo_preparo='Misture e asse.',
                tempo_preparo='30 minutos',
                porcoes='4 porções',
                categoria='Doce',
                fixa=False
            )
            db.session.add_all([self.usuario1, self.usuario2, self.receita])
            db.session.commit()
            self.usuario1_id = self.usuario1.id
            self.usuario2_id = self.usuario2.id
            self.receita_id = self.receita.id
        self.client = app.test_client()

    def autenticar(self, client, usuario_id):
        with client.session_transaction() as sessao:
            sessao['usuario_id'] = usuario_id
            sessao['usuario_nome'] = 'Pessoa teste'

    def test_visitante_pode_ver_catalogo_e_detalhe(self):
        resposta_inicio = self.client.get('/')
        resposta_catalogo = self.client.get('/receitas')
        resposta_detalhe = self.client.get(f'/receita/{self.receita_id}')

        self.assertEqual(resposta_inicio.status_code, 302)
        self.assertTrue(resposta_inicio.location.endswith('/receitas'))
        self.assertEqual(resposta_catalogo.status_code, 200)
        self.assertIn(b'Criar conta', resposta_catalogo.data)
        self.assertEqual(resposta_detalhe.status_code, 200)
        self.assertIn(b'Entre para avaliar', resposta_detalhe.data)
        self.assertIn(b'crie uma conta', resposta_detalhe.data)

    def test_visitante_nao_pode_executar_acoes_restritas(self):
        resposta_avaliacao = self.client.post(
            f'/avaliar/{self.receita_id}', data={'nota': '5'}
        )
        resposta_favorito = self.client.post(f'/favoritar/{self.receita_id}')
        resposta_comentario = self.client.post(
            f'/comentar/{self.receita_id}', data={'texto': 'Comentário'}
        )

        self.assertTrue(resposta_avaliacao.location.endswith('/login?next=/receita/' + str(self.receita_id)))
        self.assertTrue(resposta_favorito.location.endswith('/login'))
        self.assertTrue(resposta_comentario.location.endswith('/login'))

    def test_nota_media_reavaliacao_e_exclusao_em_cascata(self):
        self.autenticar(self.client, self.usuario1_id)
        self.client.post(f'/avaliar/{self.receita_id}', data={'nota': '4'})
        self.client.post(f'/avaliar/{self.receita_id}', data={'nota': '2'})

        with app.app_context():
            avaliacoes_usuario1 = Avaliacao.query.filter_by(
                usuario_id=self.usuario1_id, receita_id=self.receita_id
            ).all()
            self.assertEqual(len(avaliacoes_usuario1), 1)
            self.assertEqual(avaliacoes_usuario1[0].nota, 2)

        segundo_cliente = app.test_client()
        self.autenticar(segundo_cliente, self.usuario2_id)
        segundo_cliente.post(f'/avaliar/{self.receita_id}', data={'nota': '4'})
        resposta_detalhe = segundo_cliente.get(f'/receita/{self.receita_id}')
        self.assertIn(b'3.0 de 5', resposta_detalhe.data)
        self.assertIn(b'(2 avalia', resposta_detalhe.data)

        with app.app_context():
            receita = db.session.get(Receita, self.receita_id)
            db.session.delete(receita)
            db.session.commit()
            self.assertEqual(
                Avaliacao.query.filter_by(receita_id=self.receita_id).count(), 0
            )

    def test_rejeita_notas_fora_do_intervalo(self):
        self.autenticar(self.client, self.usuario1_id)
        self.client.post(f'/avaliar/{self.receita_id}', data={'nota': '6'})

        with app.app_context():
            self.assertEqual(
                Avaliacao.query.filter_by(receita_id=self.receita_id).count(), 0
            )


if __name__ == '__main__':
    unittest.main()