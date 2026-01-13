const options = ['A', 'B', 'C', 'D'];
let correctAnswers = {};

function renderGrid() {
    const container = document.getElementById('gridArea');
    const count = document.getElementById('numQuestions').value;
    container.innerHTML = '';
    correctAnswers = {};

    for (let i = 1; i <= count; i++) {
        let row = document.createElement('div');
        row.className = 'q-row';
        
        let num = document.createElement('span');
        num.className = 'q-num';
        num.innerText = i + '.';
        row.appendChild(num);

        options.forEach(opt => {
            let bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.innerText = opt;
            bubble.onclick = () => selectBubble(i, opt, bubble, row);
            row.appendChild(bubble);
        });
        container.appendChild(row);
    }
    updateJson();
}

function selectBubble(qNum, opt, element, row) {
    let bubbles = row.getElementsByClassName('bubble');
    for(let b of bubbles) b.classList.remove('selected');
    
    element.classList.add('selected');
    
    correctAnswers[qNum] = opt;
    updateJson();
}

function updateJson() {
    document.getElementById('finalJson').value = JSON.stringify(correctAnswers);
}

renderGrid();