const button = document.getElementById('login');

// Butonul se comporta ca un link catre pagina de login
button.onclick = () => {
    window.location.href = '/login';
};