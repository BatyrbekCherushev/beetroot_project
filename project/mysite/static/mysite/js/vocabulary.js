let words = '';
let currentBox = ''
const NEXT_BOX_SCHEME = {
  'BOX_1': 'BOX_2',
  'BOX_2': 'BOX_3',
  'BOX_3': 'LEARNT'
}

const toastLiveExample = document.getElementById('liveToast')
const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toastLiveExample)

let statistics

// bASIC FUNCTIONS ==================================================================================================
function showLocalStorage(){
  console.log(`Showing local storage ${localStorage.getItem("daily_words")}`)
  console.log(`Showing local storage ${localStorage.getItem("daily_words_date")}`)
}



async function getStatisticsBasic() {
  fetch('/get-statistics-basic/')
    .then(response => response.json())
    .then(data => {
      refreshStatistics(data);  
      // console.log(data)
    });
}

function refreshStatistics(data) {
  document.querySelector('.js-vocabulary-basic').textContent = `BASIC VOCABULARY (${data['TOTAL']} words totally, ${data['NEW']} new words, ${data['REPEAT']} words for repeat)`;
  // console.log('vocabulary.js: ', JSON.parse(localStorage.getItem('userInfo'))['settings']);
  const categories = ['REPEAT','PROCESS','BOX_1', 'BOX_2', 'BOX_3', 'LEARNT']
  const settings = JSON.parse(localStorage.getItem('userInfo'))['settings'];
        for (const category of categories){
          let text = '';
          if (['BOX_1', 'BOX_2', 'BOX_3'].includes(category)) {
            text = `${data[category]} / ${settings[`${category}_limit`]}`
            document.querySelector(`.js-box.box-${category} .js-usable`).textContent = data[`${category}_usable`] + " для тесту";
          } else {
            text = data[category];
          }
            // console.log(category)
            document.querySelector(`.js-box-text-${category}`).textContent = text;
        }
    document.querySelector('.js-box.box-LEARNT .js-usable').textContent = data['LEARNT_usable'] + " для тесту";
        paintBoxes(data);
}


function paintBoxes(data){
  for (category of ['BOX_1', 'BOX_2', 'BOX_3']) {
    // console.log(category);
    // console.log(JSON.parse(localStorage.getItem('userInfo'))['settings'][`${category}_limit`])
    if (data[category] >= JSON.parse(localStorage.getItem('userInfo'))['settings'][`${category}_limit`]) {
     document.querySelector(`.js-box.box-${category}`).classList.add('box_overloaded');
      }
  else {
    document.querySelector(`.js-box.box-${category}`).classList.remove('box_overloaded');
  }
  }
}

document.addEventListener('DOMContentLoaded', async function () {
  const storedWords = localStorage.getItem("daily_words");
  const storedDate = localStorage.getItem("daily_words_date");
  if (storedWords) {
    // повертаємо збережені слова
    words = JSON.parse(storedWords);
    fillWords(words, storedDate)
    getStatisticsBasic();
  }
  
  
});

// STUDY PROCCESS BLOCK ================================================================================================
// CLICK on CREATE NEW LIST BUTTON
const createButton = document.querySelector('.js-create-new-list')

createButton.addEventListener('click', (event) =>{
    if (document.querySelector('.js-box.box-BOX_1').classList.contains('box_overloaded')){
      alert('BOX-1 does not have place')
    } else {
      createStudyList();
    }
    
   
});

// SHOW PREVIOUS CARD
const previousCardBtn = document.querySelector('.js-previous-card');
const nextCardBtn = document.querySelector('.js-next-card');

previousCardBtn.addEventListener('click', () => {
  const activeElement = document.querySelector('.card_container.active');
  let prevElement = activeElement?.previousElementSibling;
  if (prevElement) {
    prevElement.classList.add('active');
    activeElement.classList.remove('active');
    if (nextCardBtn.disabled) {
      nextCardBtn.disabled = false;
    }
  } else {
    previousCardBtn.disabled = true;

  }
});

