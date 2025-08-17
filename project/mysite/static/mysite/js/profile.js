document.addEventListener('DOMContentLoaded', async () => {

    try {
        const settings = await getUserInfo();  // чекаємо завершення fetch
        document.querySelector('.js-show-settings').textContent = JSON.stringify(settings);
    } catch (err) {
        console.error(err);
    }
})