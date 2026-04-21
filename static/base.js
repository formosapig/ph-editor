// static/js/base.js
(function() {
    let timeout;
    const INACTIVE_TIME = 180000; // 180,000 ms = 180 秒

    function resetTimer() {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            // 時間到，直接跳轉到登出路由，讓 Flask 清除 Session
            window.location.href = '/logout';
        }, INACTIVE_TIME);
    }

    // 監聽各種動作來重置計時
    const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    activityEvents.forEach(event => {
        document.addEventListener(event, resetTimer, true);
    });

    resetTimer(); // 初始啟動
})();