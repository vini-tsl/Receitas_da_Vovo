function configurarUpload() {
  const inputFoto    = document.getElementById('foto');
  const preview      = document.getElementById('upload-preview');
  const uploadArea   = document.getElementById('upload-area');
  const uploadTexto  = document.getElementById('upload-texto');

  if (!inputFoto) return;

  if (uploadArea) {
    uploadArea.addEventListener('click', () => inputFoto.click());
  }

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


function configurarExclusao() {
  const formExcluir = document.getElementById('form-excluir');
  if (!formExcluir) return;

  formExcluir.addEventListener('submit', function (e) {
    const confirmar = window.confirm(
      'Tem certeza que deseja excluir esta receita?\nEsta ação não pode ser desfeita.'
    );
    if (!confirmar) {
      e.preventDefault();
    }
  });
}

function configurarFlash() {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (flash) {
    setTimeout(function () {
      flash.style.transition = 'opacity 0.5s ease';
      flash.style.opacity    = '0';
      setTimeout(function () { flash.remove(); }, 500);
    }, 5000); 
  });
}


document.addEventListener('DOMContentLoaded', function () {
  configurarUpload();
  configurarExclusao();
  configurarFlash();
});
