import { getCookie } from './global.js';
import * as boxes_and_slides from  './elements/boxes_and_slide_blocks.js'

//=============================================================================================== EDIT or ADD WORD ===============================================================================
const btn_add_word = document.querySelector('.js-btn-add-word');
const btn_modify_word = document.querySelector('.js-btn-modify-word');
const btn_clear_fields = document.querySelector('.js-edit-clear-fields');
const input_edit_language = document.querySelector('.js-edit-language');
const input_edit_word_type = document.querySelector('.js-edit-word-type');
const input_edit_word_level = document.querySelector('.js-edit-word-level');
const input_edit_article = document.querySelector('.js-edit-article');
const input_edit_transcription = document.querySelector('.js-edit-transcription');
const input_edit_word = document.querySelector('.js-edit-word');
const input_edit_translation = document.querySelector('.js-edit-translation');
// const textEditTranslationOptions = document.querySelector('.js-edit-translation-options');
const input_edit_category = document.querySelector('.js-edit-category');
const input_edit_sub_category = document.querySelector('.js-edit-subcategory');
const input_edit_comment = document.querySelector('.js-edit-comment');
const input_edit_synonims = document.querySelector('.js-edit-synonims');
const input_edit_ID = document.querySelector('.js-edit-id');
const input_edit_status = document.querySelector('.js-edit-status');
const search_feedback = document.querySelector('.js-search-feedbcak');



//============================================================================================ SEARCH WORD  ======================================================================================
//-------------------------------------------------------- ПОКАЗАТИ ДОДАТКОВЫ КНОПКИ БЫЛЯ ПОЛЯ ВВОДУ СЛОВА ЯКЩО ОБРАНА НЫМЕЦЬКА МОВА
input_edit_language.addEventListener('change', ()=>{
  // console.log('CHANGED LANGUAGE', input_edit_language.value);
  const umlaut_block = document.querySelector('.js-umlaut');
  if (input_edit_language.value == 'DE') {
    umlaut_block.classList.remove('d-none');
  }else {
    umlaut_block.classList.add('d-none');
  }
});

document.querySelectorAll('.js-umlaut-letter').forEach(umlaut_letter =>{
  umlaut_letter.addEventListener('click', ()=>{
    input_edit_word.value += umlaut_letter.textContent;
  })
});


//--------------------------------------------------------------------------------- EDIT CATEGORIES AUTOCHANGE
const select_search_category = document.querySelector('.js-edit-category');
const select_search_subcategory = document.querySelector('.js-edit-subcategory');

function update_search_subcategories(selectedCategory){
  const subcategories_map = JSON.parse(localStorage.getItem('word_categories'))['subcategories'];
  select_search_subcategory.innerHTML = '';
  const randomOption = document.createElement("option");
  randomOption.value = 'RANDOM';
  randomOption.textContent = 'RANDOM';
  select_search_subcategory.appendChild(randomOption);

  if (selectedCategory && subcategories_map) {
        subcategories_map[selectedCategory].forEach(sub => {
            const option = document.createElement("option");
            option.value = sub['id'];
            option.textContent = sub['name'];
            select_search_subcategory.appendChild(option);
        });
  }
  select_search_subcategory.value = 'RANDOM';
}

//Зміна значень в селекті з ПІДКАТЕГОРІЯМИ при виборі КАТЕГОРІЇ слова
select_search_category.addEventListener('change', (event) =>{ 
  const selectedCategory = event.target.value;  
  console.log(selectedCategory);
  update_search_subcategories(selectedCategory);  
  
}); 




document.querySelector('.js-btn-search-word').addEventListener('click', async () =>{
    input_edit_ID.value = '';
    input_edit_status.value = '';
    btn_add_word.disabled = true;
    btn_modify_word.disabled = true;

    const params = new URLSearchParams({
        language: input_edit_language.value,
        word_type: input_edit_word_type.value,
        word_level: input_edit_word_level.value,
        article: input_edit_article.value,
        transcription: input_edit_transcription.value,
        word: input_edit_word.value,
        translation: input_edit_translation.value,
        // translation_options: textEditTranslationOptions.value,
        category: input_edit_category.value,
        sub_category: input_edit_sub_category.value,
        comment: input_edit_comment.value,
        synonims: input_edit_synonims.value,
    });

    const response = await fetch(`/get-custom-words/?${params.toString()}`, {
    method: 'GET',
    headers: {
      'X-CSRFToken': getCookie('csrftoken') // CSRF не потрібен для GET, але можна залишити
    }
  });

  const data = await response.json();
  const tableSearchResults = document.querySelector('.js-search-results-list');
  tableSearchResults.innerHTML = '';
  
  search_feedback.textContent = '';
  console.log(data);

  if (data['words']) {
    data['words'].forEach((word,index)  =>{
      const tableItem = document.createElement("tr");
      
      tableItem.classList.add('js-found-word', 'search_word_item');
      for (let property in word){
        tableItem.setAttribute(`data-${property}`, word[property]);
      }
      //number
      const cell_number = document.createElement("td");
      cell_number.textContent = index + 1;
      tableItem.appendChild(cell_number);

      // LANGUAGE
      if (word['language']) {
        const cell_language = document.createElement("td"); 
        cell_language.textContent = word['language'];
        tableItem.appendChild(cell_language);
      }

      // WORD LEVEL
        const word_level = word['word_level'] || '---'
        const cell_word_level = document.createElement("td");
        cell_word_level.textContent = word_level;
        tableItem.classList.add(`search_word_item_${word_level}`)
        tableItem.appendChild(cell_word_level);

      // WORD TYPe
      const word_type = word['word_type'] || "---";
      const cell_word_type = document.createElement("td");
      cell_word_type.textContent = word_type;      
      tableItem.appendChild(cell_word_type);
      
      // WORD
      if (word['word']){
        const cell_word = document.createElement("td"); 
        cell_word.textContent = word['article'] + ' ' + word['word']
        tableItem.appendChild(cell_word);
      }

      

      // WORD STATUS
      if (word['status']) {
        const cell_word_status = document.createElement("td");
        cell_word_status.textContent = word['status'] != "" ? word['status'] :  '----';
        // cell_word_status.textContent = '----';
        tableItem.appendChild(cell_word_status);
      }
      

      tableSearchResults.appendChild(tableItem);
    });

    document.querySelectorAll('.js-found-word').forEach(element => {
      element.addEventListener('click', () => {
        btn_modify_word.disabled = false;
        const activeElement = document.querySelector('.search_word_item.active');
        if (activeElement){
          activeElement.classList.remove('active');
        }
        element.classList.add('active');

        input_edit_language.value = element.dataset.language;
        input_edit_word_type.value = element.dataset.word_type;
        input_edit_word_level.value = element.dataset.word_level;
        input_edit_category.value = element.dataset.word_category;
        update_search_subcategories(input_edit_category.value);
        input_edit_sub_category.value = element.dataset.word_subcategory;
        
        input_edit_article.value = element.dataset.article
        input_edit_word.value = element.dataset.word;
        input_edit_transcription.value = element.dataset.transcription
        input_edit_translation.value = element.dataset.translation;
        input_edit_comment.value = element.dataset.comment;
        input_edit_synonims.value = element.dataset.synonims;
        // textEditTranslationOptions.value = element.dataset.translation_options;
        input_edit_ID.value = element.dataset.id;
        input_edit_status.value = element.dataset.status;

      });
    });
    document.querySelector('.table_search_results_wrapper').scrollIntoView({ behavior: "smooth" });
    
  }

  if (data['status'] == 'error') {
    btn_add_word.disabled = false;
    
    search_feedback.textContent = 'NO WORDS FOUND WITH SUCH A FILTER CONDITIONS';
    search_feedback.classList.add('text-danger');
    tableSearchResults.innerHTML = '';
  }
});

