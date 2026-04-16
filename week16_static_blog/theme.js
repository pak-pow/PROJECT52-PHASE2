const themeToggleBtn = document.getElementById('themeToggle');
const currentTheme = localStorage.getItem('blog_theme');

if (currentTheme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    if(themeToggleBtn) themeToggleBtn.innerText = '☀️'; 
}

if(themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
        let theme = document.documentElement.getAttribute('data-theme');
        
        if (theme === 'dark') {
            document.documentElement.removeAttribute('data-theme');
            localStorage.setItem('blog_theme', 'light');
            themeToggleBtn.innerText = '🌙';
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('blog_theme', 'dark');
            themeToggleBtn.innerText = '☀️';
        }
    });
}

window.onscroll = function() { updateProgressBar() };

function updateProgressBar() {
    let winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    let height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    let scrolled = (winScroll / height) * 100;
    
    const bar = document.getElementById("myBar");
    if (bar) {
        bar.style.width = scrolled + "%";
    }
}