// SHOW NEXT CARD
nextCardBtn.addEventListener('click', () => {
  const activeElement = document.querySelector('.card_container.active');
  let nextElement = activeElement?.nextElementSibling;
  
  if (nextElement){
    nextElement.classList.add('active');
    activeElement.classList.remove('active');
    if (previousCardBtn.disabled) {
      previousCardBtn.disabled = false;
    }
  } else {
    nextCardBtn.disabled = true;
  }
});

// CREATE NEW STUDY LIST
function createStudyList() {
  fetch('/create-list/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      rep_number: 3,
      new_number: 10
    })
  })
  .then(response => {
    if (!response.ok) { // якщо HTTP статус не 2xx
      return response.json().then(errData => {
        // обробляємо помилку
        throw errData; 
      });
    }
    return response.json(); // успішна відповідь
  })
  .then(data => {
    console.log('Success:', data);
    toastBootstrap.show();
    const listCreateDate = new Date().toLocaleString();
    fillWords(data.words, listCreateDate);

    localStorage.setItem("daily_words", JSON.stringify(data.words));
    localStorage.setItem("daily_words_date", listCreateDate);
    getStatisticsBasic();
      
  })
  .catch(error => {
    // тут ловимо як мережеві помилки, так і помилки сервера
    console.error('Error:', error);
    if (error.code === 'NO_MORE_WORDS') {
      alert('Слова для вивчення закінчилися!');
      // toastBootstrap.show('Слова для вивчення закінчилися!');
    } else {
      alert('Сталася помилка при створенні списку слів.');
    }
     getStatisticsBasic();
  });
}

// FILL WORD CARDS WITH WORDS
function fillWords(wordsList, createDate){
  // console.log(wordsList)
  const dateItem = document.querySelector('.js-study_list_date_container')
  dateItem.innerHTML = `List creating date: ${createDate}`

  const container = document.querySelector('.js-flip-card-container');
  container.innerHTML = '';
  wordsList.forEach((word, index) => {     
    const item = document.createElement('div');
    item.classList.add('card_container')
   
    if (index === 0) {
        item.classList.add('active'); // Перший елемент каруселі має бути активним
      }

      item.innerHTML =
      `
      <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill  text-bg-secondary">${index + 1}</span>
      <div class="card_warpper flip-card">
      
            <div class="flip-card-inner js-flip-card">
                <div class="flip-card-front">${word.article + ' ' + word.eng}</div>
                <div class="flip-card-back">${word.ukr}</div>
                <div class="accordion" id="word-accordion">
                    
                </div>
            </div>
            
        </div>
        <div class="accordion_wrapper">
            <div class="accordion" id="accordionWord-${index + 1}">
                <div class="accordion-item">
                    <h2 class="accordion-header">
                    <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseCommentary-${index + 1}" aria-expanded="true" aria-controls="collapseCommentary-${index + 1}">
                        COMMENTS
                    </button>
                    </h2>
                    <div id="collapseCommentary-${index + 1}" class="accordion-collapse collapse" data-bs-parent="#accordionWord-${index + 1}">
                    <div class="accordion-body">
                        ${'SOME COMMENTARY'}
                    </div>
                    </div>
                </div>
                <div class="accordion-item">
                    <h2 class="accordion-header">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseSynonims-${index + 1}" aria-expanded="false" aria-controls="collapseSynonims-${index + 1}">
                        SYNONIMS
                    </button>
                    </h2>
                    <div id="collapseSynonims-${index + 1}" class="accordion-collapse collapse" data-bs-parent="#accordionWord-${index + 1}">
                    <div class="accordion-body">
                        ${'SYNONIMS: ' + word.synonims}
                    </div>
                    </div>
                </div>
  
            </div>
        </div>`;
      
      
      
      // `
      //   <span class="position-absolute top-0 start-100 translate-middle badge rounded-pill  text-bg-secondary">${index + 1}</span>
      //   <h5 class="card-header">${word.article + ' ' + word.eng}</h5>
      //   <div class="card-body flip-card p-0 m-0 w-100">
      //   <div class="flip-card-inner js-flip-card">
      //       <div class="flip-card-front">${'SOME COMMENTARY'}</div>
      //       <div class="flip-card-back">${word.ukr}</div>
      //   </div>
          
      //   </div>
      //   <div class="card-footer text-body-secondary">${'SYNONIMS: ' + word.synonims}</div>
        
      // `;
      container.appendChild(item);
  });

    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl,))
    document.querySelectorAll('.js-flip-card').forEach(card => {
      card.addEventListener('click', () => {
      card.closest('.flip-card').classList.toggle('flipped');
    });
});
}



