document.addEventListener('DOMContentLoaded', () => {
    function updateTime() {
        const time = document.getElementById('live-clock');
        if (!time) {
            return;
        }
        const now = new Date();

        time.textContent = now.toLocaleTimeString('en-US', { 
                    hour12: false, 
                    hour: '2-digit', 
                    minute: '2-digit', 
                    second: '2-digit' 
                });
    }
    updateTime();
    setInterval(updateTime, 1000);

    const modal = document.getElementById('my-popup');
    const topicForm = document.getElementById('topic-form');

    if (!modal || !topicForm) {
        return;
    }

    const closeButton = document.getElementById('modal-close');
    const dateInput = document.getElementById('review-date');

    function closeModal() {
        modal.hidden = true;
    }

    function openModal(item) {
        document.getElementById('modal-subject').textContent = item.dataset.subject;
        document.getElementById('modal-title').textContent = item.dataset.title;
        document.getElementById('modal-repetition').textContent = item.dataset.repetition;
        document.getElementById('modal-interval').textContent = `${item.dataset.interval} days`;
        document.getElementById('modal-ease-factor').textContent = item.dataset.easeFactor;
        dateInput.value = item.dataset.reviewDate;
        topicForm.action = `/topics/${item.dataset.topicId}/review`;
        modal.hidden = false;
        closeButton.focus();
    }

    document.querySelectorAll('.topic-trigger').forEach(item => {
        item.addEventListener('click', () => openModal(item));
        item.addEventListener('keydown', event => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                openModal(item);
            }
        });
    });

    closeButton.addEventListener('click', closeModal);
    modal.addEventListener('click', event => {
        if (event.target === modal) {
            closeModal();
        }
    });
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && !modal.hidden) {
            closeModal();
        }
    });

});