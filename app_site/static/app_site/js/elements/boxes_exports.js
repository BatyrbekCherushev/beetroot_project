
export function refresh_instance_statistics(instance_type, instance_language, instance_data){
    // console.log('REFRESHING STATISTICS for:', instance_type, instance_language)
    const settings = JSON.parse(localStorage.getItem('settings'))[`${instance_type}_${instance_language}`];
    // console.log(instance_data);
    if (instance_data && settings) {

      const categories = ['REPEAT','PROCESS','BOX_1', 'BOX_2', 'BOX_3', 'LEARNT']
      for (const category of categories){
            // console.log(category)
            let text = instance_data[category];
            const box_element = document.querySelector(`.js-box[data-instance_type="${instance_type}"][data-instance_language="${instance_language}"].box-${category}`);
            // console.log(box_element)

            if (['BOX_1', 'BOX_2', 'BOX_3', 'LEARNT'].includes(category)) {
              if (category != 'LEARNT') {
                text = text + ` / ${settings[`${category.toLowerCase()}_limit`]}`
              }
              
              if(category == 'LEARNT') {
                text = ' ' + text + ` / ${instance_data[`${category}_freezed`]}❄️`
              }

              if (box_element){
                box_element.querySelector('.js-box-words-testible').dataset.tooltip = instance_data[`${category}_usable`] + " слів доступно для тестування";
              }
              
            }
              if (box_element){
                box_element.querySelector(`.js-box-text-${category}`).textContent = text;
              }
              
          }
      }

      paintBoxes(instance_type, instance_language, instance_data);
}

function paintBoxes(instance_type, instance_language, data){
  const settings = JSON.parse(localStorage.getItem('settings'))[`${instance_type}_${instance_language}`];
  // console.log('PAINT_BOXES ---> income settings:', settings)
  for (const category of ['REPEAT','PROCESS', 'BOX_1', 'BOX_2', 'BOX_3', 'LEARNT']) {
    // console.log(instance)
    const currentBox = document.querySelector(`.js-box[data-instance_type="${instance_type}"][data-instance_language="${instance_language}"][data-box="${category}"]`);
    // console.log(category)
    // console.log(currentBox)
    if (currentBox){
      if (data[category] == 0) {
        currentBox.classList.add('box_empty');
      
      } else {
        currentBox.classList.remove('box_empty');
      }
      if (data[category] >= settings[`${category.toLowerCase()}_limit`]) {
      currentBox.classList.add('box_overloaded');
        }
      else {
        currentBox.classList.remove('box_overloaded');
      }
    }
  }
}