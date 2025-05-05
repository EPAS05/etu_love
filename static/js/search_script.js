// Модальное окно критериев
const modal = document.getElementById('criteriaModal');
document.querySelector('.open-criteria-btn').onclick = () => modal.classList.add('active');
modal.querySelector('.modal-close').onclick = () => modal.classList.remove('active');
window.onclick = e => {
    if (e.target === modal) modal.classList.remove('active');
};

// Аккордеон детальных настроек
const acc = document.getElementById('valuesAccordion');
const header = acc.querySelector('.accordion-header');
const content = acc.querySelector('.accordion-content');
header.onclick = () => {
    const open = acc.classList.toggle('active');
    content.style.maxHeight = open ? content.scrollHeight + 'px' : '0';
};