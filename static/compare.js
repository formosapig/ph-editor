window.addEventListener('DOMContentLoaded', () => {
  // 1. 直接從全域變數中取得資料
  const { characters, attributes, attrNameMap, attrBlockMap } = window.rawCompareData;

  // 2. 定義 Petite-Vue 應用程式的資料和方法
  const compareData = {
    characters,
    attributes,
    attrNameMap,
    attrBlockMap,
	
	// 新增一個計算屬性或直接過濾
    get displayAttributes() {
      return this.attributes.filter(attr => attr !== 'file_id');
    },
	// **新增的函式：用於開啟編輯視窗**
    openEditWindow(fileId) {
        const windowName = `edit_file_${fileId}`;
        // 使用 window.open 開啟新視窗，並傳遞 file_id
        window.open(`/edit?file_id=${encodeURIComponent(fileId)}`, windowName);
    },
	// **新增：獲取屬性區塊 class 的函式**
    getAttributeBlockClass(attr) {
      const blockType = this.attrBlockMap[attr];
      if (blockType) {
        return `${blockType}-data-cell`; // 返回對應的 class 名稱
      }
      return ''; // 如果沒有定義，返回空字串
    },
	// 檢查色塊,只接受 #RRGGBBAA
	isCssColor(value) {
	  return false;
      if (typeof value !== 'string' || value.trim() === '') {
        return false; // 不是字串或空字串，直接返回 false
      }
        
      const trimmedValue = value.trim();

      // **僅檢查 #RRGGBBAA 格式的正規表達式**
      // ^# : 匹配字串開頭的 '#'
      // [0-9A-Fa-f]{8} : 匹配 8 個十六進位字元 (0-9, A-F, a-f)
      // $ : 匹配字串的結尾
      if (/^#[0-9A-Fa-f]{8}$/.test(trimmedValue)) {
        return true;
      }

      return false; // 不符合 #RRGGBBAA 格式
	},
	// 縮檔名
	truncateFileId(fileId) {
      const maxLength = 166; // 設定你希望顯示的最大長度
      if (!fileId || typeof fileId !== 'string') {
        return '-'; // 如果 fileId 無效或不是字串，顯示 '-'
      }
      if (fileId.length > maxLength) {
        return fileId.substring(0, maxLength) + '...'; // 截斷並加上省略號
      }
      return fileId; // 不足長度則完整顯示
    },
	isDifferentFromFirst(index, attr) {
      if (!this.characters.length || index === 0) return false;
	  if (this.attrBlockMap[attr] === 'basic') return false;
      const firstValue = this.characters[0][attr];
      const currentValue = this.characters[index][attr];
      return firstValue !== currentValue;
    },
    parseColorString(str) {
      console.log("input = " + str);
	  
  // 1. 處理無效輸入：null 或 undefined
  // 這些情況無法顯示，用 '-' 表示
  if (str === null || str === undefined) {
    return [{ type: 'text', value: '-' }];
  }

  // 2. 處理數字：將數字直接轉為字串顯示
  if (typeof str === 'number') {
    return [{ type: 'text', value: String(str) }];
  }

  // 3. 處理空字串：單獨回傳空字串的文字物件
  if (str === '') {
    return [{ type: 'text', value: '' }];
  }
  
  // 到這裡，str 一定是有效的非空字串

  // 4. 檢查整個字串是否為單一顏色碼
  const singleColorRegex = /^#[0-9A-Fa-f]{6,8}$/i;
  if (singleColorRegex.test(str)) {
    return [{ type: 'color', value: str }];
  }

  // 5. 處理包含多個顏色碼或文字的複雜字串
  const result = [];
  const regex = /(#[0-9A-Fa-f]{6,8})/gi;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(str)) !== null) {
    if (match.index > lastIndex) {
      result.push({ type: 'text', value: str.slice(lastIndex, match.index) });
    }
    result.push({ type: 'color', value: match[1] });
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < str.length) {
    result.push({ type: 'text', value: str.slice(lastIndex) });
  }
  
  // 6. 如果最終結果陣列是空的，表示沒有顏色碼，整個字串都是文字
  if (result.length === 0) {
    return [{ type: 'text', value: str }];
  }

  return result;
},
  generateColorHtml(attrValue) {
    if (!attrValue) return ''; // 處理空值

    let html = '';
    const parts = this.parseColorString(attrValue);

    for (const part of parts) {
        if (part.type === 'color') {
            // 注意：這裡使用 ES6 模板字串來建立 HTML
            html += `<span class="color-box" style="background-color: ${part.value}"></span>`;
        } else {
            // 記得要對文字進行 HTML 轉義，以防 XSS 攻擊
            const sanitizedValue = part.value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            html += `<span>${sanitizedValue}</span>`;
        }
    }
    return html;
},
    // --- 修改開始：新增 checkbox 與 reload 功能 ---
    visibleBlocks: ["hair", "face", "body", "clothing", "accessory"],

    reloadData() {
      this.characters = [...window.rawCompareData.characters];
      this.attributes = [...window.rawCompareData.attributes];
      this.visibleBlocks = ["hair", "face", "body", "clothing", "accessory"]; // reload 後預設全開
    }
    // --- 修改結束 ---


  };

  PetiteVue.createApp(compareData).mount('[v-scope]');
});