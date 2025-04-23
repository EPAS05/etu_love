document.addEventListener('DOMContentLoaded', () => {
    // ???????????? ???????
    const tabs = document.querySelectorAll('.auth-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // ??????? ?????????? ? ????
            tabs.forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.form-content').forEach(f => f.classList.remove('active'));

            // ?????????? ?????????
            tab.classList.add('active');
            const targetId = tab.getAttribute('data-target');
            document.querySelector(targetId).classList.add('active');
        });
    });
});