import * as base from './base.js'

document.addEventListener('DOMContentLoaded', async () => {

    try {
        const settings = await base.getUserInfo();  // чекаємо завершення fetch
        console.log(settings)
        // document.querySelector('.js-show-settings').textContent = JSON.stringify(settings);
    } catch (err) {
        console.error(err);
    }
})