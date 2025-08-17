

// window.getUserInfo = async function() {
//     try {
//         const response = await fetch('/get-settings/');
//         const data = await response.json();
//         return data
//     } catch (err) {
//         console.error(err);
//     }
// };

// let settings = await getUserInfo();
// console.log(settings)


async function init() {
    window.userInfo = await getUserInfo();
    console.log(window.userInfo);
}

async function getUserInfo() {
    try {
        const response = await fetch('/get-user-info/');
        return await response.json();
    } catch (err) {
        console.error(err);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    init();
    // document.querySelector('.js-show-settings').textContent = await JSON.stringify(window.userSettings);
});