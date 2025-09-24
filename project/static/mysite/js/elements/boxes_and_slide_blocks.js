import {get_statistics, getCookie, getUserInfo} from '../global.js'
import {refresh_instance_statistics} from './boxes_exports.js'

//================================================================================= CLICK ON BOXES BUTTONS =====================================================================================

const btns_create_study_list = document.querySelectorAll('.js-btn-create-list')

btns_create_study_list.forEach(btn_create => {
      btn_create.addEventListener('click', ()=>{
        const instance_type = btn_create.closest('.js-box').dataset.instance_type;
        const instance_language = btn_create.closest('.js-box').dataset.instance_language;
        // console.log('INSTANCE=', instance)
        document.dispatchEvent(new CustomEvent('create_study_list', {
        detail:{
            instance_type: instance_type,
            instance_language: instance_language
        }
        }));
      });
});

const btns_test_words = document.querySelectorAll('.js-test');

btns_test_words.forEach(button => {
  button.addEventListener('click', () => {
    const closest_box = button.closest('.js-box');
    const instance_type = closest_box.dataset.instance_type;
    const instance_language = closest_box.dataset.instance_language;
    const box = closest_box.dataset.box;

    document.dispatchEvent(new CustomEvent('test_words', {
      detail: {
        instance_type: instance_type,
        instance_language: instance_language,
        box: box
      }
    }));    
  });
});

const btns_study_words = document.querySelectorAll('.js-study-words');

btns_study_words.forEach(button =>{
  button.addEventListener('click', () => {
    const closest_box = button.closest('.js-box');
    const instance_type = closest_box.dataset.instance_type;
    const instance_language = closest_box.dataset.instance_language;

    document.dispatchEvent(new CustomEvent('study_words', {
      detail: {
        instance_type: instance_type,
        instance_language: instance_language,
      }
    }));    
  });
});

const btns_clear_box = document.querySelectorAll('.js-clean-box');

btns_clear_box.forEach(button => {
  button.addEventListener('click', ()=>{
    const closest_box = button.closest('.js-box');
    const instance_type = closest_box.dataset.instance_type;
    const instance_language = closest_box.dataset.instance_language;
    const box = closest_box.dataset.box;
    document.dispatchEvent(new CustomEvent('clean_box', {
      detail: {
        instance_type: instance_type,
        instance_language: instance_language,
        box: box,
      }
    }));
  });
});

//  ============================================================================================== CREATE NEW STUDY LIST =======================================================================
const inputStudyListLength = document.querySelector('.js-study-list-length');
const inputRepeatWordsNumber = document.querySelector('.js-rep-words-number');
const selectWordsType = document.querySelector('.js-study-list-words-type');
const selectWordsLevel = document.querySelector('.js-study-list-words-level');
const selectWordsCategory = document.querySelector('.js-study-list-category');
const selectWordsSubCategory = document.querySelector('.js-study-list-subcategories');


//------------------------------------------------------------------------------------ ЛОГІКА ФОРМИ СТВОРЕННЯ СПИСКУ СЛІВ
// Зміна максимальної кількості слів зі списку ПОВТОР при зміні загальної кількості слів в авчальному списку
inputStudyListLength.addEventListener('input', () => {
    inputRepeatWordsNumber.max = Number(inputStudyListLength.value);
    if (inputStudyListLength.value < inputRepeatWordsNumber.value) {
      inputRepeatWordsNumber.value = inputStudyListLength.value
    }
});

async function get_categories_for_new() {
  // Формуємо query string
  // const params = new URLSearchParams({
  //   new_words_type: selectWordsType.value,
  //   new_words_level: selectWordsLevel.value,
  // });

  const response = await fetch(`/get-categories/`, {
    method: 'GET',
    headers: {
      'X-CSRFToken': getCookie('csrftoken') // CSRF не потрібен для GET, але можна залишити
    }
  });

  const data = await response.json();
  // console.log('vocabulary.js -> categories for filtered ', data);
  // gl_category_map = data['subcategories'];
  console.log(data)
  return data;
}

