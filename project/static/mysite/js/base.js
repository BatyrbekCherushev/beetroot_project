


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