//СLICK on BOX element на бокс він стає активним і в оперативні області з'являється відповідний контент
document.querySelectorAll('.js-box').forEach(box => {
    box.addEventListener('click', (event) => {
        // console.log(event.currentTarget);
        const clickedBox = event.currentTarget;
        const activeBox = document.querySelector('.js-box.box-active')

        const newAreaSelector = `.${clickedBox.dataset.operationArea}`;
        const newArea = document.querySelector(newAreaSelector);

        // Зняти клас з попереднього активного
        if (activeBox && activeBox !== clickedBox) {
            activeBox.classList.remove('box-active');

            const oldArea = document.querySelector(`.${activeBox.dataset.operationArea}`);
            // Ховаємо стару область тільки якщо це інша зона
            if (oldArea && oldArea !== newArea) {
                oldArea.classList.add('d-none');
            }
        }

        // Додати клас активному блоку
        clickedBox.classList.add('box-active');

        // Показати область, якщо вона ще прихована
        if (newArea && newArea.classList.contains('d-none')) {
            newArea.classList.remove('d-none');
        }
        
        currentBox = clickedBox.dataset.box
        document.querySelector('.js-title').textContent = currentBox;
        // console.log(currentBox)

        document.querySelector('.js-show-word').textContent = '';
        document.querySelector('.js-input-answer').value = '';
        document.querySelector('.js-feedback').textContent = '';



    });
});

// TESTING =========================================================================================================
function getNextWord(boxName) {
    fetch(`/get-box-word/?box=${boxName}`)
        .then(response => response.json())
        .then(data => {
            if (!data.word) {
                alert('Слова для цього бокса закінчилися');
                return;
            }
            // console.log('NEXT BUTTON CLICK: ', data)
            const word = data.word;
            // console.log('Наступне слово:', word.eng);
            // тут можна оновити UI: показати слово користувачу
            document.querySelector('.js-show-word').textContent = `${word.article} ${word.eng}`;
            document.querySelector('.js-input-answer').dataset.wordId = data.word.id
        });
}
document.querySelector('.js-next-word').addEventListener('click', () => {
    // console.log(currentBox)
    getNextWord(currentBox);
})

document.querySelector('.js-test-answer').addEventListener('click',async () => {
  // console.log(`.js-box.box-${NEXT_BOX_SCHEME[currentBox]}`);
    const next_box_selector_part = NEXT_BOX_SCHEME[currentBox]
    const next_box = document.querySelector(`.js-box.box-${next_box_selector_part}`);
    
   if (next_box && next_box.classList.contains('box_overloaded')) {
    alert(`BOX ${next_box_selector_part} is overloaded`)
   } else {
    const input = document.querySelector('.js-input-answer');
    const word_id = input.dataset.wordId
    const answer = input.value.trim();
    const feedback = document.querySelector('.js-feedback');

    const clear_input = () => {
      input.value = ''
    }

    if (!answer) {
        feedback.textContent = 'Введи відповідь!';
        return;
    }

    try {
        const response = await fetch('/test-word/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // функція getCookie повинна бути визначена
            },
            body: JSON.stringify({
                word_id: word_id,
                answer: answer
            })
        });

        const data = await response.json();

        if (data.error) {
            feedback.textContent = data.error;
            clear_input();
            return;
        }

        if (data.correct) {
            feedback.textContent = 'Правильно! 🎉';
            
            // console.log(currentBox);
            // getNextWord(currentBox); // показати наступне слово
        } else {
            feedback.textContent = `Відповідь ${answer} є НЕПРАВИЛЬНА. \n Правильна відповідь: ${data.correct_answer}`;
            
        }
        clear_input(); // очищаємо інпут
        getStatisticsBasic();
        getNextWord(currentBox);

    } catch (err) {
        // console.error('Помилка при відправці відповіді:', err);
        feedback.textContent = 'Помилка при перевірці відповіді';
    }
   }
    
});





