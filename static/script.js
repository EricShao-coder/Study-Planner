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

    const calendar_items = document.querySelectorAll('.calendar-item.upcoming');
    const popup = document.getElementById('my-popup');
    const popupText = document.getElementById('popup-text');

    calendar_items.forEach(item => {
        item.addEventListener('mouseover', function(event) {
            // Update content dynamically based on the hovered item
            const title = item.getAttribute('data-title');
            popupText.textContent = `Due topic: ${title}`;
            
            popup.style.display = 'block';
            popup.style.top = (event.pageY + 10) + 'px';
            popup.style.left = (event.pageX + 10) + 'px';
        });

        item.addEventListener('mousemove', function(event) {
            // Optional: Make popup follow the mouse slightly while inside the item
            popup.style.top = (event.pageY + 10) + 'px';
            popup.style.left = (event.pageX + 10) + 'px';
        });

        item.addEventListener('mouseout', function() {
            popup.style.display = 'none';
        });
    });

});