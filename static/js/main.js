// ============================================
//  RECEITAS DA VOVÓ — main.js
//  JavaScript básico para interações da tela
// ============================================


// ── Preview de foto no upload ────────────────
// Quando o usuário escolhe uma imagem, mostra ela na tela antes de salvar
function configurarUpload() {
  const inputFoto    = document.getElementById('foto');
  const preview      = document.getElementById('upload-preview');
  const uploadArea   = document.getElementById('upload-area');
  const uploadTexto  = document.getElementById('upload-texto');

  if (!inputFoto) return; // Se não tiver campo de foto, não faz nada

  // Ao clicar na área de upload, abre o seletor de arquivo
  if (uploadArea) {
    uploadArea.addEventListener('click', () => inputFoto.click());
  }

  // Quando um arquivo é selecionado, mostra o preview
  inputFoto.addEventListener('change', function () {
    const arquivo = this.files[0];
    if (!arquivo) return;

    const leitor = new FileReader();
    leitor.onload = function (e) {
      preview.src     = e.target.result;
      preview.style.display = 'block';
      if (uploadTexto) uploadTexto.style.display = 'none';
    };
    leitor.readAsDataURL(arquivo);
  });
}


// ── Confirmação de exclusão ──────────────────
// Antes de excluir uma receita, pede confirmação ao usuário
function configurarExclusao() {
  const formExcluir = document.getElementById('form-excluir');
  if (!formExcluir) return;

  formExcluir.addEventListener('submit', function (e) {
    const confirmar = window.confirm(
      '⚠️ Tem certeza que deseja excluir esta receita?\nEsta ação não pode ser desfeita.'
    );
    if (!confirmar) {
      e.preventDefault(); // Cancela o envio do formulário
    }
  });
}


// ── Fechar mensagens flash automaticamente ───
// Remove os alertas depois de 5 segundos
function configurarFlash() {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (flash) {
    setTimeout(function () {
      flash.style.transition = 'opacity 0.5s ease';
      flash.style.opacity    = '0';
      setTimeout(function () { flash.remove(); }, 500);
    }, 5000); // 5 segundos
  });
}

function configurarRespostas() {
  const botoes = document.querySelectorAll('.btn-responder');
  botoes.forEach(function (botao) {
    botao.addEventListener('click', function () {
      const formulario = document.getElementById(`form-resposta-${botao.dataset.resposta}`);
      if (!formulario) return;
      formulario.hidden = !formulario.hidden;
      if (!formulario.hidden) formulario.querySelector('textarea').focus();
    });
  });
}


// ── Roda tudo quando a página carregar ───────
document.addEventListener('DOMContentLoaded', function () {
  configurarUpload();
  configurarExclusao();
  configurarFlash();
  configurarRespostas();
});
