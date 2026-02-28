// request.js
export async function request(url, options = {}) {
    // 1. 自動補上 application/json，除非你手動覆蓋它
    const defaultHeaders = {
        'Content-Type': 'application/json'
    };

    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers
        }
    };

    const res = await fetch(url, config);
    
    // 2. 先試著解析 JSON
    let data;
    try {
        data = await res.json();
    } catch (e) {
        data = { error: '伺服器解析失敗 (Non-JSON)' };
    }

    // 3. 如果 HTTP 狀態碼不 OK (4xx, 5xx)
    if (!res.ok) {
        // 核心邏輯：統合各種錯誤欄位，讓前端 showMessage 永遠有東西抓
        // 優先順序：後端給的 message > 後端給的 error > HTTP 狀態文字
        data.displayMessage = data.message || data.error || `HTTP Error ${res.status}`;
        throw data; // 拋出整包，包含後端原本的 status 等資訊
    }

    // 4. 成功就直接回傳 data
    return data;
}