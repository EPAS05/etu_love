document.addEventListener('DOMContentLoaded', function () {
    // Функция синхронной активации вкладки
    function activateTab(tabId, initialLoad = false) {
        // Блокировка рендера перед изменениями
        document.body.style.opacity = '0';

        // Синхронное скрытие всех элементов
        document.querySelectorAll('.settings-block').forEach(el => {
            el.style.display = 'none';
            el.classList.remove('active');
        });

        const tab = document.querySelector(`.settings-tab[data-tab="${tabId}"]`);
        const content = document.getElementById(tabId);

        if (tab && content) {
            // Синхронное отображение нужного контента
            content.style.display = 'block';
            content.style.opacity = '0';
            tab.classList.add('active');

            // Форсируем рефлоу перед анимацией
            void content.offsetHeight;

            // Плавное появление
            setTimeout(() => {
                content.style.opacity = '1';
                content.classList.add('active');
                document.body.style.opacity = '1';
            }, initialLoad ? 0 : 50);
        }
    }

    // Восстановление вкладки ДО отрисовки страницы
    const activeTab = localStorage.getItem('activeSettingsTab') || 'account';
    activateTab(activeTab, true);

    // Обработчики вкладок
    document.querySelectorAll('.settings-tab').forEach(tab => {
        tab.addEventListener('click', function () {
            const tabId = this.dataset.tab;
            localStorage.setItem('activeSettingsTab', tabId);

            document.querySelectorAll('.settings-tab, .settings-block').forEach(el => {
                el.style.transition = 'none';
                el.classList.remove('active');
            });

            activateTab(tabId);
        });
    });

    // Удаление аккаунта
    document.querySelector('.danger')?.addEventListener('click', () => {
        if (!confirm('Вы уверены, что хотите удалить аккаунт? Это нельзя отменить!')) return;
    });

    // Выпадающие списки
    function toggleDropdown(header) {
        const dropdown = header.parentElement;
        const content = dropdown.querySelector('.dropdown-content');
        const arrow = dropdown.querySelector('.arrow');

        document.querySelectorAll('.dropdown-content').forEach(d => {
            if (d !== content) d.classList.remove('show');
        });
        content.classList.toggle('show');
        arrow.classList.toggle('rotate');
    }

    document.querySelectorAll('.dropdown-header').forEach(header => {
        header.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown-content')) {
                toggleDropdown(header);
            }
        });
    });

    // Множественный выбор языков
    document.querySelectorAll('#languageDropdown input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const selected = Array.from(document.querySelectorAll('#languageDropdown input:checked'))
                .map(el => el.parentElement.textContent.trim()).join(', ');
            document.querySelector('.selected-items').textContent = selected || 'Выберите языки...';
        });
    });

    // Радио-кнопки
    document.querySelectorAll('.single-select input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function () {
            const dropdown = this.closest('.custom-dropdown');
            const selectedText = this.parentElement.textContent.trim();
            dropdown.querySelector('.selected-item').textContent = selectedText;
            dropdown.querySelector('.dropdown-content').classList.remove('show');
            dropdown.querySelector('.arrow').classList.remove('rotate');
        });
    });

    // Закрытие выпадающих списков
    window.addEventListener('click', function (e) {
        if (!e.target.closest('.custom-dropdown')) {
            document.querySelectorAll('.dropdown-content').forEach(d => {
                d.classList.remove('show');
            });
            document.querySelectorAll('.arrow').forEach(arrow => {
                arrow.classList.remove('rotate');
            });
        }
    });

    // Валидация пароля
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', function (e) {
            const newPass = document.getElementById('id_new_password').value;
            const confirmPass = document.getElementById('id_confirm_password').value;
            if (newPass !== confirmPass) {
                e.preventDefault();
                alert('Пароли не совпадают!');
            }
        });
    }
});