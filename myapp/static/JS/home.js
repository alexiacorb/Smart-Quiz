const popupTeacher = document.getElementById('popup');
const popupStudent = document.getElementById('popup-student');
const createClassBtn = document.getElementById('createClass');
const closeButtons = document.querySelectorAll('#closePopup');

createClassBtn.addEventListener('click', () => {
    if (popupTeacher) {
        popupTeacher.classList.add('open-popup');
    }

    if (popupStudent) {
        popupStudent.classList.add('open-popup');
    }
});

closeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        if (popupTeacher) {
            popupTeacher.classList.remove('open-popup');
        }

        if (popupStudent) {
            popupStudent.classList.remove('open-popup');
        }
    });
});
