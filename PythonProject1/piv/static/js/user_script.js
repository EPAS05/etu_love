// =======================================================
// Функции для работы с темой оформления и иконкой смены темы
// =======================================================

/**
 * Применяет сохраненную тему из localStorage и обновляет иконку смены темы.
 * Если в localStorage сохранена тема, она устанавливается как атрибут data-theme для <body>.
 * Затем вызывается функция updateThemeIcon для обновления изображения иконки.
 */
function applySavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }
    updateThemeIcon(savedTheme || '');
}

/**
 * Обновляет атрибут src у иконки смены темы в зависимости от текущей темы.
 * Если тема "dark", устанавливается путь к иконке темной темы, иначе - светлой.
 * @param {string} theme - Текущая тема ('dark' или пустая строка для светлой темы)
 */
function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.src = theme === 'dark' ? themeDarkUrl : themeLightUrl;
    }
}

/**
 * Переключает тему оформления между светлой и темной.
 * Определяет текущую тему, переключает на противоположную, обновляет атрибут data-theme,
 * сохраняет новую тему в localStorage и обновляет иконку.
 */
function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? '' : 'dark';
    document.body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

// =======================================================
// Функции для работы с аватаром и модальными окнами
// =======================================================

/**
 * Открывает модальное окно для выбора аватара, устанавливая display: flex для элемента.
 */
function openavatarModal() {
    document.getElementById('avatarModal').style.display = 'flex';
}

/**
 * Закрывает модальное окно выбора аватара, устанавливая display: none для элемента.
 */
function closeavatarModal() {
    document.getElementById('avatarModal').style.display = 'none';
}

/**
 * Сохраняет выбранный аватар в localStorage, обновляет отображение аватара и закрывает модальное окно.
 * @param {string} avatar - Выбранный аватар
 */
function saveavatar(avatar) {
    localStorage.setItem('useravatar', avatar);
    applySavedavatar();
    closeavatarModal();
}

/**
 * Применяет сохраненный аватар из localStorage. Если аватар не сохранён,
 * используется аватар по умолчанию (эмодзи "👤").
 */
function applySavedavatar() {
    const savedavatar = localStorage.getItem('useravatar');
    const defaultavatar = '👤';
    document.querySelector('.user-photo').textContent = savedavatar || defaultavatar;
}

/**
 * Открывает модальное окно с информацией о пользователе, устанавливая display: flex.
 */
function openUserInfoModal() {
    document.getElementById('infoModal').style.display = 'flex';
}

/**
 * Закрывает модальное окно с информацией о пользователе, устанавливая display: none.
 */
function closeUserInfoModal() {
    document.getElementById('infoModal').style.display = 'none';
}

// =======================================================
// Инициализация и установка обработчиков событий после загрузки DOM
// =======================================================

document.addEventListener('DOMContentLoaded', () => {
    // Применяем сохранённые настройки темы и аватара
    applySavedTheme();
    applySavedavatar();

    // Анимация элементов с классом .animate при загрузке страницы
    document.querySelectorAll('.animate').forEach(el => {
        el.style.opacity = 0;
        setTimeout(() => el.style.opacity = 1, 100);
    });

    // Устанавливаем обработчик клика для аватарки для открытия модального окна выбора аватара
    document.querySelector('.user-photo').addEventListener('click', openavatarModal);

    // Устанавливаем обработчик клика для кнопки информации для открытия модального окна с информацией о пользователе
    document.querySelector('.info-btn').addEventListener('click', openUserInfoModal);

    // Обработчик клика по контейнеру звезды (пример действия, можно заменить на нужную логику)
    document.querySelector('.star-container').addEventListener('click', () => {
        alert('МБ ФУНКЦИЮ С ПЕРЕКИДЫВАНИЕМ ДОМОЙ');
    });

    // Закрытие модального окна аватара по клику вне его области
    document.getElementById('avatarModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('avatarModal')) {
            closeavatarModal();
        }
    });

    // Закрытие модального окна информации по клику вне его области
    document.getElementById('infoModal').addEventListener('click', (e) => {
        if (e.target === document.getElementById('infoModal')) {
            closeUserInfoModal();
        }
    });

    // Устанавливаем обработчики кликов для кнопок выбора аватара внутри модального окна
    document.querySelectorAll('.avatar-option').forEach(btn => {
        btn.addEventListener('click', () => saveavatar(btn.textContent));
    });
});