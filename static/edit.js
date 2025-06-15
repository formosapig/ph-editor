window.addEventListener('DOMContentLoaded', () => {
    // Tab 切換功能
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有 active 類
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            
            // 添加 active 類到當前點擊的按鈕和對應內容
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // 頁面載入時立即調用 reloadFile 來載入數據
    //refresh();
	// 一開頁面直接用後端資料初始化頁面
    if (typeof characterData !== 'undefined') {
        updateTabs(characterData);
		document.getElementById('hex-display').textContent = '角色資料預戴完成。';
    } else {
        document.getElementById('hex-display').textContent = '無角色數據';
    }
});

/**
 * 向後端重新載入資料並解析顯示（完整流程）。
 */
function refresh() {
  const hexDisplay = document.getElementById('hex-display');
  const miscPre = document.querySelector('#misc pre');

  hexDisplay.textContent = '正在重新載入檔案數據...';
  miscPre.textContent = '正在載入解析數據...';

  fetch('/edit/read_hex')
    .then(response => {
      if (!response.ok) {
        return response.json().then(errData => {
          throw new Error(errData.error || `HTTP 錯誤: ${response.status}`);
        }).catch(() => {
          throw new Error(`HTTP 錯誤: ${response.status}`);
        });
      }
      return response.json();
    })
    .then(data => {
      hexDisplay.textContent = '';

      if (data.error) {
        hexDisplay.textContent = '錯誤：' + data.error;
        if (data.parsed_data_preview) {
          hexDisplay.textContent += '\n解析數據預覽：' + data.parsed_data_preview;
        }
      } else {
        hexDisplay.textContent = data.raw_data_hex_preview || '找不到原始數據的十六進位預覽。';

        if (data.full_parsed_data) {
          try {
            const parsedData = JSON.parse(data.full_parsed_data);
            updateTabs(parsedData);
          } catch (e) {
            miscPre.textContent = `--- 完整的解析結果 (格式錯誤) ---\n${data.full_parsed_data}\n錯誤: ${e.message}`;
          }
        } else {
          miscPre.textContent = '找不到完整的解析結果。';
        }
      }
    })
    .catch(err => {
      hexDisplay.textContent = '載入失敗：' + err.message;
      miscPre.textContent = '載入解析數據失敗：' + err.message;
    });
}

/**
 * 從後端獲取最新資料（純資料刷新），並更新到各個 tab。
 */
function reloadFile() {
  const hexDisplay = document.getElementById('hex-display');
  hexDisplay.textContent = '正在重新載入檔案數據...';

  fetch('/edit/reload_file')
    .then(response => {
      if (!response.ok) {
        return response.json().then(errData => {
          throw new Error(errData.error || `HTTP 錯誤: ${response.status}`);
        }).catch(() => {
          throw new Error(`HTTP 錯誤: ${response.status}`);
        });
      }
      return response.json();
    })
    .then(data => {
      if (data.error) {
        hexDisplay.textContent = '錯誤：' + data.error;
        return;
      }

      updateTabs(data);
	  hexDisplay.textContent = '重新載入檔案數據成功。';
    })
    .catch(err => {
      hexDisplay.textContent = '載入失敗：' + err.message;
    });
}

/**
 * 更新頁籤內容
 */
function updateTabs(parsedData) {
  document.querySelector('#fixed_header pre').textContent = parsedData.fixed_header ? JSON.stringify(parsedData.fixed_header, null, 2) : '無數據';
  document.querySelector('#hair pre').textContent = parsedData.hair ? JSON.stringify(parsedData.hair, null, 2) : '無數據';
  document.querySelector('#face pre').textContent = parsedData.face ? JSON.stringify(parsedData.face, null, 2) : '無數據';
  document.querySelector('#body pre').textContent = parsedData.body ? JSON.stringify(parsedData.body, null, 2) : '無數據';
  document.querySelector('#clothing pre').textContent = parsedData.clothing ? JSON.stringify(parsedData.clothing, null, 2) : '無數據';
  document.querySelector('#accessory pre').textContent = parsedData.accessory ? JSON.stringify(parsedData.accessory, null, 2) : '無數據';
  document.querySelector('#misc pre').textContent = parsedData.misc ? JSON.stringify(parsedData.misc, null, 2) : '無數據';
}

function saveFile() {
  const hexDisplay = document.getElementById('hex-display');
  hexDisplay.textContent = '正在儲存資料...';

  fetch('/edit/save_bak', {
    method: 'POST'
  })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => {
          throw new Error(err.error || '儲存失敗');
        }).catch(() => {
          throw new Error('無法解析伺服器回應');
        });
      }
      return response.json();
    })
    .then(result => {
      hexDisplay.textContent = result.message || '儲存成功！';
    })
    .catch(error => {
      hexDisplay.textContent = '儲存失敗：' + error.message;
    });
}

// 為了讓 HTML 中的 onclick 可以直接呼叫這個函式
// 這裡將 reloadFile 函式暴露到全域作用域
window.reloadFile = reloadFile;
// 暴露給 HTML
window.saveFile = saveFile;