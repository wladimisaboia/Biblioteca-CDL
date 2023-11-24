function Login() {
  const user = document.getElementById('user').value;
  const password = document.getElementById('password').value;

  fetch('/', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `usuario=${user}&senha=${password}`,
  })
  .then(response => {
      if (response.redirected) {
          window.location.href = response.url;
      } else {
          console.error('Erro no login: Credenciais inválidas');
          Toastify({
              text: "Usuario ou senha incorretas",
              duration: 2000,
              gravity: "top",
              position: 'right',
              backgroundColor: "linear-gradient(to right, #ff8a00, #e52e71)",
              close: true,
          }).showToast();
      }
  })
  .catch(error => console.error('Erro:', error));
}
