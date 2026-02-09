// 全域存放從後端拿到的解析資料
let globalParsedData = null;
let autoSaveTimer = null;
let autoSaveRemarkTimer = null;

// 第二層 tab 設定物件，key 是第一層 tab id，value 是陣列，裡面是 { key, label } 物件
const subTabs = {
  hair: [
    { key: 'back_hair', label: '後髮' },
    { key: 'front_hair', label: '前髮' },
    { key: 'side_hair', label: '側髮' },
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
    //{ key: 'general', label: '全域' },
    { key: 'profile', label: '簡介' },
    { key: 'scenario', label: '場景' },
    { key: 'backstage', label: '幕後' }
  ]
};

// START: 新增 - 定義下拉選單插槽的 ID 陣列
const dropdownSlotIds = ['dropdown-1', 'dropdown-2', 'dropdown-3'];
// END: 新增

window.addEventListener('DOMContentLoaded', () => {
  //console.log('DOMContentLoaded 事件觸發。'); // 新增日誌

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
  //console.log('檢查 characterData 是否已定義...'); // 新增日誌
  if (typeof characterData !== 'undefined') {
    //console.log('characterData 已定義，開始初始化頁面。'); // 新增日誌
    updateTabs(characterData);
    //console.log('初始角色資料:', globalParsedData); // 調整 console 訊息
    // 自動選擇第一個可用的 tab 作為預設載入
    const firstTab = document.querySelector('.tab-button');
    if (firstTab) {
      const tabId = firstTab.getAttribute('data-tab');
      firstTab.classList.add('active');
      //console.log(`自動載入第一個主 Tab: ${tabId}`); // 新增日誌
      renderSubTabs(tabId); // 這會觸發第二層 tab 的渲染，並在內部呼叫 renderSubTabContent

      // START: 修正 - 確保頁面載入時能正確觸發第一個 subTab 的內容和下拉選單載入
      const subTabList = subTabs[tabId];
      if (subTabList && subTabList.length > 0) {
        //console.log(`自動載入第一個子 Tab: ${subTabList[0].key}`); // 新增日誌
        // 直接調用 renderSubTabContent，它會再呼叫 renderDropdowns
        renderSubTabContent(tabId, subTabList[0].key);
      } else {
        //console.log(`第一個主 Tab (${tabId}) 沒有子 Tab。`); // 新增日誌
      }
      // END: 修正
    } else {
      //console.log('未找到任何主 Tab 按鈕。'); // 新增日誌
    }
    
	showMessage('角色資料預載完成。');
    //document.getElementById('result-message').textContent = '角色資料預載完成。';
  } else {
    //console.log('characterData 未定義，無法初始化頁面。'); // 新增日誌
	showMessage('無角色數據', 'warning');
    //document.getElementById('result-message').textContent = '無角色數據';
  }

  // 綁定 main-content 的 input 事件，觸發自動儲存
  const mainContent = document.getElementById('main-content');
  
  let hasChanged = false;  // ← 宣告在事件處理器外，整個模組都能共用
  
  // 輸入事件，30 sec debounce 自動儲存
  mainContent.addEventListener('input', () => {
	hasChanged = true;
    if (autoSaveTimer) clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => {
      autoSaveData();
    }, 30000);
  });

  // 離焦事件，立即儲存（取消 debounce）
  mainContent.addEventListener('blur', () => {
    if (autoSaveTimer) {
      clearTimeout(autoSaveTimer);
      autoSaveTimer = null;
    }
	if (hasChanged) {
      autoSaveData();
      hasChanged = false;
    } 
  });
  
  // 綁定 file-id-remark 也要防抖動...
  const remarkContent = document.getElementById('file-id-remark');
  let remarkHasChanged = false;	
  // 綁定 input 事件
  remarkContent.addEventListener('input', () => {
    remarkHasChanged = true;
    if (autoSaveRemarkTimer) clearTimeout(autoSaveRemarkTimer);
    autoSaveRemarkTimer = setTimeout(() => {
      const newRemark = remarkContent.innerText.trim();
	  console.log("input trigger.");
      updateRemark(newRemark);
	}, 10000);
  });

  // 離焦立刻儲存
  remarkContent.addEventListener('blur', () => {
    if (autoSaveRemarkTimer) {
      clearTimeout(autoSaveRemarkTimer);
	  autoSaveRemarkTimer = null;
	}
	if (remarkHasChanged) {
      const newRemark = remarkContent.innerText.trim();
	  console.log("blur trigger.");
      updateRemark(newRemark);
	  remarkHasChanged = false;
	}
  });
  
  // 綁定 Status Radio Group
  const statusRadios = document.querySelectorAll('input[name="file-status"]');
  statusRadios.forEach(radio => {
    radio.addEventListener('change', () => {
      if (radio.checked) {
        const newStatus = radio.value;
        console.log("status trigger: " + newStatus);
        updateStatus(newStatus);
      }
    });
  });  
  
});

