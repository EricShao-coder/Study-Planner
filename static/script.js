document.addEventListener('DOMContentLoaded', () => {
    function updateTime() {
        const time = document.getElementById('live-clock');
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
});