function updateSubcategories(selectedCategory){
  const subcategories_map = JSON.parse(localStorage.getItem('word_categories'))['subcategories'];
  selectWordsSubCategory.innerHTML = '';
  const randomOption = document.createElement("option");
  randomOption.value = 'RANDOM';
  randomOption.textContent = 'RANDOM';
  selectWordsSubCategory.appendChild(randomOption);

  if (selectedCategory && subcategories_map) {
        subcategories_map[selectedCategory].forEach(sub => {
            const option = document.createElement("option");
            option.value = sub['id'];
            option.textContent = sub['name'];
            selectWordsSubCategory.appendChild(option);
        });
  }
}

//Зміна значень в селекті з ПІДКАТЕГОРІЯМИ при виборі КАТЕГОРІЇ слова
selectWordsCategory.addEventListener('change', (event) =>{ 
  const selectedCategory = event.target.value;  
  console.log(selectedCategory);
  updateSubcategories(selectedCategory);  
  
}); 

//------------------------------------------------------------------------------------ CREATE STUDY LIST
function createStudyList(instance_type, instance_language) {
  

  fetch('/create-list/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      instance_type: instance_type,
      instance_language: instance_language,
      study_list_length: inputStudyListLength.value,
      repeat_words_number: inputRepeatWordsNumber.value,
      words_type: selectWordsType.value,
      words_level: selectWordsLevel.value,
      words_category: selectWordsCategory.value,
      words_subcategory: selectWordsSubCategory.value
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

    const listCreateDate = new Date().toLocaleString();
    fillWords(instance_type, instance_language, data.words, listCreateDate);


    hide_slide_blocks();
    get_statistics();
      
  })
  .catch(error => {
    // тут ловимо як мережеві помилки, так і помилки сервера
    console.error('Error:', error);
    if (error.code === 'NO_MORE_WORDS') {
      alert('Слова для вивчення закінчилися!');
    } else {
      alert('Сталася помилка при створенні списку слів.');
    }
    //  global.getUserInfo();
    get_statistics();
  });
}

//------------------------------------------------------------------------------------- FILL WORD CARDS WITH WORDS
function fillWords(instance_type, instance_language, wordsList, createDate){
  console.log(instance_type + ' ' + instance_language)
  const parent_container = document.querySelector(`.js-study-cards-container[data-instance_type="${instance_type}"][data-instance_language="${instance_language}"]`);
  console.log(parent_container)
  const dateItem = document.querySelector(`.js-box[data-box="PROCESS"][data-instance_type="${instance_type}"][data-instance_language="${instance_language}"] .js-study_list_date_container`);
  const container = parent_container.querySelector('.js-flip-card-container');
  
  dateItem.dataset.tooltip = `Список створено: ${createDate}`;

  container.innerHTML = '';
  wordsList.forEach((word, index) => {     
    const item = document.createElement('div');
    item.classList.add('card_container', 'swiper-slide')
   
    if (index === 0) {
        item.classList.add('active'); // Перший елемент каруселі має бути активним
      }

      item.innerHTML =`
      <div class=" card_warpper flip-card"
        data-index="${index + 1}"
        data-word_level="${word.word_level}"
        data-word_type="${word.word_type}"
        data-word_comment="${word.comment}"
        data-word_categories="Category: ${word.word_category} -> Subcategory: ${word.word_subcategory}">
      
            <div class="flip-card-inner js-flip-card">
                <div class="flip-card-front">${word.article + ' ' + word.word}</div>
                <div class="flip-card-back">${word.translation}</div>
                <div class="accordion" id="word-accordion">
                    
                </div>
            </div>
            
        </div>
        `;
        item.querySelector('.js-flip-card').addEventListener('click', (event) => {
          event.currentTarget.closest('.flip-card').classList.toggle('flipped');
        });
      container.appendChild(item);
      
    }
  
  );
  swipers_list[`${instance_type}`][`${instance_language}`].update();
}



