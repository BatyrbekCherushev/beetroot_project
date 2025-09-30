import { getCookie, show_modal_message } from './global.js';

const btn_fight = document.querySelector('.js-fight');

// ========================================================================================== FIND BATTLE ===================================================================
function refresh_character(character_type, info){
    const character_panel = document.querySelector(`.js-character-${character_type}`);
    // console.log(info)
    character_panel.querySelector('.stats_hitpoints .progress-bar').style.width = `${info['hitpoints']}%`;
    character_panel.querySelector('.stats_endurance .progress-bar').style.width = `${info['endurance']}%`;
    character_panel.querySelector('.stats_mana .progress-bar').style.width = `${info['mana']}%`;
    character_panel.querySelector('.stats_name').textContent = `${info['name']}` || 'NONAME';

    const skills_panel = document.querySelector('.js-player-skills');
    
    // console.log(skills_panel);
    if (info['skills'] && character_type == 'player') {
        skills_panel.innerHTML = '';
        info['skills'].forEach(element => {
            // console.log(element)
            const skill_element = document.createElement('div');
            skill_element.innerHTML = `<label class="skill">
                        <input type="radio" name="skill" value="${element}" />
                        <svg fill="#000000"  version="1.2" baseProfile="tiny" id="_x31_" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="-63 65 128 128" xml:space="preserve"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M-27.5,137.1h-25.6c-4.2,0-7.5,3.3-7.5,7.5s3.3,7.5,7.5,7.5h25.6c4.2,0,7.5-3.3,7.5-7.5S-23.3,137.1-27.5,137.1z M-53.1,110 H-35V94.9h-18.1c-4.2,0-7.5,3.3-7.5,7.5C-60.7,106.7-57.3,110-53.1,110z M-27.5,158.2h-18.1c-4.2,0-7.5,3.3-7.5,7.5 c0,4.2,3.3,7.5,7.5,7.5h18.1c4.2,0,7.5-3.3,7.5-7.5C-19.9,161.5-23.3,158.2-27.5,158.2z M28.3,113L4.9,89.6l0,0 c-1.4-1.4-3.3-2.3-5.3-2.3h-21.1c-4.2,0-7.5,3.3-7.5,7.5v28.7c0,4.2,3.3,7.5,7.5,7.5s7.5-3.3,7.5-7.5V107l0,0c0-1.7,1.4-3,3-3 s3,1.4,3,3l0,0l0,0c0,18.2,14.9,33.2,33.2,33.2c1.7,0,3,1.4,3,3s-1.4,3-3,3c-14.3,0-26.8-7.7-33.6-19.2c-0.9,3.2-2.9,5.9-5.6,7.7 c0,0,0,26.7,0,30.9c0,2.7-0.9,5.4-2.3,7.5H5.7c9.3,0,17.6-4.8,22.6-12.1h36V113H28.3z M-53.1,131.1h20.4c-1.5-2.1-2.3-4.8-2.3-7.5 V116h-18.1c-4.2,0-7.5,3.3-7.5,7.5S-57.3,131.1-53.1,131.1z"></path> </g></svg>
                    </label>`;
            skills_panel.appendChild(skill_element);
            
        });
    }

}
// -------------------------------------------------------------------------- FIND PVP BATTLE
let battle_found = false;

