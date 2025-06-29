// 全域存放從後端拿到的解析資料
let globalParsedData = null;
let autoSaveTimer = null;

// 第二層 tab 設定物件，key 是第一層 tab id，value 是陣列，裡面是 { key, label } 物件
const subTabs = {
  hair: [
    { key: 'back_hair', label: '後髮' },
    { key: 'front_hair', label: '前髮' },
    { key: 'side_hair', label: '側髮' },
    { key: 'style', label: '髮型樣式' } // 新增：用於測試下拉選單
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
    { key: 'chin', 'label': '下巴' },
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
    { key: 'author', label: '作者' } // 新增：用於測試下拉選單
  ]
};

// START: 新增 - 定義下拉選單插槽的 ID 陣列
const dropdownSlotIds = ['dropdown-1', 'dropdown-2', 'dropdown-3'];
// END: 新增

window.addEventListener('DOMContentLoaded', () => {
  console.log('DOMContentLoaded 事件觸發。'); // 新增日誌

  // 第一層 Tab 切換功能
  document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
      console.log(`點擊主 Tab: ${button.getAttribute('data-tab')}`); // 新增日誌
      // 移除所有第一層 tab 的 active 類
      document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
      // 加上目前點擊按鈕 active
      button.classList.add('active');

      const tabId = button.getAttribute('data-tab');

      // 產生並切換第二層 tab
      renderSubTabs(tabId);
    });
  });

  // 一開頁面直接用後端資料初始化頁面
  console.log('檢查 characterData 是否已定義...'); // 新增日誌
  if (typeof characterData !== 'undefined') {
    console.log('characterData 已定義，開始初始化頁面。'); // 新增日誌
    updateTabs(characterData);
    console.log('初始角色資料:', globalParsedData); // 調整 console 訊息
    // 自動選擇第一個可用的 tab 作為預設載入
    const firstTab = document.querySelector('.tab-button');
    if (firstTab) {
      const tabId = firstTab.getAttribute('data-tab');
      firstTab.classList.add('active');
      console.log(`自動載入第一個主 Tab: ${tabId}`); // 新增日誌
      renderSubTabs(tabId); // 這會觸發第二層 tab 的渲染，並在內部呼叫 renderSubTabContent

      // START: 修正 - 確保頁面載入時能正確觸發第一個 subTab 的內容和下拉選單載入
      const subTabList = subTabs[tabId];
      if (subTabList && subTabList.length > 0) {
        console.log(`自動載入第一個子 Tab: ${subTabList[0].key}`); // 新增日誌
        // 直接調用 renderSubTabContent，它會再呼叫 renderDropdowns
        renderSubTabContent(tabId, subTabList[0].key);
      } else {
        console.log(`第一個主 Tab (${tabId}) 沒有子 Tab。`); // 新增日誌
      }
      // END: 修正
    } else {
      console.log('未找到任何主 Tab 按鈕。'); // 新增日誌
    }
    
	showMessage('角色資料預載完成。');
    //document.getElementById('result-message').textContent = '角色資料預載完成。';
  } else {
    console.log('characterData 未定義，無法初始化頁面。'); // 新增日誌
	showMessage('無角色數據', 'warning');
    //document.getElementById('result-message').textContent = '無角色數據';
  }

  // 綁定 main-content 的 input 事件，觸發自動儲存
  const mainContent = document.getElementById('main-content');
  // 輸入事件，500ms debounce 自動儲存
  mainContent.addEventListener('input', () => {
    if (autoSaveTimer) clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => {
      autoSaveData();
    }, 5000);
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
  console.log('執行 updateTabs 函數。'); // 新增日誌
  globalParsedData = parsedData;
  // 這裡不再更新任何 <pre> 或 tab-content，因為統一用 main-content 顯示
}

/**
 * 產生第二層 tab 按鈕並加入事件監聽
 * @param {string} mainTabKey - 第一層 tab id
 */
