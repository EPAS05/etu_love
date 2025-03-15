// Применяет сохраненную тему из localStorage
function applySavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }
}
// Открывает модальное окно выбора аватарки
function openavatarModal() {
    document.getElementById('avatarModal').style.display = 'flex';
}
// Закрывает модальное окно выбора аватарки
function closeavatarModal() {
    document.getElementById('avatarModal').style.display = 'none';
}
// Сохраняет выбранный аватар и обновляет отображение
function saveavatar(avatar) {
    localStorage.setItem('useravatar', avatar);
    applySavedavatar();
    closeavatarModal();
}
// Применяет сохраненный аватар из localStorage
function applySavedavatar() {
    const savedavatar = localStorage.getItem('useravatar');
    const defaultavatar = '👤';
    document.querySelector('.user-photo').textContent = savedavatar || defaultavatar;
}
// Открывает модальное окно с информацией о пользователе
function openUserInfoModal() {
    document.getElementById('infoModal').style.display = 'flex';
}
// Закрывает модальное окно с информацией
function closeUserInfoModal() {
    document.getElementById('infoModal').style.display = 'none';
}
// Основная инициализация после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    // Применяем сохраненные настройки
    applySavedTheme();
    applySavedavatar();
    // Анимация элементов при загрузке
    document.querySelectorAll('.animate').forEach(el => {
        el.style.opacity = 0;
        setTimeout(() => el.style.opacity = 1, 100);
    });
    // Обработчики кликов
    document.querySelector('.user-photo').addEventListener('click', openavatarModal);
    document.querySelector('.info-btn').addEventListener('click', openUserInfoModal);
    document.querySelector('.star-container').addEventListener('click', () => {
        alert('МБ ФУНКЦИЮ С ПЕРЕКИДЫВАНИЕМ ДОМОЙ');
    });
    // Закрытие модалок по клику вне области
    document.getElementById('avatarModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('avatarModal')) {
            closeavatarModal();
        }
    });

    document.getElementById('infoModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('infoModal')) {
            closeUserInfoModal();
        }
    });
    // Обработчики для кнопок выбора аватарки
    document.querySelectorAll('.avatar-option').forEach(btn => {
        btn.addEventListener('click', () => saveavatar(btn.textContent));
    });
});
// Переключает между светлой и темной темой
function toggleTheme() {
    const newTheme = document.body.getAttribute('data-theme') === 'dark' ? '' : 'dark';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}