// static/js/base.js
(function() {
    let timeout;
    let countdownInterval;
    let isPaused = false; 
    let remainingAtPause = 0; // 紀錄暫停那一刻剩餘的時間
    const INACTIVE_TIME = 44687; 
    const syncChannel = new BroadcastChannel('session_manager');

    const injectStyles = () => {
        const style = document.createElement('style');
        style.textContent = `
            #session-countdown {
                position: fixed;
                bottom: 2px;
                left: 2px;
                padding: 5px 10px;
                background: rgba(10, 10, 10, 0.85);
                color: #00ff41;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                border: 1px solid #00ff41;
                border-radius: 4px;
                z-index: 2147483647;
                cursor: pointer; /* 點擊感 */
                user-select: none;
                transition: all 0.2s ease;
                box-shadow: 0 0 8px rgba(0, 255, 65, 0.2);
            }
            /* 暫停態：變灰、邊框黯淡 */
            #session-countdown.is-paused {
                color: #888 !important;
                border-color: #555 !important;
                background: rgba(40, 40, 40, 0.9);
                box-shadow: none;
                animation: none !important;
            }
            #session-countdown.warning {
                color: #ff3e3e;
                border-color: #ff3e3e;
                animation: echo-blink 1s infinite;
            }
            @keyframes echo-blink {
                0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    };

    let countdownEl;
    const createUI = () => {
        countdownEl = document.createElement('div');
        countdownEl.id = 'session-countdown';
        document.body.appendChild(countdownEl);

        // 點擊事件：切換暫停/恢復
        //countdownEl.addEventListener('click', () => {
        //    togglePause(true);
        //});
    };

    function togglePause(propagate = true) {
        isPaused = !isPaused;
        
        if (isPaused) {
            // 進入時停：清除計時器
            clearInterval(countdownInterval);
            clearTimeout(timeout);
            countdownEl.classList.add('is-paused');
            // countdownEl.innerText = "PAUSED";
        } else {
            // 恢復運作：從初始值重新開始 (或可根據需求微調回原本秒數)
            countdownEl.classList.remove('is-paused');
            resetTimer(false);
        }

        if (propagate) {
            syncChannel.postMessage({ type: 'TOGGLE_PAUSE', paused: isPaused });
        }
    }

    function updateCountdownUI(msLeft) {
        if (!countdownEl || isPaused) return;
        const seconds = Math.ceil(msLeft / 1000);
        countdownEl.innerText = `${seconds}`;
        
        if (seconds <= 10) countdownEl.classList.add('warning');
        else countdownEl.classList.remove('warning');
    }

    function startVisualCountdown() {
        if (isPaused) return;
        clearInterval(countdownInterval);
        const startTime = Date.now();
        
        countdownInterval = setInterval(() => {
            const remaining = INACTIVE_TIME - (Date.now() - startTime);
            if (remaining <= 0) {
                clearInterval(countdownInterval);
                updateCountdownUI(0);
            } else {
                updateCountdownUI(remaining);
            }
        }, 1000);
        
        updateCountdownUI(INACTIVE_TIME);
    }

    function terminateSession(isManual = false) {
        if (isPaused && !isManual) return;
        
        document.body.style.display = 'none';
        if (isManual) syncChannel.postMessage({ type: 'FORCE_TERMINATE' });

        const isMain = window.IS_MAIN_PAGE === true;
        if (isMain) window.location.replace('/logout');
        else {
            window.close();
            setTimeout(() => { if (!window.closed) window.location.replace('/logout'); }, 150);
        }
    }

    function resetTimer(propagate = true) {
        if (isPaused) return; 
        
        clearTimeout(timeout);
        startVisualCountdown();
        timeout = setTimeout(() => terminateSession(true), INACTIVE_TIME);

        if (propagate) {
            syncChannel.postMessage({ type: 'RESET_TIMER' });
        }
    }

    const init = () => {
        injectStyles();
        createUI();

        // 監聽鍵盤/滑鼠活動
        //['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        //    document.addEventListener(event, () => {
        //        if (!isPaused) resetTimer(true);
        //    }, true);
        //});
        // --- 監聽使用者操作 (加入節流防護) ---
        const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        let lastActivity = 0;
        const THROTTLE_DELAY = 1000; // 1 秒內只允許重置一次

        activityEvents.forEach(event => {
            document.addEventListener(event, () => {
                if (isPaused) return; // 暫停中直接無視

                const now = Date.now();
                // 只有距離上次重置超過 1 秒，才再次執行重置
                if (now - lastActivity > THROTTLE_DELAY) {
                    resetTimer(true);
                    lastActivity = now;
                    // console.log(`[Session] 偵測到 ${event}，重設計時器`);
                }
            }, true);
        });

        // 快捷鍵：Escape/Backquote
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Backquote') {
                e.preventDefault(); // 攔截預設符號輸入

                if (e.ctrlKey || e.metaKey) {
                    // 情況 A: Ctrl + ` -> 切換暫停 (就像開關 Terminal)
                    console.log("Ctrl + ` 觸發：切換時停領域...");
                    togglePause(true);
                } else {
                    // 情況 B: 單純 ` -> 執行緊急避險
                    terminateSession(true);
                }
            }
        }, true);

        // 跨分頁同步
        syncChannel.onmessage = (event) => {
            if (event.data.type === 'RESET_TIMER') resetTimer(false);
            else if (event.data.type === 'FORCE_TERMINATE') {
                isPaused = false;
                terminateSession(true);   
            } else if (event.data.type === 'TOGGLE_PAUSE') {
                if (isPaused !== event.data.paused) togglePause(false);
            }
        };

        resetTimer(false);
    };

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();