function updateMainContent(strJson, autoSave = false) {
  const mainContent = document.getElementById('main-content');

  if (!mainContent) {
    console.error(`找不到 ID 為 "main-content" 的元素。`);
    return;
  }
  
  try {
    mainContent.textContent = JSON.stringify(
      strJson,
      (key, value) => key.startsWith('!') ? undefined : value,
      2
    );
  } catch (e) {
	  console.error(`處理資料並轉換為字串時發生錯誤：`, e);
	  mainContent.textContent = '';
	  return;
  }
  
  if (autoSave) {
    // 觸發自動儲存（如果需要）
    if (autoSaveTimer) clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => {
      autoSaveData();
    }, 500);
  }
}

/**
 * 從後端獲取資料並更新
 */
function updateTabs(parsedData) {
  //console.log('執行 updateTabs 函數。'); // 新增日誌
  globalParsedData = parsedData;
  // 這裡不再更新任何 <pre> 或 tab-content，因為統一用 main-content 顯示
}

/**
 * 產生第二層 tab 按鈕並加入事件監聽
 * @param {string} mainTabKey - 第一層 tab id
 */
function renderSubTabs(mainTabKey) {
  //console.log(`執行 renderSubTabs 函數，主 Tab: ${mainTabKey}`); // 新增日誌
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
  //console.log('已清空並隱藏所有下拉選單插槽。'); // 新增日誌
  // END: 修改

  const tabs = subTabs[mainTabKey] || [];
  //console.log(`主 Tab (${mainTabKey}) 的子 Tab 數量: ${tabs.length}`); // 新增日誌

  tabs.forEach((tab, index) => {
    const btn = document.createElement('button');
    btn.className = 'sub-tab-button';
    if (index === 0) btn.classList.add('active');
    btn.textContent = tab.label;   // 顯示中文標籤
    btn.dataset.tabKey = tab.key;  // 儲存英文 key

    btn.addEventListener('click', () => {
      //console.log(`點擊子 Tab: ${tab.key}`); // 新增日誌
      // 移除所有第二層 tab 按鈕 active
      document.querySelectorAll('.sub-tab-button').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // 顯示內容並載入下拉選單
      renderSubTabContent(mainTabKey, tab.key);
    });

    container.appendChild(btn);
  });

  if (tabs.length > 0) {
    //console.log(`renderSubTabs: 預設載入第一個子 Tab 的內容和下拉選單 (${mainTabKey}/${tabs[0].key})`); // 新增日誌
    // 預設載入第一個子 tab 的內容和下拉選單
    renderSubTabContent(mainTabKey, tabs[0].key);
  } else {
    //console.log(`renderSubTabs: 主 Tab (${mainTabKey}) 沒有子 Tab，清空 main-content。`); // 新增日誌
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
  //console.log(`執行 renderSubTabContent 函數，主 Tab: ${mainTabKey}, 子 Tab: ${subTabKey}`); // 新增日誌
  const mainContent = document.getElementById('main-content');
  if (
    globalParsedData &&
    globalParsedData[mainTabKey] &&
    globalParsedData[mainTabKey][subTabKey] !== undefined
  ) {
    updateMainContent(globalParsedData[mainTabKey][subTabKey], false);	  
    // 紀錄目前編輯的 tab key
    mainContent.dataset.mainTabKey = mainTabKey;
    mainContent.dataset.subTabKey = subTabKey;
    //console.log(`main-content 已更新為 ${mainTabKey}/${subTabKey} 的資料。`); // 新增日誌
  } else {
    mainContent.textContent = `找不到資料：第一層 "${mainTabKey}"，第二層 "${subTabKey}"`;
    mainContent.dataset.mainTabKey = '';
    mainContent.dataset.subTabKey = '';
    console.log(`main-content 顯示「找不到資料」訊息 (${mainTabKey}/${subTabKey})。`); // 新增日誌
  }

  // START: 修改 - 在 renderSubTabContent 內部呼叫 fetch 並渲染下拉選單
  // 這裡假設後端 API 路徑是 /api/ui_config/options/<tab>/<subTab>
  //console.log(`準備呼叫 fetchAndRenderDropdowns 函數 (${mainTabKey}/${subTabKey}).`); // 新增日誌
  fetchAndRenderDropdowns(mainTabKey, subTabKey);
  // END: 修改
}

/**
 * 自動儲存目前 main-content 的資料，傳回後端更新
 */
function autoSaveData() {
  console.log('執行 autoSaveData 函數。');
  const mainContent = document.getElementById('main-content');
  const mainTabKey = mainContent.dataset.mainTabKey;
  const subTabKey = mainContent.dataset.subTabKey;

  if (!mainTabKey || !subTabKey) {
    showMessage('無法儲存：無效的 tab 鍵值', 'error');
    console.error('autoSaveData: 無效的 tab 鍵值。');
    return;
  }

  let newData;
  try {
    newData = JSON.parse(mainContent.textContent);
  } catch (err) {
    showMessage('JSON 格式錯誤，無法儲存', 'error');
    console.error('autoSaveData: JSON 格式錯誤。', err);
    return;
  }

  // ← 【修改點】從 globalParsedData 補回 ! 開頭的 key
  if (globalParsedData && globalParsedData[mainTabKey] && globalParsedData[mainTabKey][subTabKey]) {
    const originalData = globalParsedData[mainTabKey][subTabKey];
    for (const key in originalData) {
      if (key.startsWith('!')) {
        newData[key] = originalData[key];
      }
    }
  }

  showMessage(`正在儲存 ${mainTabKey} / ${subTabKey} ...`);

  fetch(`/api/character/update/${encodeURIComponent(mainTabKey)}/${encodeURIComponent(subTabKey)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      file_id: fileId,
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
    showMessage(result.message || '更新成功！');
    console.log('autoSaveData: 更新成功。', result);
	
	// ✅ 如果後端有給新的 profile ID，先更新到 newData 上
    if (result.new_profile_id) {
      newData["!id"] = result.new_profile_id;
    } else if (result.new_scenario_id) {
      newData["!id"] = result.new_scenario_id;
	}
    
	if (globalParsedData && globalParsedData[mainTabKey]) {
      globalParsedData[mainTabKey][subTabKey] = newData;
    }
	
	notifyParent();
	
    if (result.need_update_profile_dropdown) {
	  fetchAndRenderDropdowns("story", "profile");
    } else if (result.need_update_scenario_dropdown) {
      fetchAndRenderDropdowns("story", "scenario");
	}
  })
  .catch(error => {
    showMessage('儲存失敗：' + error.message, 'error');
    console.error('autoSaveData: 儲存失敗。', error);
  });
}

// 定義後端傳送函數 (fetch 範例)
function updateRemark(remark) {
  console.log("update remark: " + remark);
  fetch(`/api/character/${encodeURIComponent(fileId)}/remark`, {
    method: 'PATCH',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ remark: remark })
  })
  .then(response => response.json())
  .then(data => {
    console.log('更新成功:', data);
	showMessage(`更新成功。`);
	notifyParent();
  })
  .catch(err => {
    console.error('更新失敗:', err);
    showMessage(`更新失敗。`, 'error');
  });
}

/**
 * 更新狀態並通知後端
 */
function updateStatus(status) {
  showMessage(`正在更新狀態為 ${status}...`);
  
  fetch(`/api/character/${encodeURIComponent(fileId)}/status`, {
    method: 'PATCH',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ status: status })
  })
  .then(response => response.json())
  .then(data => {
    console.log('狀態更新成功:', data);
    showMessage(`狀態已更新為：${status}`);
    
    // 通知父頁面 (Gallery) 重新讀取，這樣 Emoji 才會變
	notifyParent();
  })
  .catch(err => {
    console.error('狀態更新失敗:', err);
    showMessage(`狀態更新失敗。`, 'error');
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

  fetch(`/api/character/reload?file_id=${encodeURIComponent(fileId)}`)
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

  fetch('/api/character/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      file_id: fileId
    })
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
    document.getElementById('saveButton').disabled = true;
  })
  .catch(error => {
    showMessage('儲存失敗：' + error.message, 'error');
    //hexDisplay.textContent = '儲存失敗：' + error.message;
    console.error('saveFile: 儲存失敗。', error); // 新增日誌
  });
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
    // 如果 opt.value 已經是簡單值 (string, number)，則不需要 JSON.stringify
    // 這裡假設 opt.value 可能會是物件，所以保留 JSON.stringify
    option.value = JSON.stringify(opt.value);
    option.textContent = opt.label;

    // *** 新增的 disabled 邏輯 ***
    // 檢查 opt 物件中是否有 disabled 屬性且其值為 true
    if (opt.disabled === true) {
        option.disabled = true;
    }

    // 比較 defaultValue 和 opt.value，如果相同則選中
    // 處理 defaultValue 可能是物件或簡單值的情況
    if (typeof defaultValue === 'object' && defaultValue !== null) {
        if (JSON.stringify(opt.value) === JSON.stringify(defaultValue)) {
            option.selected = true;
        }
    } else {
        // 當 opt.value 是物件時，即使 defaultValue 是簡單值，也需要比較其序列化後的結果
        // 假設 defaultValue 也是簡單值，或者 opt.value 會被正確轉換
        if (JSON.stringify(opt.value) === JSON.stringify(defaultValue)) {
             option.selected = true;
        }
    }
    select.appendChild(option);
  });

  select.addEventListener('change', e => {
    const selectEl = e.target;
    const selectedIndex = selectEl.selectedIndex;
    const selectedOption = selectEl.options[selectedIndex];

    const selectedValueStr = selectedOption.value;
    let selectedValue;
    try {
      selectedValue = selectedValueStr === '' ? null : JSON.parse(selectedValueStr);
    } catch {
      selectedValue = selectedValueStr;
    }

    const selectedLabel = selectedOption.text; // option 顯示的文字就是 label

    // 傳物件給 callback，包含 value 和 label
    onChangeCallback({
      value: selectedValue,
      label: selectedLabel
    });

    console.log(`Select 元素 ${id} 值改變，value=${selectedValue}, label=${selectedLabel}`);
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
  // 判斷是否為 profile 或 scenario 路由
  let apiUrl = `/api/ui_config/options/${mainTab}/${subTab}`;
  const isProfileDropdown = (mainTab === 'story' && subTab === 'profile');
  const isScenarioDropdown = (mainTab === 'story' && subTab === 'scenario');
  const isBackstageDropdown = (mainTab === 'story' && subTab === 'backstage');

  if (isProfileDropdown) {
    apiUrl = `/api/ui_config/profiles`;
  } else if (isScenarioDropdown) {	  
    apiUrl = `/api/ui_config/scenarios`;
  } else if (isBackstageDropdown) {
    apiUrl = `/api/ui_config/backstage_options`;
  }
  
  //console.log(`執行 fetchAndRenderDropdowns 函數，請求: ${apiUrl}`);
  
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

  showMessage(`正在載入 ${mainTab}/${subTab} 的下拉選單選項...`);
  
  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`HTTP 錯誤: ${response.status}`);
    }
    const result = await response.json();
    //console.log(`收到後端回應 ${apiUrl}:`, result); // <-- 關鍵日誌

    let dropdownsToRender = [];

    if (isBackstageDropdown) {
      if (result.defaultScenario && (!globalParsedData[mainTab] || !globalParsedData[mainTab][subTab] || Object.keys(globalParsedData[mainTab][subTab]).length === 0)) {
        if (!globalParsedData[mainTab]) {
          globalParsedData[mainTab] = {};
        }
        // 將後端傳來的 defaultBackstage 模板深層複製到 globalParsedData 對應位置
        globalParsedData[mainTab][subTab] = JSON.parse(JSON.stringify(result.defaultScenario));
        //console.log('Default Backstage 模板已填充到 globalParsedData (因為原數據為空):', globalParsedData[mainTab][subTab]);

        // 立即更新主內容顯示，以便用戶看到初始模板
		updateMainContent(globalParsedData[mainTab][subTab], true);

      } else if (result.defaultBackstage) { // 如果 defaultBackstage 存在但未填充（因為 globalParsedData 不為空）
        //console.log('Default Backstage 模板存在，但未填充到 globalParsedData (因已存在數據)。');
      } else { // 如果 result.defaultScenario 不存在
        showMessage(`後端 API ${apiUrl} 回傳格式不符合預期 (缺少 "defaultBackstage" 鍵)。`, 'warning');
        //console.warn(`fetchAndRenderDropdowns: 後端回應缺少 "defaultBackstage" 鍵。`, result);
      }
	  
      if (result.dropdowns && Array.isArray(result.dropdowns)) {
        dropdownsToRender = result.dropdowns;
        //console.log(`後端回傳 ${dropdownsToRender.length} 個下拉選單配置。`);
      } else {
        if (result.dropdowns === undefined) {
          showMessage(`後端 API /api/ui_config/scenario_options 回傳格式不符合預期 (缺少 "dropdowns" 鍵)。`, 'warning');
          //console.warn(`fetchAndRenderDropdowns: 後端回應缺少 "dropdowns" 鍵。`, result);
        } else if (!Array.isArray(result.dropdowns)) {
          showMessage(`後端 API /api/ui_config/scenario_options 回傳的 "dropdowns" 不是陣列。`, 'warning');
          //console.warn(`fetchAndRenderDropdowns: 後端回應的 "dropdowns" 不是陣列。`, result);
        } else {
          showMessage(`後端 API /api/ui_config/scenario_options 回傳格式未知錯誤。`, 'warning');
          //console.warn(`fetchAndRenderDropdowns: 後端回應格式未知錯誤。`, result);
        }
        
		// 如果沒有 dropdowns，但有 defaultScenario，我們可能仍會繼續
        // 這裡的 return 語句會阻止後續渲染，請根據你的具體需求決定是否保留
        if (!result.defaultScenario) return; // 如果既沒有 defaultScenario 也沒有 dropdowns 才返回
      }
    } else {
      // ... (unchanged code for other cases)
      if (result.dropdowns && Array.isArray(result.dropdowns)) {
        dropdownsToRender = result.dropdowns;
        //console.log(`後端回傳 ${dropdownsToRender.length} 個下拉選單配置。`); // 新增日誌
      } else {
        // START: 調整錯誤訊息
        if (result.dropdowns === undefined) {
          showMessage(`後端 API /api/ui_config/options/${mainTab}/${subTab} 回傳格式不符合預期 (缺少 "dropdowns" 鍵)。`, 'warning');
          //hexDisplay.textContent = `後端 API /api/ui_config/options/${mainTab}/${subTab} 回傳格式不符合預期 (缺少 "dropdowns" 鍵)。`;
          //console.warn(`fetchAndRenderDropdowns: 後端回應缺少 "dropdowns" 鍵。`, result); // 新增日誌
        } else if (!Array.isArray(result.dropdowns)) {
          showMessage(`後端 API /api/ui_config/options/${mainTab}/${subTab} 回傳的 "dropdowns" 不是陣列。`, 'warning');
          //hexDisplay.textContent = `後端 API /api/ui_config/options/${mainTab}/${subTab} 回傳的 "dropdowns" 不是陣列。`;
          //console.warn(`fetchAndRenderDropdowns: 後端回應的 "dropdowns" 不是陣列。`, result); // 新增日誌
        } else {
          showMessage(`後端 API /api/ui_config/options/${mainTab}/${subTab} 回傳格式未知錯誤。`, 'warning');
          //hexDisplay.textContent = `後端 API /api/ui_config/options/${mainTab}/${subTab} 回傳格式未知錯誤。`;
          //console.warn(`fetchAndRenderDropdowns: 後端回應格式未知錯誤。`, result); // 新增日誌
        }
        // END: 調整錯誤訊息
        return;
      }
    }

    // 如果 dropdownsToRender 陣列為空
    if (!dropdownsToRender || dropdownsToRender.length === 0) {
      showMessage(`無 ${mainTab}/${subTab} 的下拉選單選項。`, 'error');
      //console.log(`fetchAndRenderDropdowns: 後端回傳的下拉選單配置為空。`); // 新增日誌
      return;
    }

    // 顯示整個下拉選單容器
    dropdownContainer.classList.add('show');
    //console.log('下拉選單容器已顯示。'); // 新增日誌

    let slotIndex = 0;
    for (const dropdownConfig of dropdownsToRender) {
      if (slotIndex >= dropdownSlotIds.length) {
          //console.warn(`fetchAndRenderDropdowns: 超過三個下拉選單插槽限制，跳過剩餘配置。`); // 新增日誌
          break; // 超過三個插槽則停止
      }

      const slotId = dropdownSlotIds[slotIndex];
      const slot = document.getElementById(slotId);

      if (!slot) {
	    //console.error(`fetchAndRenderDropdowns: 未找到 ID 為 ${slotId} 的下拉選單插槽。`);
        continue;
	  }

      slot.innerHTML = ''; // 清空舊內容
        
      const label = document.createElement('label');
      label.textContent = dropdownConfig.displayLabel; // 後端提供顯示名稱

      // 從 globalParsedData 中獲取當前選中的值
      // 假設 `dropdownConfig.dataKey` 對應到 `globalParsedData[mainTab][subTab][dataKey]`
      let currentDataForDropdown = null;
      if (globalParsedData && globalParsedData[mainTab] && globalParsedData[mainTab][subTab]) {
          currentDataForDropdown = globalParsedData[mainTab][subTab][dropdownConfig.dataKey];
          //console.log(`fetchAndRenderDropdowns: 取得當前資料 for ${dropdownConfig.dataKey}:`, currentDataForDropdown); // 新增日誌
      } else {
          //console.log(`fetchAndRenderDropdowns: globalParsedData 中無對應 ${mainTab}/${subTab}/${dropdownConfig.dataKey} 的資料。`); // 新增日誌
      }

      const select = createSelect(
        `${slotId}-${dropdownConfig.dataKey}`, // 每個 select 都有唯一 ID
        dropdownConfig.options,
        currentDataForDropdown || dropdownConfig.defaultValue, // 優先使用當前資料，否則使用後端提供的預設值
        selected => {
          // 給 profile / scenario 使用的...
          const isMainIdSwitch = (dropdownConfig.dataKey === "!id");
		  
          if (isProfileDropdown && isMainIdSwitch) {
            if (selected.value === "") return; // 使用者還沒有選到真實的東西.
            // profile 路由：呼叫後端拉詳細資料更新整個 JSON
            fetch(`/api/profile/detail/${selected.value}`)
            .then(res => {
              if (!res.ok) throw new Error(`HTTP 錯誤: ${res.status}`);
                return res.json();
            })
            .then(profileData => {
              if (globalParsedData && globalParsedData[mainTab]) {
                globalParsedData[mainTab][subTab] = profileData;
				updateMainContent(profileData, true);	
                console.log('Profile 詳細資料已更新到 globalParsedData:', profileData);
              }
            })
            .catch(err => {
              showMessage(`載入 Profile 詳細資料失敗：${err.message}`, 'error');
              console.error('載入 Profile 詳細資料失敗', err);
            });
		  } else if (isScenarioDropdown && isMainIdSwitch) {
            if (selected.value === "") return; // 使用者還沒有選到真實的東西.
            // scenario 路由：呼叫後端拉詳細資料更新整個 JSON
            fetch(`/api/scenario/detail/${selected.value}`)
            .then(res => {
              if (!res.ok) throw new Error(`HTTP 錯誤: ${res.status}`);
                return res.json();
            })
            .then(scenarioData => {
              if (globalParsedData && globalParsedData[mainTab]) {
                globalParsedData[mainTab][subTab] = scenarioData;
                updateMainContent(scenarioData, true);	
                console.log('Scenario 詳細資料已更新到 globalParsedData:', scenarioData);
              }
            })
            .catch(err => {
              showMessage(`載入 Scenario 詳細資料失敗：${err.message}`, 'error');
              console.error('載入 Scenario 詳細資料失敗', err);
            });
		  } else {
            // 更新 globalParsedData 中對應的值
            if (globalParsedData && globalParsedData[mainTab] && globalParsedData[mainTab][subTab]) {
                globalParsedData[mainTab][subTab][dropdownConfig.dataKey] = selected.value;
				globalParsedData[mainTab][subTab][dropdownConfig.labelKey] = selected.label;
				
                // 同步更新 main-content 顯示的 JSON
				updateMainContent(globalParsedData[mainTab][subTab], true);
                console.log(`下拉選單值已更新到 globalParsedData: ${mainTab}/${subTab}/${dropdownConfig.dataKey} =`, selected); // 新增日誌
            } else {
                console.warn('無法更新 globalParsedData，因為路徑不存在。'); // 新增日誌
            }
		  }
		}
      );

      slot.appendChild(label);
      slot.appendChild(select);
      slot.style.display = 'flex'; // 顯示此插槽
      console.log(`已渲染下拉選單到 ${slotId}，標籤: ${dropdownConfig.displayLabel}`); // 新增日誌
      slotIndex++;
    }
	
    showMessage(`已載入 ${slotIndex} 個下拉選單。`);
	//hexDisplay.textContent = `已載入 ${slotIndex} 個下拉選單。`;
    //console.log(`fetchAndRenderDropdowns: 總共載入 ${slotIndex} 個下拉選單。`); // 新增日誌

  } catch (error) {
    showMessage(`載入下拉選單失敗：${error.message}`, 'error');
	//hexDisplay.textContent = `載入下拉選單失敗：${error.message}`;
    //console.error('載入下拉選單錯誤:', error); // 新增日誌
  } finally {
    // 無論成功或失敗，都嘗試定位下拉選單
    //console.log('嘗試定位下拉選單。'); // 新增日誌
    positionDropdown();
  }
}
// END: 修改

function positionDropdown() {
  const dropdown = document.getElementById('dropdown-container');
  const mainContentShell = document.getElementById('main-content-shell');
  const mainContent = document.getElementById('main-content');
  const tabContainer = document.querySelector('.tab-container');

  if (!dropdown || !mainContentShell || !mainContent || !tabContainer) return;

  const shellRect = mainContentShell.getBoundingClientRect();
  const containerRect = tabContainer.getBoundingClientRect();
  const dropdownRect = dropdown.getBoundingClientRect();

  const margin = 10; // 邊距

  // 計算浮動選單位置（相對 tab-container）
  const top = shellRect.top - containerRect.top + margin;
  const right = containerRect.right - shellRect.right + margin;

  dropdown.style.position = 'absolute';
  dropdown.style.top = `${top}px`;
  dropdown.style.right = `${right}px`;

  // 計算 main-content max-width
  const maxWidth = shellRect.width - (dropdownRect.width === 0 ? 0 : dropdownRect.width + margin * 2);

  if (maxWidth > 0) {
    mainContent.style.maxWidth = `${maxWidth}px`;
  } else {
    mainContent.style.maxWidth = '50px'; // 防止太小
  }
}

function showMessage(text, type = 'success') {
  const el = document.getElementById('result-message');
  el.textContent = text;
  el.className = '';
  el.classList.add(type);
}

const bc = new BroadcastChannel('edit_file_sync_bus');

function notifyParent() {
  // --- 新增 postMessage 通知父頁 ---
  //if (window.opener && !window.opener.closed && fileId) {
  //  window.opener.postMessage(
  //    { action: "updated", file_id: fileId },
  //    window.location.origin
  //  );
  //}

  // 大吼大叫...
  //new BroadcastChannel('edit_file_sync_bus').postMessage('reload_all');
  
  // 用 channel 通知檔案更新
  if (fileId) {
    bc.postMessage({ action: "updated", file_id: fileId });
  }
}

window.reloadFile = reloadFile;
window.saveFile = saveFile;

window.addEventListener('load', positionDropdown);
window.addEventListener('resize', positionDropdown);