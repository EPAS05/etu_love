// Сохранение и применение темы
function applySavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
    applySavedTheme();

    document.querySelectorAll('.animate').forEach(el => {
        el.style.opacity = 0;
        setTimeout(() => el.style.opacity = 1, 100);
    });

    document.querySelector('.user-photo').addEventListener('click', () => {
        alert('НЕ ТЫКАТЬ!!!');
    });
    document.querySelector('.star-container').addEventListener('click', () => {
        alert('МБ ФУНКЦИЮ С ПЕРЕКИДЫВАНИЕМ ДОМОЙ');
    });
});

// Переключение темы
function toggleTheme() {
    const newTheme = document.body.getAttribute('data-theme') === 'dark' ? '' : 'dark';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}