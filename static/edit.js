// 全域存放從後端拿到的解析資料
let globalParsedData = null;
let autoSaveTimer = null;

// 第二層 tab 設定物件，key 是第一層 tab id，value 是陣列，裡面是 { key, label } 物件
const subTabs = {
  hair: [
    { key: 'back_hair', label: '後髮' },
    { key: 'front_hair', label: '前髮' },
    { key: 'side_hair', label: '側髮' }
  ],
  face: [
    { key: 'overall', label: '全体' },
    { key: 'ears', label: '耳朵' },
    { key: 'eyebrows', label: '眉毛' },
    { key: 'eyelashes', label: '睫毛' },
    { key: 'eyes', label: '眼睛' },
    { key: 'eyeballs', label: '眼球' },
    { key: 'nose', label: '鼻子' },
    { key: 'cheeks', label: '臉頰' },
    { key: 'mouth', label: '嘴唇' },
    { key: 'chin', label: '下巴' },
    { key: 'mole', label: '痣' },
    { key: 'makeup', label: '化妝' },
    { key: 'tattoo', label: '刺青' }
  ],
  body: [
    { key: 'overall', label: '全体' },
    { key: 'breast', label: '胸部' },
    { key: 'upper_body', label: '上半身' },
    { key: 'lower_body', label: '下半身' },
    { key: 'arms', label: '腕' },
    { key: 'legs', label: '腳' },
    { key: 'nails', label: '指甲' },
    { key: 'pubic_hair', label: '陰毛' },
    { key: 'tan_lines', label: '曬痕' },
    { key: 'tattoo', label: '刺青' }
  ],
  clothing: [
    { key: 'top', label: '上衣' },
    { key: 'bottom', label: '下著' },
    { key: 'bra', label: '胸罩' },
    { key: 'panty', label: '內褲' },
    { key: 'swimsuit', label: '泳衣' },
    { key: 'swimsuit_top', label: '泳衣-上衣' },
    { key: 'swimsuit_bottom', label: '泳衣-下著' },
    { key: 'gloves', label: '手套' },
    { key: 'pantyhose', label: '褲襪' },
    { key: 'socks', label: '襪子' },
    { key: 'shoes', label: '鞋子' }
  ],
  accessory: [
    { key: 'accessory_01', label: '01' },
    { key: 'accessory_02', label: '02' },
    { key: 'accessory_03', label: '03' },
    { key: 'accessory_04', label: '04' },
    { key: 'accessory_05', label: '05' },
    { key: 'accessory_06', label: '06' },
    { key: 'accessory_07', label: '07' },
    { key: 'accessory_08', label: '08' },
    { key: 'accessory_09', label: '09' },
    { key: 'accessory_10', label: '10' }
  ],
  story: [
    { key: 'general', label: '全域' },
    { key: 'character', label: '角色' },
    { key: 'scenario', label: '情境' },
  ]
};

window.addEventListener('DOMContentLoaded', () => {
  // 第一層 Tab 切換功能
  document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
      // 移除所有第一層 tab 的 active 類
      document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
      // 加上目前點擊按鈕 active
      button.classList.add('active');

      const tabId = button.getAttribute('data-tab');

      // 產生並切換第二層 tab
      renderSubTabs(tabId);
    });
  });

  // 頁面載入時立即初始化第二層 tab（預設第一個第一層 tab 為 hair）
  //renderSubTabs('hair');

  // 一開頁面直接用後端資料初始化頁面
  if (typeof characterData !== 'undefined') {
    updateTabs(characterData);
	console.log(globalParsedData);
	// 自動選擇第一個可用的 tab 作為預設載入
    const firstTab = document.querySelector('.tab-button');
    if (firstTab) {
      const tabId = firstTab.getAttribute('data-tab');
      firstTab.classList.add('active');
      renderSubTabs(tabId);

      const subTabList = subTabs[tabId];
      if (subTabList && subTabList.length > 0) {
        renderSubTabContent(tabId, subTabList[0].key);
      }
    }
	
    document.getElementById('hex-display').textContent = '角色資料預載完成。';
  } else {
    document.getElementById('hex-display').textContent = '無角色數據';
  }

  // 綁定 main-content 的 input 事件，觸發自動儲存
  const mainContent = document.getElementById('main-content');
  // 輸入事件，500ms debounce 自動儲存
  mainContent.addEventListener('input', () => {
    if (autoSaveTimer) clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => {
      autoSaveData();
    }, 500);
  });

  // 離焦事件，立即儲存（取消 debounce）
  mainContent.addEventListener('blur', () => {
    if (autoSaveTimer) {
      clearTimeout(autoSaveTimer);
      autoSaveTimer = null;
    }
    autoSaveData();
  });
});