//  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   ADD NEW CUSTOM WORD
btn_add_word.addEventListener('click', () =>{
  const body_data = {
        language: input_edit_language.value,
        word_type: input_edit_word_type.value,
        word_level: input_edit_word_level.value,
        article: input_edit_article.value,
        transcription: input_edit_transcription.value,
        word: input_edit_word.value,
        ukrainian: input_edit_translation.value,
        // translation_options: textEditTranslationOptions.value,
        category: input_edit_category.value,
        sub_category: input_edit_sub_category.value,
        comment: input_edit_comment.value,
        synonims: input_edit_synonims.value,
    }
    if (!body_data['word']) {
        console.log(' OBLIGATORY FIELD')
        return
    }
  fetch('/add-word/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        language: input_edit_language.value,
        word_type: input_edit_word_type.value,
        word_level: input_edit_word_level.value,
        article: input_edit_article.value,
        transcription: input_edit_transcription.value,
        word: input_edit_word.value,
        translation: input_edit_translation.value,
        // translation_options: textEditTranslationOptions.value,
        category: input_edit_category.value,
        sub_category: input_edit_sub_category.value,
        comment: input_edit_comment.value,
        synonims: input_edit_synonims.value,
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
    
    
      
  })
  .catch(error => {
    // тут ловимо як мережеві помилки, так і помилки сервера
    console.error('Error:', error);
    alert(error);
    
  });
});

//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  MODIFY EXISTING CUSTOM WORD 

btn_modify_word.addEventListener('click', ()=> {
  fetch('/modify-word/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
        word_ID: input_edit_ID.value,
        language: input_edit_language.value,
        word_type: input_edit_word_type.value,
        word_level: input_edit_word_level.value,
        article: input_edit_article.value,
        transcription: input_edit_transcription.value,
        word: input_edit_word.value,
        translation: input_edit_translation.value,
        // translation_options: textEditTranslationOptions.value,
        category: input_edit_category.value,
        sub_category: input_edit_sub_category.value,
        comment: input_edit_comment.value,
        synonims: input_edit_synonims.value,
        status: input_edit_status,
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
    search_feedback.textContent = 'Modification of the word was successful!!!';
    search_feedback.classList.remove('text-danger');
    search_feedback.classList.add('text-success');
    
      
  })
  .catch(error => {
    // тут ловимо як мережеві помилки, так і помилки сервера
    console.error('Error:', error);
    alert(error);
    
  });
});

// >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>==================================== CLEAR FIELDS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
function clear_filter_fields(){
  const tableSearchResults = document.querySelector('.js-search-results-list');
  const search_feedback = document.querySelector('.js-search-feedbcak');
  tableSearchResults.innerHTML = '';
  input_edit_language.value = input_edit_language.querySelector("option[selected]").value;
  input_edit_word_type.value = input_edit_word_type.querySelector("option[selected]").value;
  input_edit_word_level.value = input_edit_word_level.querySelector("option[selected]").value;
  input_edit_category.value = '';
  update_search_subcategories();
  input_edit_article.value = input_edit_article.defaultValue;
  input_edit_word.value = input_edit_word.defaultValue;
  input_edit_transcription.value = input_edit_transcription.defaultValue;
  input_edit_translation.value = input_edit_translation.defaultValue;
  input_edit_comment.value = input_edit_comment.defaultValue;
  input_edit_synonims.value = input_edit_synonims.defaultValue;
  input_edit_ID.value = input_edit_ID.defaultValue;
  input_edit_status.value = input_edit_status.defaultValue;
  search_feedback.textContent = '';

}

btn_clear_fields.addEventListener('click', ()=>{
  clear_filter_fields();
});