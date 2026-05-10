// static/js/base.js
(function() {
    let timeout;
    let countdownInterval;
    let isPaused = false; 
    
    // --- 定義兩種模式的時間 ---
    const NORMAL_TIME = 44687;    // 44秒
    const EXTENDED_TIME = 699633;  // 約11.6分鐘
    let currentInactiveTime = NORMAL_TIME;
    
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
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #00ff41;
                border-radius: 4px;
                z-index: 2147483647;
                cursor: pointer;
                user-select: none;
                transition: all 0.2s ease;
                box-shadow: 0 0 8px rgba(0, 255, 65, 0.2);
            }
            #session-countdown.is-paused {
                color: #4da6ff !important;
                border-color: #4da6ff !important;
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
    };

    // 修改：切換模式時確保所有變數同步
    function applyMode(pausedState) {
        isPaused = pausedState;
        if (isPaused) {
            currentInactiveTime = EXTENDED_TIME;
            countdownEl.classList.add('is-paused');
            countdownEl.style.color = '#4da6ff'; 
            countdownEl.style.borderColor = '#4da6ff';
        } else {
            currentInactiveTime = NORMAL_TIME;
            countdownEl.classList.remove('is-paused');
            countdownEl.style.color = '#00ff41';
            countdownEl.style.borderColor = '#00ff41';
        }
        // 切換模式後，必須立即重設計時器以套用新的 currentInactiveTime
        resetTimer(false); 
    }

    function togglePause(propagate = true) {
        const newState = !isPaused;
        applyMode(newState);

        if (propagate) {
            syncChannel.postMessage({ type: 'TOGGLE_PAUSE', paused: newState });
        }
    }

    function updateCountdownUI(msLeft) {
        if (!countdownEl) return;
        const seconds = Math.ceil(msLeft / 1000);
        
        // 優化顯示：超過 60 秒顯示 分:秒
        //if (seconds >= 60) {
        //    const m = Math.floor(seconds / 60);
        //    const s = seconds % 60;
        //    countdownEl.innerText = `${m}:${s.toString().padStart(2, '0')}`;
        //} else {
            countdownEl.innerText = `${seconds}`;
        //}
        
        if (seconds <= 10) countdownEl.classList.add('warning');
        else countdownEl.classList.remove('warning');
    }

    function startVisualCountdown() {
        clearInterval(countdownInterval);
        const startTime = Date.now();
        
        countdownInterval = setInterval(() => {
            const remaining = currentInactiveTime - (Date.now() - startTime);
            if (remaining <= 0) {
                clearInterval(countdownInterval);
                updateCountdownUI(0);
            } else {
                updateCountdownUI(remaining);
            }
        }, 1000);
        
        updateCountdownUI(currentInactiveTime);
    }

    function terminateSession(isManual = false) {
        // 如果是自動觸發且處於暫停（長時間）模式，邏輯上這裡應該還是要執行，
        // 因為長模式只是「時間變長」，不是「永遠不登出」。
        // 若你希望長模式下「絕對不自動登出」，才保留 isPaused 攔截。
        // 但根據金流需求，建議長模式到期一樣登出，所以移除攔截。
        
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
        clearTimeout(timeout);
        startVisualCountdown();
        // 使用當前選定的時間模式進行倒數
        timeout = setTimeout(() => terminateSession(true), currentInactiveTime);

        if (propagate) {
            syncChannel.postMessage({ type: 'RESET_TIMER' });
        }
    }

    const init = () => {
        injectStyles();
        createUI();

        const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
        let lastActivity = 0;
        const THROTTLE_DELAY = 1000;

        activityEvents.forEach(event => {
            document.addEventListener(event, () => {
                const now = Date.now();
                if (now - lastActivity > THROTTLE_DELAY) {
                    resetTimer(true); // 這裡不再檢查 isPaused，移動即重置
                    lastActivity = now;
                }
            }, true);
        });

        document.addEventListener('keydown', (e) => {
            if (e.code === 'Backquote') {
                e.preventDefault();
                if (e.ctrlKey || e.metaKey) {
                    togglePause(true);
                } else {
                    terminateSession(true);
                }
            }
        }, true);

        // --- 完善跨分頁通訊 ---
        syncChannel.onmessage = (event) => {
            if (event.data.type === 'RESET_TIMER') {
                resetTimer(false); // 接收來自其他分頁的重置訊號
            } else if (event.data.type === 'FORCE_TERMINATE') {
                terminateSession(false);   
            } else if (event.data.type === 'TOGGLE_PAUSE') {
                // 收到切換模式訊號，同步狀態並重設計時器
                applyMode(event.data.paused);
            }
        };

        resetTimer(false);
    };

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();