/**
 * 從後端獲取資料並更新
 */
function updateTabs(parsedData) {
  globalParsedData = parsedData;
  // 這裡不再更新任何 <pre> 或 tab-content，因為統一用 main-content 顯示
}

/**
 * 產生第二層 tab 按鈕並加入事件監聽
 * @param {string} mainTabKey - 第一層 tab id
 */
function renderSubTabs(mainTabKey) {
  const container = document.getElementById('sub-tab-buttons');
  container.innerHTML = ''; // 清空舊按鈕

  const tabs = subTabs[mainTabKey] || [];

  tabs.forEach((tab, index) => {
    const btn = document.createElement('button');
    btn.className = 'sub-tab-button';
    if (index === 0) btn.classList.add('active');
    btn.textContent = tab.label;   // 顯示中文標籤
    btn.dataset.tabKey = tab.key;  // 儲存英文 key

    btn.addEventListener('click', () => {
      // 移除所有第二層 tab 按鈕 active
      document.querySelectorAll('.sub-tab-button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // 顯示內容
      renderSubTabContent(mainTabKey, tab.key);
    });

    container.appendChild(btn);
  });

  if (tabs.length > 0) {
    renderSubTabContent(mainTabKey, tabs[0].key);
  } else {
    document.getElementById('main-content').textContent = '無第二層資料';
  }
}

/**
 * 在固定的 main-content 容器裡，顯示 JSON 資料
 * @param {string} mainTabKey 
 * @param {string} subTabKey 
 */
function renderSubTabContent(mainTabKey, subTabKey) {
  const mainContent = document.getElementById('main-content');
  if (
    globalParsedData &&
    globalParsedData[mainTabKey] &&
    globalParsedData[mainTabKey][subTabKey] !== undefined
  ) {
    mainContent.textContent = JSON.stringify(
      globalParsedData[mainTabKey][subTabKey],
      (key, value) => {
        if (key.startsWith('!')) {
          return undefined; // 會跳過這個 key
        }
        return value;
      },
      2);
    // 紀錄目前編輯的 tab key
    mainContent.dataset.mainTabKey = mainTabKey;
    mainContent.dataset.subTabKey = subTabKey;
  } else {
    mainContent.textContent = `找不到資料：第一層 "${mainTabKey}"，第二層 "${subTabKey}"`;
    mainContent.dataset.mainTabKey = '';
    mainContent.dataset.subTabKey = '';
  }
}

/**
 * 自動儲存目前 main-content 的資料，傳回後端更新
 */
function autoSaveData() {
  const mainContent = document.getElementById('main-content');
  const hexDisplay = document.getElementById('hex-display');

  const mainTabKey = mainContent.dataset.mainTabKey;
  const subTabKey = mainContent.dataset.subTabKey;

  if (!mainTabKey || !subTabKey) {
    hexDisplay.textContent = '無法儲存：無效的 tab 鍵值';
    return;
  }

  let newData;
  try {
    newData = JSON.parse(mainContent.textContent);
  } catch (err) {
    hexDisplay.textContent = 'JSON 格式錯誤，無法儲存';
    return;
  }

  hexDisplay.textContent = `正在儲存 ${mainTabKey} / ${subTabKey} ...`;

  fetch('/edit/update', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mainTabKey,
      subTabKey,
      data: newData
    })
  })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => {
          throw new Error(err.error || `HTTP 錯誤: ${response.status}`);
        }).catch(() => {
          throw new Error(`HTTP 錯誤: ${response.status}`);
        });
      }
      return response.json();
    })
    .then(result => {
      hexDisplay.textContent = result.message || '儲存成功！';
      // 更新全域資料狀態，避免下一次讀取舊資料
      if (globalParsedData && globalParsedData[mainTabKey]) {
        globalParsedData[mainTabKey][subTabKey] = newData;
      }
    })
    .catch(error => {
      hexDisplay.textContent = '儲存失敗：' + error.message;
    });
}

/**
 * 以下是你原本的 ajax 請求範例，可配合使用
 * 例如呼叫 reloadFile() 或 saveFile() 來更新 globalParsedData
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

      // 重新渲染第二層 tab，保持目前第一層 tab 按鈕 active
      const activeMainTab = document.querySelector('.tab-button.active');
      if (activeMainTab) {
        renderSubTabs(activeMainTab.getAttribute('data-tab'));
      } else {
        renderSubTabs('fixed_header');
      }
    })
    .catch(err => {
      hexDisplay.textContent = '載入失敗：' + err.message;
    });
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

window.reloadFile = reloadFile;
window.saveFile = saveFile;