//================================================================================================== SLIDE BLOCKS ==========================================================================================================
const slideBlockCreateList = document.querySelector('.js-slide-block-create-list');
const slideBlockTesting = document.querySelector('.js-slide-block-testing');
const slideBlockStudy = document.querySelector('.js-slide-block-study');
const slideBlockCleanBox = document.querySelector('.js-slide-block-clean-box');

document.querySelectorAll('.js-slide-block-hide').forEach( button => {
  button.addEventListener('click', () => {
    hide_slide_blocks();
  })});

function hide_test_slide_block(){
  slideBlockTesting.classList.remove('slide_block_show');
  slideBlockCleanBox.classList.remove('slide_block_show');
}

function hide_slide_blocks(){
  [slideBlockCreateList, slideBlockStudy, slideBlockTesting, slideBlockCleanBox].forEach(slideBlock =>{
      slideBlock.classList.remove('slide_block_show');
    });
}


//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CREATE STUDY LIST SLIDE BLOCK

// -------------------------------- EVENT that create list box button was pushed
document.addEventListener('create_study_list', (event)=>{
    // console.log(event.detail);
    hide_slide_blocks();
    slideBlockCreateList.dataset.caller_instance_type = event.detail.instance_type;
    slideBlockCreateList.dataset.caller_instance_language = event.detail.instance_language;

    const settings = JSON.parse(localStorage.getItem('settings'))[`${slideBlockCreateList.dataset.caller_instance_type}_${slideBlockCreateList.dataset.caller_instance_language}`];
    inputStudyListLength.value = settings['study_list_length'];
    inputRepeatWordsNumber.value = settings['repeat_words_number'];

    
    slideBlockCreateList.classList.add('slide_block_show');
    slideBlockCreateList.querySelector('.js-slide-title').textContent = slideBlockCreateList.dataset.caller_instance_type + ' ' + slideBlockCreateList.dataset.caller_instance_language;
});

//----------------------------------- CLICK on CREATE NEW LIST BUTTON ON SLIDE BLOCK
const createButton = document.querySelector('.js-create-new-list')

createButton.addEventListener('click', (event) =>{
    const instance_type = slideBlockCreateList.dataset.caller_instance_type;
    const instance_language = slideBlockCreateList.dataset.caller_instance_language;

    console.log(instance_language, instance_type);
    if (document.querySelector(`.js-box[data-instance_type="${instance_type}"][data-instance_language="${instance_language}"][data-box="BOX_1"]`).classList.contains('box_overloaded')){
      alert('BOX-1 does not have place')
    } else {
      
      createStudyList(instance_type, instance_language);
    }
    
   
});


//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> STUDY WORDS SLIDE BLOCK

// ---------------------------------- EVENT STUDY BUTTON CLICKED
document.addEventListener('study_words', (event)=>{
  slideBlockStudy.dataset.caller_instance_type = event.detail.instance_type;
  slideBlockStudy.dataset.caller_instance_language = event.detail.instance_language;

  document.querySelectorAll('.js-study-cards-container').forEach(element =>{
    element.classList.add('d-none');
  });
  document.querySelector(`.js-study-cards-container[data-instance_type="${event.detail.instance_type}"][data-instance_language="${event.detail.instance_language}"]`).classList.remove('d-none');
  hide_slide_blocks();
  slideBlockStudy.classList.add('slide_block_show');
});

//------------------------------------------- WORD STUDY SLIDES FOR EVERY LANGUAGE INSTANCE


const instance_types = ['basic', 'custom'];
const instance_languages = ['EN', 'DE']
const swipers_list = {}

