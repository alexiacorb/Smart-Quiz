const button = document.getElementById('createAccount');

// Butonul se comporta ca un link catre pagina de inregistrare
button.onclick = () => {
    window.location.href = '/register';
};