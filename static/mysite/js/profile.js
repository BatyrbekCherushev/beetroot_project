const inputs_study_list_length = document.querySelectorAll('.js-settings-study-list-length');
const inputs_repeat_words_number = document.querySelectorAll('.js-settings-rep-num');

// Зміна максимальної кількості слів зі списку ПОВТОР при зміні загальної кількості слів в авчальному списку
inputs_study_list_length.forEach(item =>{
    item.addEventListener('input', () => {
        const instance = item.dataset.instance;
        const language = item.dataset.language;
        const item_repeat = document.querySelector(`.js-settings-rep-num[data-instance="${instance}"][data-language="${language}"]`);
        item_repeat.max = Number(item.value);
})
});