function activate_swipers(){
  for (const type of instance_types){
  swipers_list[type] = {}
  for (const language of instance_languages){
    const parent_container = document.querySelector(`.js-study-cards-container[data-instance_type="${type}"][data-instance_language="${language}"]`);
    if (parent_container){
      swipers_list[`${type}`][`${language}`] = new Swiper(parent_container.querySelector('.swiper'), {
        slidesPerView: 1,
          speed: 700,
          freeMode: false,     // якщо true — можна прокручувати з інерцією
          grabCursor: true,
          loop: true,

          pagination: {
            el: parent_container.querySelector('.swiper-pagination'),
          },
          navigation: {
            nextEl: parent_container.querySelector('.js-previous-card'),
            prevEl: parent_container.querySelector('.js-next-card'),
          },
          scrollbar: {
            el: parent_container.querySelector('.swiper-scrollbar'),
          },
          breakpoints: {
              0: {                // мобільні (все, що від 0px)
                direction: 'vertical',
              },
              768: {              // планшети та десктопи (від 768px і більше)
                direction: 'horizontal',
              }}
        });
        const swiper = swipers_list[type][language];
        // слухаємо зміну слайда
        swiper.on('slideChange', () => {

          // const activeIndex = swiper.realIndex; // реальний індекс (без loop-клонів)
          const activeSlide = swiper.slides[swiper.activeIndex]; // сам DOM-елемент\
            if (activeSlide) {
              document.querySelector('.js-card-badge-index').textContent = activeSlide.querySelector('.flip-card').dataset.index;
              document.querySelector('.js-card-badge-word_type').textContent = activeSlide.querySelector('.flip-card').dataset.word_type;
              const word_level_element = document.querySelector('.js-card-badge-word_level')
              word_level_element.textContent = activeSlide.querySelector('.flip-card').dataset.word_level;
              word_level_element.dataset.word_level = activeSlide.querySelector('.flip-card').dataset.word_level;
            }

        });
    }
  }
}
}



//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> TEST WORD SLIDE BLOCK

// -------------------------------- EVENT that test words butoon on some box was pressed
document.addEventListener('test_words', (event)=>{
  hide_slide_blocks();
  slideBlockTesting.dataset.caller_instance_type = event.detail.instance_type;
  slideBlockTesting.dataset.caller_instance_language = event.detail.instance_language;
  slideBlockTesting.dataset.caller_box = event.detail.box;


  slideBlockTesting.classList.add('slide_block_show');
  document.querySelector('.js-feedback').innerHTML = '';
  document.querySelector('.js-show-word').textContent = '';
  document.querySelector('.js-test-answer').disabled = true;
  slideBlockTesting.querySelector('.js-slide-title').textContent = slideBlockTesting.dataset.caller_instance_type + ' ' + slideBlockTesting.dataset.caller_instance_language + ' ' + slideBlockTesting.dataset.caller_box;
});

// ------------------------------------------------------------------------------------------------ TESTING WORDS

function showEmptyBoxMessage(instance_type, instance_language, box_name) {
    const testing_days_limit = JSON.parse(localStorage.getItem('settings'))[`${instance_type}_${instance_language}`]['testing_days_limit'];
    document.querySelector('.js-feedback').innerHTML = `
        <div class="text-danger">В коробці ${box_name} немає слів для тестування!!!<br>
        Треба почекати <strong>${testing_days_limit}</strong> днів після потрапляння слова до коробки, згідно з налаштуваннями профілю...</div>
    `;
}


function is_next_box_ok(instance_type, instance_language, testing_box_name){
  const testing_box = document.querySelector(`.js-box[data-instance_type="${instance_type}"][data-instance_language="${instance_language}"][data-box="${testing_box_name}"]`)
    console.log(testing_box)
    const next_box = testing_box.dataset.next_box;
    console.log(next_box)
    const statistics = JSON.parse(localStorage.getItem('statistics'))[instance_type][instance_language];
    const next_box_length = statistics[next_box];
    const next_box_length_limit = statistics[`${next_box}_LIMIT`];
    if (next_box && next_box_length == next_box_length_limit) {
      
      return false
    }

    return true

}

