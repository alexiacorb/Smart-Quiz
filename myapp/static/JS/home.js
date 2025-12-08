const button =  document.getElementById('createClass');

button.onclick = () => {
    openPopup();
}
function openPopup() {
    const popup = document.getElementById('popup');
    popup.classList.add('open-popup');
}

function closePopup() {
    const popup = document.getElementById('popup');
    popup.classList.remove('open-popup');
}
const closeButton = document.getElementById('closePopup');
closeButton.onclick = () => {
    closePopup();
}




