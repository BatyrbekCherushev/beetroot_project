import {refresh_instance_statistics} from  './elements/boxes_exports.js'

//================================================================================================= GLOBAL VARIABLES ====================================================================


export function getCookie(name) {
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


//----------------------------------------------------------------------------------- MODALS
const myModal = new bootstrap.Modal('#modal_message', {
    keyboard: false
  })

export function show_modal_message(type='secondary', title='NO TITLE', message='NO MESSAGE') {
  const modalEl = document.getElementById('modal_message');
  const modalTitle = document.querySelector('.my_modal_title');
  const modalBody = document.querySelector('.my_modal_body');
  
  modalBody.innerHTML = `<p class="text-${type}">${message}</p>`;
  modalTitle.innerHTML = `<span class="text-${type}">${title}</span>`;

  myModal.show();
}

const statistics_modal = new bootstrap.Modal("#modal_statistics", {
  keyboard: false
});

export function show_modal_statistics(type='seconadry', title='NO TITLE', message='NO MESSAGE', data={}) {
  const modal_element = document.getElementById('modal_statistics');
  const modal_title = modal_element.querySelector('.my_modal_title');
  const modalBody = modal_element.querySelector('.my_modal_body');
  modalBody.innerHTML = `
    <p class="statistics_total">Всього слів: ${data['TOTAL']}</p>
    <p class="statistics_new">Нових слів: ${data['NEW']}</p>
    <p class="statistics_learnt">Вивчено слів: ${data['LEARNT']}</p>
  `;
  statistics_modal.show();
}

// show_modal_message();

//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET FULL USER INFO
export async function getUserInfo(){
  fetch('/get-user-info/')
    .then(response => response.json())
    .then(data => {
      // console.log(data)
      localStorage.setItem('settings', JSON.stringify(data.settings));
      localStorage.setItem('statistics', JSON.stringify(data.statistics))
      localStorage.setItem('player_profile', JSON.stringify(data.player_profile));
      localStorage.setItem('word_categories', JSON.stringify(data.categories));
      // console.log(data)
      
      document.dispatchEvent(new CustomEvent('user_info_refreshed',{
        detail:{
          statistics: data.statistics,
          settings: data.settings,
          player_info: data.player_info
        }
      }));
    });
}

export async function get_settings(){
  try {
    const response = await fetch('/get-settings');
    if (!response.ok) throw new Error('Failed to fetch settings');
    const data = await response.json();

    // console.log('GOT SETTINGS: ', data);
    document.dispatchEvent('settings_refreshed', {
      detail: data
    });
    localStorage.setItem('settings', data);
    return data;
  }catch (error) {
    console.error('Error fetching statistics:', error);
    throw error; // проброс помилки далі
  }
}

//>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET STATISTICS FOR BOXES
export async function get_statistics(){
  
  try {
    const response = await fetch('/get-statistics/');
    if (!response.ok) throw new Error('Failed to fetch statistics');

    const data = await response.json();

    // Генеруємо подію
    // console.log('GET STATISTICS DATA:',data)
    document.dispatchEvent(new CustomEvent('statistics_refreshed', { detail: data }));

    return data; // ✅ повертаємо результат
  } catch (error) {
    // console.error('Error fetching statistics:', error);
    throw error; // проброс помилки далі
  }
}

function showLocalStorage(){
  console.log(`Showing local storage ${localStorage.getItem("daily_words")}`)
  console.log(`Showing local storage ${localStorage.getItem("daily_words_date")}`)
}




async function init(){
  getUserInfo();
  // get_settings();
  // get_statistics();
  
}


// ==================================================================================== EVENT LISTENERS =====================================================================
// ========================= EVENT user_info_refreshed
document.addEventListener('user_info_refreshed',(event)=>{
  const statistics_data = event.detail['statistics'];
  
  for (const instance_type in statistics_data){
    for (const instance_language in statistics_data[instance_type]){
      const data = statistics_data[instance_type][instance_language];
      
      // if (Object.keys(data).length === 0) {
      //   console.log(`Інстанс "${instance}" порожній`);
      //   continue; // пропускаємо цей інстанс
      // }

      refresh_instance_statistics(instance_type, instance_language, data)
    }
  }
  
});

// ========================= EVENT statistics_refreshed
document.addEventListener('statistics_refreshed',(event)=>{
 const statistics_data = event.detail;
//  console.log(statistics_data)
  
  for (const instance_type in statistics_data){
    for (const instance_language in statistics_data[instance_type]){
      const data = statistics_data[instance_type][instance_language];
      
      refresh_instance_statistics(instance_type, instance_language, data)
    }
  }
  
});

// ========================= EVENT settings_refreshed
document.addEventListener('settings_refreshed', (event)=>{

});

document.addEventListener('DOMContentLoaded', async () => {
    init();
    // localStorage.setItem('userInfo', JSON.stringify(document.querySelector('#js-user-info').textContent)) 
    

    // document.querySelector('.js-show-settings').textContent = await JSON.stringify(window.userSettings);
});