document.querySelector('.js-next-word').addEventListener('click', () => {
    const instance_type = slideBlockTesting.dataset.caller_instance_type;
    const instance_language = slideBlockTesting.dataset.caller_instance_language;
    const testing_box_name = slideBlockTesting.dataset.caller_box;
    
    if (!is_next_box_ok(instance_type, instance_language, testing_box_name)){
      alert('В НАСТУПНОМУ БОКСІ НЕМАЄ МІСЦЯ');
    }   
    
    getNextWord(instance_type, instance_language, testing_box_name);
});


async function getNextWord(instance_type, instance_language, box_name) {
    try {
        // можна показати "завантаження..."
        document.querySelector('.js-spinner-testing').classList.remove('d-none');

        const response = await fetch(`/get-box-word/?box=${box_name}&instance_type=${instance_type}&instance_language=${instance_language}`);

        document.querySelector('.js-spinner-testing').classList.add('d-none');

        if (!response.ok) {
            console.warn(`Не вдалося отримати слово, статус: ${response.status}`);
            showEmptyBoxMessage(instance_type, instance_language, box_name);
            document.querySelector('.js-test-answer').disabled = true;
            return;
        }

        const data = await response.json();

        if (!data?.word) {
            showEmptyBoxMessage(instance_type, instance_language, box_name);
            document.querySelector('.js-test-answer').disabled = true;
            return;
        }

        const word = data.word;
      
        document.querySelector('.js-show-word').textContent = `${word.article} ${word.word}`;
        document.querySelector('.js-input-answer').dataset.wordId = word.id;
        document.querySelector('.js-test-answer').disabled = false;

    } catch (error) {
        console.error('Помилка запиту:', error);
        document.querySelector('.js-feedback').textContent = "⚠️ Сталася помилка при отриманні слова.";
    }
}

//------------------------------------------------------------- CHECKING IF ANSWER IS CORRECT
document.querySelector('.js-test-answer').addEventListener('click',async () => {
  const instance_type = slideBlockTesting.dataset.caller_instance_type;
  const instance_language = slideBlockTesting.dataset.caller_instance_language;
  const testing_box_name = slideBlockTesting.dataset.caller_box;

  if (!is_next_box_ok(instance_type, instance_language, testing_box_name)){
      alert('В НАСТУПНОМУ БОКСІ НЕМАЄ МІСЦЯ');
  } else {
    const input = document.querySelector('.js-input-answer');
    const word_id = input.dataset.wordId
    const answer = input.value.trim();
    const feedback = document.querySelector('.js-feedback');

    const clear_input = () => {
      input.value = ''
    }

    if (!answer) {
        feedback.innerHTML = `<div class="text-danger">Введи відповідь!</div>`;
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
                instance_type: instance_type,
                instance_language: instance_language,
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
            feedback.innerHTML = '<span class="text-success">Правильно! 🎉</span>';
            
            
        } else {
            feedback.innerHTML = `<spn class="text-danger">Відповідь ${answer} є НЕПРАВИЛЬНА. \n Правильна відповідь: ${data.correct_answer}</span>`;
            
        }
        clear_input(); // очищаємо інпут
        get_statistics();
        getNextWord(instance_type, instance_language, testing_box_name);

    } catch (err) {
        console.error('Помилка при відправці відповіді:', err);
        feedback.textContent = 'Помилка при перевірці відповіді';
    }
  }     
});


