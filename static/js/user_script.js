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

function openUserInfoModal() {
    document.getElementById('infoModal').style.display = 'flex';
}

function closeUserInfoModal() {
    document.getElementById('infoModal').style.display = 'none';
}
function openPhotoModal() {
    document.getElementById('photoModal').style.display = 'block';
}

function closePhotoModal() {
    document.getElementById('photoModal').style.display = 'none';
}

function openPhotoPreview(src) {
    const previewModal = document.getElementById('photoPreviewModal');
    const previewImg = previewModal.querySelector('img');
    previewImg.src = src;
    previewModal.style.display = 'flex';
}

function closePhotoPreview() {
    document.getElementById('photoPreviewModal').style.display = 'none';
}

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

let currentPreviewPhotoUrl = null;

function confirmDeletePhoto(url) {
    if (confirm('Вы уверены, что хотите удалить эту фотографию?')) {
        window.location.href = url;
    }
}

function openPhotoPreview(src) {
    const previewModal = document.getElementById('photoPreviewModal');
    const previewImg = previewModal.querySelector('img');
    const photoElement = Array.from(document.querySelectorAll('.gallery-photo'))
        .find(img => img.src === src);

    if (photoElement) {
        currentPreviewPhotoUrl = photoElement.dataset.deleteUrl;
        previewImg.src = src;
        previewModal.style.display = 'flex';
    }
}
function openReviewsModal() {
    document.getElementById('reviewsModal').style.display = 'flex';
}

function closeReviewsModal() {
    document.getElementById('reviewsModal').style.display = 'none';
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeReviewsModal();
});