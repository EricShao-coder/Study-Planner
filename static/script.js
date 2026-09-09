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

    let draggedTopic = null;

    function clearDragPreviews() {
        document.querySelectorAll('.drag-preview').forEach(preview => preview.remove());
    }

    function formatDate(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    function showDragPreview(target) {
        clearDragPreviews();

        const targetDate = new Date(`${target.dataset.targetDate}T00:00:00`);
        const previewDates = [targetDate];
        let interval = Math.max(1, Number(draggedTopic.dataset.interval) || 1);
        const easeFactor = Number(draggedTopic.dataset.easeFactor) || 2.5;

        for (let index = 0; index < 2; index += 1) {
            const nextDate = new Date(previewDates.at(-1));
            nextDate.setDate(nextDate.getDate() + interval);
            previewDates.push(nextDate);
            interval = Math.max(1, Math.round(interval * easeFactor));
        }

        previewDates.forEach((date, index) => {
            const previewTarget = document.querySelector(
                `.drop-target[data-target-date="${formatDate(date)}"]`
            );
            if (!previewTarget) {
                return;
            }

            const preview = document.createElement('div');
            preview.className = 'drag-preview';
            preview.textContent = index === 0
                ? `Move ${draggedTopic.dataset.title} here`
                : `Future review: ${draggedTopic.dataset.title}`;
            previewTarget.append(preview);
        });
    }

    document.querySelectorAll('.draggable-topic').forEach(topic => {
        topic.addEventListener('dragstart', event => {
            draggedTopic = topic;
            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.setData('text/plain', topic.dataset.topicId);
            topic.classList.add('is-dragging');
        });

        topic.addEventListener('dragend', () => {
            topic.classList.remove('is-dragging');
            draggedTopic = null;
            clearDragPreviews();
            document.querySelectorAll('.drop-target').forEach(target => {
                target.classList.remove('is-drag-over');
            });
        });
    });

    document.querySelectorAll('.drop-target').forEach(target => {
        target.addEventListener('dragover', event => {
            event.preventDefault();
            event.dataTransfer.dropEffect = 'move';
            target.classList.add('is-drag-over');
            if (draggedTopic) {
                showDragPreview(target);
            }
        });

        target.addEventListener('dragleave', event => {
            if (!target.contains(event.relatedTarget)) {
                target.classList.remove('is-drag-over');
            }
        });

        target.addEventListener('drop', async event => {
            event.preventDefault();
            target.classList.remove('is-drag-over');
            clearDragPreviews();

            if (!draggedTopic || target.contains(draggedTopic)) {
                return;
            }

            const formData = new FormData();
            formData.append('target_date', target.dataset.targetDate);
            const response = await fetch(draggedTopic.dataset.rescheduleUrl, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                window.location.reload();
            }
        });
    });

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