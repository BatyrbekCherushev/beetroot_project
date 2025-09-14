const inputRepeatWordsNumber = document.querySelector('#settings-rep_words_number');
const inputNewWordsNumber = document.querySelector('#settings-new_words_number');
const inputStudyListLength = document.querySelector('#settings-study-list-length');

// Автоматична зміна кількості слів зі списку НОВІ при зміні кількості слів зі списку ПОВТОР
inputRepeatWordsNumber.addEventListener('input', () => {
    // inputNewWordsNumber.value = Math.max(0, Number(inputStudyListLength.value) - Number(inputRepeatWordsNumber.value));    
});


// Зміна максимальної кількості слів зі списку ПОВТОР при зміні загальної кількості слів в авчальному списку
inputStudyListLength.addEventListener('input', () => {
    inputRepeatWordsNumber.max = Number(inputStudyListLength.value);
});
