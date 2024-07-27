// switch display themes

window.onload = () => {
  let baseURL = location.origin;
  let head = document.getElementsByTagName('head')[0];
  let switchModeBtn = document.getElementById('switch-mode');
  let mode = getModeCookie();

  if (typeof  mode === 'boolean') {
    // default dark mode
    document.cookie = 'mode=dark';
  }
  else {
    let to = (mode === 'dark') ? 'light' : 'dark';
    switchTheme(head, to, `${baseURL}/static/css/${mode}-theme.css`);
  }
  
  /**
  * Delete the old stylesheet and build a link element that loads given stylesheet
  * @function switchTheme - DOM method
  * @param {Element} head - the head element - link element container
  * @param {String} theme - used to change the mode icon
  * @param {String} stylesheetURL = stylesheet's url
  */
  function switchTheme(head, theme, stylesheetURL) {
      switchModeBtn.innerHTML = `<span class="material-icons icon">${theme}_mode</span>`;
      
      let oldStylesheet = document.getElementById('theme');
      oldStylesheet.disabled = true;
      oldStylesheet.parentNode.removeChild(oldStylesheet);

      let stylesheet = document.createElement('link');
      stylesheet.id = 'theme';
      stylesheet.rel  = 'stylesheet';
      stylesheet.type = 'text/css';
      stylesheet.href = stylesheetURL;
      stylesheet.media = 'all';
      head.appendChild(stylesheet);
  }

  /**
   * return the mode stored in cookies
   * @function getModeCookie
   * @returns {String|bool} the current mode if found else false
   */
  function getModeCookie() {
    let found = document.cookie
      .split(';')
      .find(c => c.startsWith('mode='));
    if (found) {
      return found.split('=')[1];
    }
    else {
      return false;
    }
  }

  switchModeBtn.addEventListener('click', ev => {
    let mode = getModeCookie();

    if (mode === 'dark') {
      document.cookie = 'mode=light';
      switchTheme(head, 'dark', `${baseURL}/static/css/light-theme.css`);
    }
    else if (mode === 'light') {
      document.cookie = 'mode=dark';
      switchTheme(head, 'light', `${baseURL}/static/css/dark-theme.css`);
    }
  });
};
