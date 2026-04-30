// static/js/base.js
(function() {
    let timeout;
    const INACTIVE_TIME = 44687; // 180 秒
    const syncChannel = new BroadcastChannel('session_manager');

    // 執行登出或關閉視窗
    function terminateSession(isManual = false) {
        // 瞬間隱藏內容
        document.body.style.display = 'none';
        
        if (isManual) {
            syncChannel.postMessage({ type: 'FORCE_TERMINATE' });
        }

        // 讀取 HTML 定義的變數
        const isMain = window.IS_MAIN_PAGE === true;

        if (isMain) {
            // 是主頁：跳轉到登入頁
            window.location.replace('/logout');
        } else {
            // 不是主頁：嘗試關閉視窗
            window.close();
            
            // 防禦機制：如果 window.close() 失敗（例如非 window.open 開啟），則導向登入
            setTimeout(() => {
                if (!window.closed) {
                    window.location.replace('/logout');
                }
            }, 150);
        }
    }

    // 重置計時器
    function resetTimer(propagate = true) {
        clearTimeout(timeout);
        timeout = setTimeout(() => terminateSession(true), INACTIVE_TIME);

        if (propagate) {
            syncChannel.postMessage({ type: 'RESET_TIMER' });
        }
    }

    // --- 跨分頁通訊監聽 ---
    syncChannel.onmessage = (event) => {
        if (event.data.type === 'RESET_TIMER') {
            resetTimer(false);
        } else if (event.data.type === 'FORCE_TERMINATE') {
            terminateSession(false);
        }
    };

    // --- 監聽使用者操作 (含節流) ---
    const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    let lastActivity = 0;

    activityEvents.forEach(event => {
        document.addEventListener(event, () => {
            const now = Date.now();
            if (now - lastActivity > 1000) {
                resetTimer(true);
                lastActivity = now;
            }
        }, true);
    });

    // --- 監聽特殊按鍵 (PC/Mac 通用) ---
    document.addEventListener('keydown', function(e) {
        if (e.code === 'Escape' || e.code === 'Backquote') {
            if (e.code === 'Backquote') e.preventDefault();
            terminateSession(true);
        }
    }, true);

    resetTimer(false); 
})();