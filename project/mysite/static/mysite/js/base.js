let words = '';


//============================================= FUNCTIONS =====================================================
function showLocalStorage(){
  console.log(`Showing local storage ${localStorage.getItem("daily_words")}`)
  console.log(`Showing local storage ${localStorage.getItem("daily_words_date")}`)
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function createStudyList() {


  fetch('/create-list/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
  })
  .then(response => response.json())
  .then(data => {
    alert(`Створено ${data.words.length} слів для вивчення`);
    const listCreateDate = new Date().toLocaleString()
    fillWords(data.words, listCreateDate);

    localStorage.setItem("daily_words", JSON.stringify(data.words));
    localStorage.setItem("daily_words_date", listCreateDate);
  });

 
}

function fillWords(wordsList, createDate){
  // console.log(wordsList)
  const dateItem = document.querySelector('.js-study_list_date_container')
  dateItem.innerHTML = `List creating date: ${createDate}`

  const container = document.querySelector('.study-list-container');
  container.innerHTML = '';
  wordsList.forEach((word, index) => {     
    const item = document.createElement('div');
    item.classList.add('card-container')
    const flipId = `flip${index}`;
    if (index === 0) {
        item.classList.add('active'); // Перший елемент каруселі має бути активним
      }

      item.innerHTML = `
      <div class = 'card-menu card-menu-sinonims' data-bs-toggle="popover" data-bs-title="Popover title" data-bs-content="And here’s some amazing content. It’s very engaging. Right?">S</div>
      <input type="checkbox" id="${flipId}" class="flip-checkbox">
      <label for="${flipId}" class="card">
        <div class="card-front">
          ${word.article + ' ' + word.eng}
        </div>
        <div class="card-back">
          ${word.ukr}
        </div>
      </label>`;
      container.appendChild(item);
      const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]')
      const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl))
    });
}

//======================================================================================================================
const createButton = document.querySelector('.js-create-new-list')
createButton.addEventListener('click', (event) =>{
    createStudyList()
});




document.addEventListener('DOMContentLoaded', function () {
  const storedWords = localStorage.getItem("daily_words");
  const storedDate = localStorage.getItem("daily_words_date");
  
  if (storedWords) {
    // повертаємо збережені слова
    words = JSON.parse(storedWords);
    fillWords(words, storedDate)
  } 
});


