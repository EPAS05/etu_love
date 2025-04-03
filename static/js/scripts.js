document.querySelectorAll('.auth-container').forEach(container => {
    container.addEventListener('mouseenter', () => {
        const isRegister = container.classList.contains('register-container');
        const offset = window.innerWidth > 480 ? 60 : 40;
        document.querySelectorAll('.auth-container').forEach(el => {
            if (el !== container) {
                el.style.transform = `translateY(${isRegister ? offset : -offset}px)`;
            }
        });
    });
    container.addEventListener('mouseleave', () => {
        document.querySelectorAll('.auth-container').forEach(el => {
            el.style.transform = 'translateY(0)';
        });
    });
});

