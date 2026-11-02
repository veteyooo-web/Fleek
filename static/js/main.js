/* Taskly — небольшие улучшения интерфейса без внешних зависимостей */
(function () {
    'use strict';

    // Закрытие всплывающих сообщений об успехе/ошибке
    document.querySelectorAll('[data-close-alert]').forEach(function (button) {
        button.addEventListener('click', function () {
            var alert = button.closest('.alert');
            if (alert) {
                alert.remove();
            }
        });
    });

    // Автоскрытие уведомлений через 7 секунд
    var alerts = document.querySelectorAll('.alert');
    if (alerts.length) {
        setTimeout(function () {
            alerts.forEach(function (alert) {
                alert.style.transition = 'opacity .4s';
                alert.style.opacity = '0';
                setTimeout(function () { alert.remove(); }, 400);
            });
        }, 7000);
    }

    // Подтверждение опасных действий (удаление, отмена проекта)
    document.querySelectorAll('form[data-confirm]').forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!window.confirm(form.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });
    document.querySelectorAll('a[data-confirm]').forEach(function (link) {
        link.addEventListener('click', function (event) {
            if (!window.confirm(link.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });

    // Автоподстановка темы диалога из названия заказа
    var chatInput = document.querySelector('#id_content');
    if (chatInput) {
        chatInput.focus();
        chatInput.addEventListener('keydown', function (event) {
            // Отправка по Ctrl+Enter
            if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                chatInput.form.submit();
            }
        });
    }
})();