async function find_pvp_battle() {
    try {
        const res = await fetch('/find-pvp-battle/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        const data = await res.json();
        // console.log(data)
        return data;
        
        
    } catch (err) {
        console.error(err);
        battle_found = true; // зупиняємо цикл при помилці
    }
}


// функція паузи
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


document.querySelector('.js-find-battle').addEventListener('click', async ()=>{
    let data
    let battle_found = false;
    while (!battle_found) {
        document.querySelector('.js-spinner').classList.remove('d-none');
        data = await find_pvp_battle();
        if (data.battle_info['battle_status']== 1) {
            console.log('Waiting for opponent...');
            await sleep(3000); // пауза 1 секунда між запитами
        } else if (data.battle_info['battle_status'] == 2) {
            battle_found = true;
            show_modal_message('success', 'ALL PLAYERS READY', 'ALL PLAYERS READY YOU CAN FIGHT');
            document.querySelector('.js-spinner').classList.add('d-none');
            btn_fight.dataset.battle_id = data.battle_info['battle_id'];
            document.querySelector('.js-arena-container').classList.remove('d-none');
            const player_position = data.player_status;
            const enemy_position = player_position == 'player_1' ? 'player_2': 'player_1';
            refresh_character('player', data.battle_info[`${player_position}`]);
            refresh_character('enemy', data.battle_info[`${enemy_position}`]);
        }    
    }
    
    
    
});

// ------------------------------------------------------------------------------------------- STOP SEARCH BATTLES
document.querySelector('.js-stop-search-battles').addEventListener('click', ()=>{
    battle_found = true;
    show_modal_message('warning', 'SEARCH STOP', 'The search of battle was stopped!!!')
});

// ------------------------------------------------------------------------------------------- CLOSE BATTLES

document.querySelector('.js-close-battles').addEventListener('click', async ()=>{
    try {
        const res = await fetch('/close-battles/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        if (!res.ok) {
            console.warn(`Не вдалося отримати слово, статус: ${res.status}`);
            
            return;
        }
        const data = await res.json();
        show_modal_message('success', '', data['message']);
    } catch (err) {
        console.error(err);       
    }
});


// ================================================================================================= FIGHT =====================================================================================
async function fight(selected_skill, player_attack, enemy_attack){
    console.log('ATTACK = ', selected_skill, player_attack, enemy_attack)
       
    
    try {
            const response = await fetch('/fight-pvp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')  // функція getCookie повинна бути визначена
                },
                body: JSON.stringify({
                    'battle_id': btn_fight.dataset.battle_id,
                    // 'battle_round': btn_fight.dataset.round,
                    'skill_id': selected_skill,
                    'player_attack': player_attack,
                    'enemy_attack': enemy_attack

                    
                })
            });
            if (!response.ok) {
                // Сервер повернув помилку (400, 404 тощо)
                const errorText = await response.text();  // отримуємо тіло відповіді як текст
                show_modal_message('danger', 'ПОМИЛКА', errorText)
                // console.error(`Помилка сервера ${response.status}:`, errorText);
                return;
            }
    
            const data = await response.json();
            console.log('FIGHT REQUEST DATA: ', data )
            return data;
    
            
            
    
        } catch (err) {
            show_modal_message('danger', 'ПОМИЛКА З СЕРВЕРА', err)
            // console.error('Помилка при відправці відповіді:', err);
        }
}
btn_fight.addEventListener('click', async ()=>{
    let status_1 = false;
    const selected_skill = document.querySelector('input[name="skill"]:checked');
    const my_attack = document.querySelector('input[name="my_strike"]:checked');
    const enemy_attack = document.querySelector('input[name="enemy_strike"]:checked');

    if (selected_skill){
        const skill_id = selected_skill.value;

        while (!status_1){
            const data = await fight(skill_id, my_attack.value, enemy_attack.value);
            console.log(data);
            
            const battle_status = data.battle_info['battle_status'];
            if (battle_status == 3) // PENDING
            {
                show_modal_message('success', 'BATTLE FINISHED')
                document.querySelector('.js-arena-container').classList.add('d-none');
                return
            }
            if (data.battle_info['round_status'] == 1){
                status_1 = true;
                const player_position = data['player_status'];
                const enemy_position = player_position == 'player_1' ? 'player_2': 'player_1';
                refresh_character('player', data.battle_info[`${player_position}`]);
                refresh_character('enemy', data.battle_info[`${enemy_position}`]);
                document.querySelector('.js-arena-title').textContent = data.battle_info['round_number'];
                
                show_modal_message('success', 'NEW ROUND', `NEW RPOND - ${data.battle_info['round_number']}`)
            }        
            await sleep(3000);
        }
        
        


    } else {
        show_modal_message('danger', 'SELECT SKILL', 'YOU DID NOT SELECT ACTIVE SKILL')
    }


    
});