//============================================================================== CLEAN BOX 
const btn_clean_box = document.querySelector('.js-clean-box-btn');
// ----------------------------------------- EVENT when some clear box badge button clicked
document.addEventListener('clean_box', (event)=>{
  slideBlockCleanBox.dataset.caller_instance_type = event.detail.instance_type;
  slideBlockCleanBox.dataset.caller_instance_language = event.detail.instance_language;
  slideBlockCleanBox.dataset.caller_box = event.detail.box;
  const box_statistics = JSON.parse(localStorage.getItem('statistics'))[`${event.detail.instance_type}`][`${event.detail.instance_language}`][`${event.detail.box}`];
  console.log('EVENT LISTENING CLEANING BOX, box statistics = ', box_statistics);
  if (box_statistics == 0) {
    btn_clean_box.disabled = true;
  } else {
    btn_clean_box.disabled = false;
  }
  
  hide_slide_blocks();
  slideBlockCleanBox.classList.add('slide_block_show');
});
//--------------------------------------------- CLICKED CLEN BOX ON SLIDE BLOCK CLEAN
btn_clean_box.addEventListener('click', () => {
  const instance_type = slideBlockCleanBox.dataset.caller_instance_type;
  const instance_language = slideBlockCleanBox.dataset.caller_instance_language;
  const current_box = slideBlockCleanBox.dataset.caller_box;
  fetch('/clean-box/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      instance_type: instance_type,
      instance_language: instance_language,
      current_box: current_box,
      words_number: document.querySelector('.js-clean-box-number').value
    })
  })
  .then(response => {
    if (!response.ok) { // якщо HTTP статус не 2xx
      return response.json().then(errData => {
        // обробляємо помилку
        throw errData; 
      });
    }
    // getUserInfo();
    return get_statistics();
    // 
  })
  .then(statistics =>{
    console.log('STATISTICS = ', statistics);
    const boxStatistics = statistics[instance_type][instance_language][current_box];
    if (boxStatistics == 0) {
      btn_clean_box.disabled = true;
    }
  })
  .catch(error => {
    // тут ловимо як мережеві помилки, так і помилки сервера
    console.error('Error:', error);
    alert(error);
  });
});

//================================================================================================= AFTER CONTENT LOADED ACTIONS =============================================================================================

const boxesNamesUkr = {
  'BOX_1': 'КОРОБКА-1',
  'BOX_2': 'КОРОБКА-2',
  'BOX_3': 'КОРОБКА-3',
  'LEARNT': 'ВИВЧЕНІ',
  'REPEAT': 'ПОВТОР',
  'PROCESS': "В ПРОЦЕСІ ВИВЧЕННЯ"
}

// ПОКАЗ ІНФИ ПРО БЛОК ПРИ НАВЕДЕННІ НА КОРОБКУ====================================
const vocabularyBadge = document.querySelector('.js-block-badge');
const boxes = document.querySelectorAll('.js-box');

boxes.forEach( box => {
  box.addEventListener('mouseenter', () =>{
    vocabularyBadge.textContent = boxesNamesUkr[box.dataset.box];
    vocabularyBadge.classList.add('block_badge_show');
  });

  box.addEventListener('mouseleave', () =>{
    vocabularyBadge.textContent = '';
    vocabularyBadge.classList.remove('block_badge_show');
  });
});

document.addEventListener('DOMContentLoaded', async function () {

  const instance = document.querySelector('#js-user-info').textContent === 'vocabulary' ? 'custom' : 'basic';

  const INSTANCES_LANGUAGES = ['EN', 'DE'];

   for (const language of INSTANCES_LANGUAGES){
    document.querySelector(`.js-study-cards-container[data-instance_language="${language}"]`).dataset.instance_type = instance;
   }
   activate_swipers();

  for (const language of INSTANCES_LANGUAGES){
      try {
       

        const response = await fetch(`/get-study-list/?instance_type=${instance}&instance_language=${language}`);

        

        if (!response.ok) {
            console.warn(`Не вдалося отримати слово, статус: ${response.status}`);
            
            return;
        }

        const data = await response.json();

        if (!data?.words) {
            console.warn(`NO WORDS IN RESPONSE...`);
            return;
        }

        const words = data.words;
        console.log(instance, language)
        fillWords(instance, language, words, data.create_date);
  
      
        

    } catch (error) {
        console.error('Помилка запиту:', error);
        document.querySelector('.js-feedback').textContent = "⚠️ Сталася помилка при отриманні слова.";
    }

  }
  

  console.log(await get_categories_for_new())
  
});