function renderSubTabs(mainTabKey) {
  console.log(`執行 renderSubTabs 函數，主 Tab: ${mainTabKey}`); // 新增日誌
  const container = document.getElementById('sub-tab-buttons');
  container.innerHTML = ''; // 清空舊按鈕

  // START: 修改 - 點擊第一層 Tab 時，清空並隱藏所有下拉選單
  const dropdownContainer = document.getElementById('dropdown-container');
  dropdownContainer.classList.remove('show'); // 隱藏整個下拉選單容器
  dropdownSlotIds.forEach(slotId => {
      const slot = document.getElementById(slotId);
      if (slot) {
          slot.innerHTML = ''; // 清空插槽內容
          slot.style.display = 'none'; // 隱藏插槽
      }
  });
  console.log('已清空並隱藏所有下拉選單插槽。'); // 新增日誌
  // END: 修改

  const tabs = subTabs[mainTabKey] || [];
  console.log(`主 Tab (${mainTabKey}) 的子 Tab 數量: ${tabs.length}`); // 新增日誌

  tabs.forEach((tab, index) => {
    const btn = document.createElement('button');
    btn.className = 'sub-tab-button';
    if (index === 0) btn.classList.add('active');
    btn.textContent = tab.label;   // 顯示中文標籤
    btn.dataset.tabKey = tab.key;  // 儲存英文 key

    btn.addEventListener('click', () => {
      console.log(`點擊子 Tab: ${tab.key}`); // 新增日誌
      // 移除所有第二層 tab 按鈕 active
      document.querySelectorAll('.sub-tab-button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // 顯示內容並載入下拉選單
      renderSubTabContent(mainTabKey, tab.key);
    });

    container.appendChild(btn);
  });

  if (tabs.length > 0) {
    console.log(`renderSubTabs: 預設載入第一個子 Tab 的內容和下拉選單 (${mainTabKey}/${tabs[0].key})`); // 新增日誌
    // 預設載入第一個子 tab 的內容和下拉選單
    renderSubTabContent(mainTabKey, tabs[0].key);
  } else {
    console.log(`renderSubTabs: 主 Tab (${mainTabKey}) 沒有子 Tab，清空 main-content。`); // 新增日誌
    document.getElementById('main-content').textContent = '無第二層資料';
    // START: 新增 - 如果沒有子 Tab，也確保下拉選單被清空和隱藏
    const dropdownContainer = document.getElementById('dropdown-container');
    dropdownContainer.classList.remove('show');
    // END: 新增
  }
}

/**
 * 在固定的 main-content 容器裡，顯示 JSON 資料
 * @param {string} mainTabKey 
 * @param {string} subTabKey 
 */
function renderSubTabContent(mainTabKey, subTabKey) {
  console.log(`執行 renderSubTabContent 函數，主 Tab: ${mainTabKey}, 子 Tab: ${subTabKey}`); // 新增日誌
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
    console.log(`main-content 已更新為 ${mainTabKey}/${subTabKey} 的資料。`); // 新增日誌
  } else {
    mainContent.textContent = `找不到資料：第一層 "${mainTabKey}"，第二層 "${subTabKey}"`;
    mainContent.dataset.mainTabKey = '';
    mainContent.dataset.subTabKey = '';
    console.log(`main-content 顯示「找不到資料」訊息 (${mainTabKey}/${subTabKey})。`); // 新增日誌
  }

  // START: 修改 - 在 renderSubTabContent 內部呼叫 fetch 並渲染下拉選單
  // 這裡假設後端 API 路徑是 /api/options/<tab>/<subTab>
  console.log(`準備呼叫 fetchAndRenderDropdowns 函數 (${mainTabKey}/${subTabKey}).`); // 新增日誌
  fetchAndRenderDropdowns(mainTabKey, subTabKey);
  // END: 修改
}

/**
 * 自動儲存目前 main-content 的資料，傳回後端更新
 */
