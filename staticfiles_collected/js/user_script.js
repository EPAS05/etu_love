// =======================================================
// Функции для работы с темой оформления и иконкой смены темы
// =======================================================

function applySavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }
    updateThemeIcon(savedTheme || '');
}

function updateThemeIcon(theme) {
    const icon = document.getElementById('theme-icon');
    if (icon) {
        icon.src = theme === 'dark' ? themeDarkUrl : themeLightUrl;
    }
}

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



function openUserInfoModal() {
    document.getElementById('infoModal').style.display = 'flex';
}

function closeUserInfoModal() {
    document.getElementById('infoModal').style.display = 'none';
}

/**
 * Открывает модальное окно для фотографий (галерея).
 */
function openPhotoModal() {
    document.getElementById('photoModal').style.display = 'block';
}

/**
 * Закрывает модальное окно для фотографий (галерея).
 */
function closePhotoModal() {
    document.getElementById('photoModal').style.display = 'none';
}

/**
 * Открывает модальное окно для предпросмотра выбранной фотографии.
 * @param {string} src - URL изображения
 */
function openPhotoPreview(src) {
    const previewModal = document.getElementById('photoPreviewModal');
    const previewImg = previewModal.querySelector('img');
    previewImg.src = src;
    previewModal.style.display = 'flex';
}

/**
 * Закрывает модальное окно предпросмотра фотографии.
 */
function closePhotoPreview() {
    document.getElementById('photoPreviewModal').style.display = 'none';
}

// =======================================================
// Инициализация и установка обработчиков событий после загрузки DOM
// =======================================================
document.addEventListener('DOMContentLoaded', () => {
    applySavedTheme();

    document.querySelectorAll('.animate').forEach(el => {
        el.style.opacity = 0;
        setTimeout(() => el.style.opacity = 1, 100);
    });

    document.querySelectorAll('.avatar-option').forEach(btn => {
        btn.addEventListener('click', () => saveavatar(btn.textContent));
    });

    // Открытие модального окна для фотографий – обработка клика на элементе с классом overlay (+N)
    document.querySelectorAll('.modal-trigger').forEach(trigger => {
        trigger.addEventListener('click', openPhotoModal);
    });

    // Обработчик закрытия окна по клику вне блока с фото (галерея) уже реализован через inline onclick в разметке
});