function autoSaveData() {
  console.log('執行 autoSaveData 函數。'); // 新增日誌
  const mainContent = document.getElementById('main-content');
  //const hexDisplay = document.getElementById('result-message');

  const mainTabKey = mainContent.dataset.mainTabKey;
  const subTabKey = mainContent.dataset.subTabKey;

  if (!mainTabKey || !subTabKey) {
    showMessage('無法儲存：無效的 tab 鍵值', 'error');
	//hexDisplay.textContent = '無法儲存：無效的 tab 鍵值';
    console.error('autoSaveData: 無效的 tab 鍵值。'); // 新增日誌
    return;
  }

  let newData;
  try {
    newData = JSON.parse(mainContent.textContent);
  } catch (err) {
	showMessage('JSON 格式錯誤，無法儲存', 'error');
    //hexDisplay.textContent = 'JSON 格式錯誤，無法儲存';
    console.error('autoSaveData: JSON 格式錯誤。', err); // 新增日誌
    return;
  }

  showMessage(`正在儲存 ${mainTabKey} / ${subTabKey} ...`);
  //hexDisplay.textContent = `正在儲存 ${mainTabKey} / ${subTabKey} ...`;

  fetch(`/api/character/update/${encodeURIComponent(mainTabKey)}/${encodeURIComponent(subTabKey)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ data: newData })
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
    showMessage(result.message || '儲存成功！');
    console.log('autoSaveData: 儲存成功。', result);
    // 更新全域資料狀態，避免下一次讀取舊資料
    if (globalParsedData && globalParsedData[mainTabKey]) {
      globalParsedData[mainTabKey][subTabKey] = newData;
    }
	// 如果有更新全域版本號，呼叫 pingPongSave
    if (result.global_version_updated) {
      console.log('偵測到全域版本號更新，觸發 pingPongSave');
      pingPongSave();
    }
  })
  .catch(error => {
    showMessage('儲存失敗：' + error.message, 'error');
    console.error('autoSaveData: 儲存失敗。', error);
  });
}

/**
 * 以下是你原本的 ajax 請求範例，可配合使用
 * 例如呼叫 reloadFile() 或 saveFile() 來更新 globalParsedData
 */

function reloadFile() {
  console.log('執行 reloadFile 函數。'); // 新增日誌
  //const hexDisplay = document.getElementById('result-message');
  showMessage('正在重新載入檔案數據...');
  //hexDisplay.textContent = '正在重新載入檔案數據...';

  fetch('/api/character/reload')
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
        showMessage('錯誤：' + data.error, 'error'); 
  	    //hexDisplay.textContent = '錯誤：' + data.error;
        console.error('reloadFile: 伺服器回傳錯誤。', data.error); // 新增日誌
        return;
      }

      updateTabs(data);
      showMessage('重新載入檔案數據成功。');
	  //hexDisplay.textContent = '重新載入檔案數據成功。';
      console.log('reloadFile: 重新載入成功。'); // 新增日誌

      // 重新渲染第二層 tab，保持目前第一層 tab 按鈕 active
      const activeMainTab = document.querySelector('.tab-button.active');
      if (activeMainTab) {
        console.log(`reloadFile: 重新渲染主 Tab: ${activeMainTab.getAttribute('data-tab')}`); // 新增日誌
        renderSubTabs(activeMainTab.getAttribute('data-tab'));
      } else {
        // 如果沒有 active tab，預設載入第一個
        const firstTab = document.querySelector('.tab-button');
        if (firstTab) {
            console.log(`reloadFile: 無 active 主 Tab，載入第一個主 Tab: ${firstTab.getAttribute('data-tab')}`); // 新增日誌
            renderSubTabs(firstTab.getAttribute('data-tab'));
        } else {
            console.warn('reloadFile: 未找到任何主 Tab 按鈕可供重新渲染。'); // 新增日誌
        }
      }
    })
    .catch(err => {
	  showMessage('載入失敗：' + err.message, 'error');	
      //hexDisplay.textContent = '載入失敗：' + err.message;
      console.error('reloadFile: 載入失敗。', err); // 新增日誌
    });
}

function saveFile() {
  console.log('執行 saveFile 函數。'); // 新增日誌
  //const hexDisplay = document.getElementById('result-message');
  showMessage('正在儲存資料...');
  //hexDisplay.textContent = '正在儲存資料...';

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
      showMessage(result.message || '儲存成功！');
	  //hexDisplay.textContent = result.message || '儲存成功！';
      console.log('saveFile: 儲存成功。', result); // 新增日誌
    })
    .catch(error => {
	  showMessage('儲存失敗：' + error.message, 'error');
      //hexDisplay.textContent = '儲存失敗：' + error.message;
      console.error('saveFile: 儲存失敗。', error); // 新增日誌
    });
}

/**
 * 觸發後端儲存待處理角色的函式。
 * 會持續呼叫後端路由，直到沒有待儲存的檔案為止。
 */
async function pingPongSave() {
    let savedCount = 0;

    async function saveNext() {
        try {
            // 呼叫後端儲存待處理檔案的路由
            const response = await fetch('/api/character/ping_pong_save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`伺服器回應錯誤: ${response.status} ${response.statusText} - ${errorText}`);
            }

            const data = await response.json();

            if (data.character_id) {
                savedCount++;
                showMessage(`成功儲存檔案: ${data.character_id}。正在檢查是否有更多檔案...`);
                await saveNext(); // 繼續處理下一個
            } else {
                // 沒有更多檔案要存了
                showMessage(`所有待儲存檔案 ${savedCount} 個已處理完畢。`);
            }
        } catch (err) {
            console.error("儲存失敗", err);
            showMessage(`儲存失敗: ${err.message}`, 'error');
        }
    }

    showMessage("正在檢查並儲存待處理檔案...");
    await saveNext();
}


/**
 * 建立一個 <select> 元素及其選項。
 * @param {string} id - <select> 元素的 ID。
 * @param {Array<Object>} options - 選項陣列，每個物件包含 label 和 value。
 * @param {*} defaultValue - 預設選中的值。
 * @param {Function} onChangeCallback - 當選項改變時的回呼函數。
 * @returns {HTMLSelectElement} 建立的 select 元素。
 */
function createSelect(id, options, defaultValue, onChangeCallback) {
  console.log(`執行 createSelect 函數，ID: ${id}`); // 新增日誌
  const select = document.createElement('select');
  select.id = id;

  // START: 修正 - 移除手動添加「請選擇」選項的邏輯
  // 由於後端已經在 options 陣列中提供了「請選擇」選項，
  // 這裡不再需要手動添加，避免重複。
  // const defaultOption = document.createElement('option');
  // defaultOption.value = ''; // 空值
  // defaultOption.textContent = '請選擇'; // 提示文字
  // select.appendChild(defaultOption);
  // END: 修正

  options.forEach(opt => {
    const option = document.createElement('option');
    // 將 value 序列化為 JSON 字串，以便在 option.value 中儲存複雜物件
    option.value = JSON.stringify(opt.value);
    option.textContent = opt.label;
    
    // 比較 defaultValue 和 opt.value，如果相同則選中
    // 處理 defaultValue 可能是物件或簡單值的情況
    if (typeof defaultValue === 'object' && defaultValue !== null) {
        if (JSON.stringify(opt.value) === JSON.stringify(defaultValue)) {
            option.selected = true;
        }
    } else {
        if (opt.value === defaultValue) {
            option.selected = true;
        }
    }
    select.appendChild(option);
  });

  select.addEventListener('change', e => {
    console.log(`Select 元素 ${id} 值改變。`); // 新增日誌
    const selectedValueStr = e.target.value;
    let selected;
    try {
        selected = selectedValueStr === '' ? null : JSON.parse(selectedValueStr); // 如果選取空選項，則為 null
    } catch (e) {
        selected = selectedValueStr; // 如果解析失敗 (例如是簡單字串)，則直接使用字串
    }
    onChangeCallback(selected);
  });
  return select;
}

// START: 修改 - 核心邏輯：動態獲取資料並渲染下拉選單
/**
 * 從後端 API 獲取選項資料並渲染下拉選單到對應插槽。
 * @param {string} mainTab - 主 tab 的 key。
 * @param {string} subTab - 子 tab 的 key。
 */
async function fetchAndRenderDropdowns(mainTab, subTab) {
  console.log(`執行 fetchAndRenderDropdowns 函數，請求: /api/options/${mainTab}/${subTab}`); // 新增日誌
  // 清空並隱藏所有下拉選單插槽
  dropdownSlotIds.forEach(slotId => {
      const slot = document.getElementById(slotId);
      if (slot) {
          slot.innerHTML = ''; // 清空內容
          slot.style.display = 'none'; // 隱藏插槽
      }
  });

  const dropdownContainer = document.getElementById('dropdown-container');
  dropdownContainer.classList.remove('show'); // 先隱藏整個容器

  //const hexDisplay = document.getElementById('result-message');
  showMessage(`正在載入 ${mainTab}/${subTab} 的下拉選單選項...`);
  //hexDisplay.textContent = `正在載入 ${mainTab}/${subTab} 的下拉選單選項...`;

  try {
    const response = await fetch(`/api/options/${mainTab}/${subTab}`);
    if (!response.ok) {
      throw new Error(`HTTP 錯誤: ${response.status}`);
    }
    const result = await response.json();
    console.log(`收到後端回應 /api/options/${mainTab}/${subTab}:`, result); // <-- 關鍵日誌

    let dropdownsToRender = [];

    if (result.dropdowns && Array.isArray(result.dropdowns)) {
        dropdownsToRender = result.dropdowns;
        console.log(`後端回傳 ${dropdownsToRender.length} 個下拉選單配置。`); // 新增日誌
    } else {
        // START: 調整錯誤訊息
        if (result.dropdowns === undefined) {
            showMessage(`後端 API /api/options/${mainTab}/${subTab} 回傳格式不符合預期 (缺少 "dropdowns" 鍵)。`, 'warning');
			//hexDisplay.textContent = `後端 API /api/options/${mainTab}/${subTab} 回傳格式不符合預期 (缺少 "dropdowns" 鍵)。`;
            console.warn(`fetchAndRenderDropdowns: 後端回應缺少 "dropdowns" 鍵。`, result); // 新增日誌
        } else if (!Array.isArray(result.dropdowns)) {
            showMessage(`後端 API /api/options/${mainTab}/${subTab} 回傳的 "dropdowns" 不是陣列。`, 'warning');
			//hexDisplay.textContent = `後端 API /api/options/${mainTab}/${subTab} 回傳的 "dropdowns" 不是陣列。`;
            console.warn(`fetchAndRenderDropdowns: 後端回應的 "dropdowns" 不是陣列。`, result); // 新增日誌
        } else {
            showMessage(`後端 API /api/options/${mainTab}/${subTab} 回傳格式未知錯誤。`, 'warning');
			//hexDisplay.textContent = `後端 API /api/options/${mainTab}/${subTab} 回傳格式未知錯誤。`;
            console.warn(`fetchAndRenderDropdowns: 後端回應格式未知錯誤。`, result); // 新增日誌
        }
        // END: 調整錯誤訊息
        return; 
    }

    // 如果 dropdownsToRender 陣列為空
    if (!dropdownsToRender || dropdownsToRender.length === 0) {
      showMessage(`無 ${mainTab}/${subTab} 的下拉選單選項。`, 'error');
	  //hexDisplay.textContent = `無 ${mainTab}/${subTab} 的下拉選單選項。`; // 這就是您看到的訊息
      console.log(`fetchAndRenderDropdowns: 後端回傳的下拉選單配置為空。`); // 新增日誌
      return;
    }

    // 顯示整個下拉選單容器
    dropdownContainer.classList.add('show');
    console.log('下拉選單容器已顯示。'); // 新增日誌

    let slotIndex = 0;
    for (const dropdownConfig of dropdownsToRender) {
      if (slotIndex >= dropdownSlotIds.length) {
          console.warn(`fetchAndRenderDropdowns: 超過三個下拉選單插槽限制，跳過剩餘配置。`); // 新增日誌
          break; // 超過三個插槽則停止
      }

      const slotId = dropdownSlotIds[slotIndex];
      const slot = document.getElementById(slotId);

      if (slot) {
        slot.innerHTML = ''; // 清空舊內容
        
        const label = document.createElement('label');
        label.textContent = dropdownConfig.displayLabel; // 後端提供顯示名稱

        // 從 globalParsedData 中獲取當前選中的值
        // 假設 `dropdownConfig.dataKey` 對應到 `globalParsedData[mainTab][subTab][dataKey]`
        let currentDataForDropdown = null;
        if (globalParsedData && globalParsedData[mainTab] && globalParsedData[mainTab][subTab]) {
            currentDataForDropdown = globalParsedData[mainTab][subTab][dropdownConfig.dataKey];
            console.log(`fetchAndRenderDropdowns: 取得當前資料 for ${dropdownConfig.dataKey}:`, currentDataForDropdown); // 新增日誌
        } else {
            console.log(`fetchAndRenderDropdowns: globalParsedData 中無對應 ${mainTab}/${subTab}/${dropdownConfig.dataKey} 的資料。`); // 新增日誌
        }


        const select = createSelect(
          `${slotId}-${dropdownConfig.dataKey}`, // 每個 select 都有唯一 ID
          dropdownConfig.options,
          currentDataForDropdown || dropdownConfig.defaultValue, // 優先使用當前資料，否則使用後端提供的預設值
          selected => {
            // 更新 globalParsedData 中對應的值
            if (globalParsedData && globalParsedData[mainTab] && globalParsedData[mainTab][subTab]) {
                globalParsedData[mainTab][subTab][dropdownConfig.dataKey] = selected;
                // 同步更新 main-content 顯示的 JSON
                const mainContent = document.getElementById('main-content');
                mainContent.textContent = JSON.stringify(
                    globalParsedData[mainTab][subTab],
                    (key, value) => key.startsWith('!') ? undefined : value,
                    2
                );
                // 觸發自動儲存
                if (autoSaveTimer) clearTimeout(autoSaveTimer);
                autoSaveTimer = setTimeout(() => {
                    autoSaveData();
                }, 500);
                console.log(`下拉選單值已更新到 globalParsedData: ${mainTab}/${subTab}/${dropdownConfig.dataKey} =`, selected); // 新增日誌
            } else {
                console.warn('無法更新 globalParsedData，因為路徑不存在。'); // 新增日誌
            }
          }
        );

        slot.appendChild(label);
        slot.appendChild(select);
        slot.style.display = 'flex'; // 顯示此插槽
        console.log(`已渲染下拉選單到 ${slotId}，標籤: ${dropdownConfig.displayLabel}`); // 新增日誌
        slotIndex++;
      } else {
          console.error(`fetchAndRenderDropdowns: 未找到 ID 為 ${slotId} 的下拉選單插槽。`); // 新增日誌
      }
    }
    showMessage(`已載入 ${slotIndex} 個下拉選單。`);
	//hexDisplay.textContent = `已載入 ${slotIndex} 個下拉選單。`;
    console.log(`fetchAndRenderDropdowns: 總共載入 ${slotIndex} 個下拉選單。`); // 新增日誌

  } catch (error) {
    showMessage(`載入下拉選單失敗：${error.message}`, 'error');
	//hexDisplay.textContent = `載入下拉選單失敗：${error.message}`;
    console.error('載入下拉選單錯誤:', error); // 新增日誌
  } finally {
    // 無論成功或失敗，都嘗試定位下拉選單
    console.log('嘗試定位下拉選單。'); // 新增日誌
    positionDropdown();
  }
}
// END: 修改

function positionDropdown() {
  console.log('執行 positionDropdown 函數。'); // 新增日誌
  const dropdown = document.getElementById('dropdown-container');
  const mainContent = document.getElementById('main-content');
  const tabContainer = document.querySelector('.tab-container');

  if (!dropdown || !mainContent || !tabContainer) {
      console.warn("定位下拉選單元素不存在。");
      return;
  }

  const mainRect = mainContent.getBoundingClientRect();
  const containerRect = tabContainer.getBoundingClientRect();
  const dropdownRect = dropdown.getBoundingClientRect(); // 取得下拉選單實際寬高

  // 計算相對於 tab-container 的位置
  // 右上角對齊 main-content 的右邊和頂部，並留一些邊距
  const topOffset = (mainRect.top - containerRect.top) + 10;
  // 由於 dropdown 是 flex-direction: column，其寬度會被內容撐開，所以要用實際寬度計算
  const rightOffset = (containerRect.right - mainRect.right) + 10; // 距離 mainContent 右邊的距離

  dropdown.style.position = 'absolute';
  dropdown.style.top = `${topOffset}px`;
  dropdown.style.right = `${rightOffset}px`; // 使用 right 屬性來對齊右邊
  // dropdown.style.left = (mainRect.right - containerRect.left - dropdownRect.width - 10) + 'px'; // 舊的 left 計算方式
  console.log(`下拉選單定位完成：Top: ${topOffset}px, Right: ${rightOffset}px`); // 新增日誌
}

function showMessage(text, type = 'success') {
  const el = document.getElementById('result-message');
  el.textContent = text;
  el.className = '';
  el.classList.add(type);
}

window.reloadFile = reloadFile;
window.saveFile = saveFile;
window.pingPongSave = pingPoneSave;
