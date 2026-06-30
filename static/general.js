function setupApp() {
  const initData = window.INIT_DATA || {};

  return {
    color_traits: [],
    tag_type_settings_array: [],
    tag_array: [],
    profile_group_array: [],
    keyword_masking: [],
    dictionary_terms: [],

    init() {
      // 初始化 color_traits
      this.color_traits = initData.colorTraits?.length > 0 
        ? initData.colorTraits 
        : [{ code: '#000000', name: { en: '', zh: '' }, trait: { zh: '' } }];

      // 初始化 tag_type_settings_array
      this.tag_type_settings_array = Object.keys(initData.tagStyles || {}).length > 0
        ? Object.entries(initData.tagStyles)
            .map(([key, value]) => ({ key, ...value }))
            .sort((a, b) => a.order - b.order)
        : [{ key: '', name: { zh: '' }, order: 1, color: '#000000', background: '#FFFFFF' }];
    console.log(this.tag_type_settings_array)

      // 初始化 tag_array
      this.tag_array = initData.tagList?.length > 0 
        ? initData.tagList 
        : [{ id: Date.now(), type: '', name: { zh: '' }, desc: { zh: '' }, snapshot: { zh: '' }, appearance: { zh: '' }, clothing: { zh: '' } }];

      // 初始化 profile_group_array
      this.profile_group_array = initData.profileGroup?.length > 0 
        ? [...initData.profileGroup].sort((a, b) => a.order - b.order)
        : [{ id: 1, name: { zh: '' }, desc: { zh: '' }, order: 1, color: '#000000', background: '#FFFFFF' }];

      // --- 2. 初始化 keyword_masking ---
      this.keyword_masking = initData.keywordMasking?.length > 0
        ? initData.keywordMasking
        : [{ keyword: '', masked: '' }];

      // --- 3. 初始化 dictionary_terms (並自動排序) ---
      const categoryWeight = { 'person': 1, 'object': 2, 'special': 3 };
      this.dictionary_terms = initData.dictionaryTerms?.length > 0
        ? [...initData.dictionaryTerms].sort((a, b) => (categoryWeight[a.category] || 99) - (categoryWeight[b.category] || 99))
        : [{ category: '', keyword: '', description: '' }];

    },

    // 取得標籤樣式 (對應原有的 getter)
    getTagStyle(typeKey) {
      const found = this.tag_type_settings_array.find(t => t.key === typeKey);
      if (found) {
        return { color: found.color, backgroundColor: found.background };
      }
      return {};
    },

    // --- 各類別操作方法 ---
    addColorTrait() {
      this.color_traits.push({ code: '#000000', name: { en: '', zh: '' }, trait: { zh: '' } });
    },
    removeColorTrait(index) {
      this.color_traits.splice(index, 1);
    },

    addTagTypeSetting() {
      const maxOrder = this.tag_type_settings_array.reduce((max, item) => Math.max(max, item.order || 0), 0);
      this.tag_type_settings_array.push({ key: '', name: { zh: '' }, order: maxOrder + 1, color: '#000000', background: '#FFFFFF' });
    },
    removeTagTypeSetting(index) {
      this.tag_type_settings_array.splice(index, 1);
    },

    addTag() {
      const maxId = this.tag_array.reduce((max, item) => Math.max(max, item.id || 0), 0);
      this.tag_array.push({ id: maxId + 1, type: '', name: { zh: '' }, desc: { zh: '' }, snapshot: { zh: '' }, appearance: { zh: '' }, clothing: { zh: '' } });
    },
    removeTag(index) {
      this.tag_array.splice(index, 1);
    },

    addProfileGroup() {
      const maxId = this.profile_group_array.reduce((max, item) => Math.max(max, item.id || 0), 0);
      const maxOrder = this.profile_group_array.reduce((max, item) => Math.max(max, item.order || 0), 0);
      this.profile_group_array.push({ id: maxId + 1, name: { zh: '' }, desc: { zh: '' }, order: maxOrder + 1, color: '#000000', background: '#FFFFFF' });
    },
    removeProfileGroup(index) {
      this.profile_group_array.splice(index, 1);
    },

    // --- 關鍵字脫敏操作 ---
    addKeywordMasking() {
      this.keyword_masking.push({ keyword: '', masked: '' });
    },
    removeKeywordMasking(index) {
      this.keyword_masking.splice(index, 1);
    },
    // 檢查脫敏關鍵字是否重複
    checkMaskingDuplicate(index) {
      const currentKeyword = this.keyword_masking[index].keyword.trim();
      if (!currentKeyword) return;

      // 尋找是否有其他行使用了相同的 keyword
      const isDuplicate = this.keyword_masking.some((item, idx) => idx !== index && item.keyword.trim() === currentKeyword);
      
      if (isDuplicate) {
        this.showMessage(`關鍵字「${currentKeyword}」已存在，請勿重複輸入！`, 'error');
        this.keyword_masking[index].keyword = ''; // 清空輸入
      }
    },

    // --- 大辭典操作 ---
    addDictionaryTerm() {
      this.dictionary_terms.push({ category: '', keyword: '', description: '' });
      this.sortDictionaryTerms();
    },
    removeDictionaryTerm(index) {
      this.dictionary_terms.splice(index, 1);
    },
    sortDictionaryTerms() {
      const categoryWeight = { 'person': 1, 'object': 2, 'special': 3 };
      this.dictionary_terms.sort((a, b) => {
        const weightA = categoryWeight[a.category] || 99;
        const weightB = categoryWeight[b.category] || 99;
        return weightA - weightB;
      });
    },
    // 檢查大辭典關鍵字是否重複
    checkDictionaryDuplicate(index) {
      const currentKeyword = this.dictionary_terms[index].keyword.trim();
      if (!currentKeyword) return;

      // 尋找是否有其他行使用了相同的 keyword
      const isDuplicate = this.dictionary_terms.some((item, idx) => idx !== index && item.keyword.trim() === currentKeyword);
      
      if (isDuplicate) {
        this.showMessage(`大辭典關鍵字「${currentKeyword}」已存在，請勿重複輸入！`, 'error');
        this.dictionary_terms[index].keyword = ''; // 清空輸入
      }
    },

    // --- 驗證與提交 ---
    isSubmitDisabled() {
      const colorTraitsInvalid = this.color_traits.some(item => !item.trait.zh.trim() || !item.name.zh.trim());
      const tagTypeSettingsInvalid = this.tag_type_settings_array.some(item => !item.key.trim() || !item.name.zh.trim() || !item.order);
      const tagsInvalid = this.tag_array.some(item => !item.type.trim() || !item.name.zh.trim());
      const profileGroupInvalid = this.profile_group_array.some(item => !item.name.zh.trim() || !item.order);
      
      // 新增：Tab 5 & Tab 6 的驗證
      const keywordMaskingInvalid = this.keyword_masking.some(item => !item.keyword.trim() || !item.masked.trim());
      const dictionaryTermsInvalid = this.dictionary_terms.some(item => !item.category.trim() || !item.keyword.trim());
      
      return colorTraitsInvalid || tagTypeSettingsInvalid || tagsInvalid || profileGroupInvalid || keywordMaskingInvalid || dictionaryTermsInvalid;

      //return colorTraitsInvalid || tagTypeSettingsInvalid || tagsInvalid || profileGroupInvalid;
    },

    async submit() {
      // 1. 建立 Type 排序對照表 (保持不變)
      const typeOrderMap = {};
      const filteredTagStyles = {};

      this.tag_type_settings_array.forEach(item => {
        if (item.key.trim()) {
          const key = item.key.trim();
          typeOrderMap[key] = item.order || 999;
          filteredTagStyles[key] = {
            name: { zh: item.name.zh },
            order: item.order,
            color: item.color,
            background: item.background
          };
        }
      });

      // 2. 執行排序並更新畫面 (保持不變)
      this.tag_array = this.tag_array
        .filter(i => i.name.zh.trim() !== '')
        .sort((a, b) => {
          const orderA = typeOrderMap[a.type] ?? 999;
          const orderB = typeOrderMap[b.type] ?? 999;
          if (orderA !== orderB) return orderA - orderB;
          return a.id - b.id;
        });

      // 新增：送出前確保大辭典再次過濾並精準排序
      this.sortDictionaryTerms();

      // 最終送出前的防重把關
      const maskingKeywords = this.keyword_masking.map(i => i.keyword.trim()).filter(Boolean);
      const hasMaskingDup = new Set(maskingKeywords).size !== maskingKeywords.length;

      const dictKeywords = this.dictionary_terms.map(i => i.keyword.trim()).filter(Boolean);
      const hasDictDup = new Set(dictKeywords).size !== dictKeywords.length;

      if (hasMaskingDup || hasDictDup) {
        this.showMessage('資料中存有重複的關鍵字，請檢查後再送出！', 'error');
        return; // 攔截不送出
      }
      
      // 3. 準備送出的資料 (打包 tab5, tab6)
      const dataToSend = {
        color_traits: this.color_traits.filter(i => i.trait.zh.trim()),
        tag_styles: filteredTagStyles,
        tag_list: this.tag_array, 
        profile_group: this.profile_group_array.filter(i => i.name.zh.trim()),
        // 新增打包欄位
        keyword_masking: this.keyword_masking.filter(i => i.keyword.trim()),
        dictionary_terms: this.dictionary_terms.filter(i => i.keyword.trim())
      };

      try {
        const res = await fetch('/general/update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(dataToSend),
        });

        if (!res.ok) {
          const errData = await res.json();
          throw new Error(errData.message || '伺服器錯誤');
        }

        this.showMessage('資料儲存並排序成功！', 'info');
      } catch (err) {
        this.showMessage(`送出失敗：${err.message}`, 'error');
      }
    },

/*    async submit() {
  // 1. 建立 Type 排序對照表 (從 tag_type_settings_array 取得 order)
  const typeOrderMap = {};
  const filteredTagStyles = {};

  this.tag_type_settings_array.forEach(item => {
    if (item.key.trim()) {
      const key = item.key.trim();
      typeOrderMap[key] = item.order || 999;
      filteredTagStyles[key] = {
        name: { zh: item.name.zh },
        order: item.order,
        color: item.color,
        background: item.background
      };
    }
  });

  // 2. 執行排序並更新畫面 (this.tag_array)
  // 先過濾掉沒有名稱的無效行，再進行排序
  this.tag_array = this.tag_array
    .filter(i => i.name.zh.trim() !== '')
    .sort((a, b) => {
      // 條件 1: 依照 type 的 order 排序
      const orderA = typeOrderMap[a.type] ?? 999;
      const orderB = typeOrderMap[b.type] ?? 999;

      if (orderA !== orderB) {
        return orderA - orderB;
      }

      // 條件 2: type 相同時，依照 id 排序 (由小到大)
      return a.id - b.id;
    });

  // 3. 準備送出的資料 (此時 this.tag_array 已經是排序過的狀態)
  const dataToSend = {
    color_traits: this.color_traits.filter(i => i.trait.zh.trim()),
    tag_styles: filteredTagStyles,
    tag_list: this.tag_array, 
    profile_group: this.profile_group_array.filter(i => i.name.zh.trim())
  };

  try {
    const res = await fetch('/general/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dataToSend),
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.message || '伺服器錯誤');
    }

    this.showMessage('資料儲存並排序成功！', 'info');
  } catch (err) {
    this.showMessage(`送出失敗：${err.message}`, 'error');
  }
},*/

    // 訊息框與同步邏輯 (保持原樣但整合進 Alpine)
    showMessage(message, type = 'info') {
      const messageBox = document.createElement('div');
      messageBox.style.cssText = `position: fixed; top: 20px; left: 50%; transform: translateX(-50%); padding: 15px 25px; border-radius: 8px; font-size: 16px; font-weight: bold; z-index: 1000; box-shadow: 0 4px 12px rgba(0,0,0,0.15); opacity: 0; transition: all 0.3s ease-in-out;`;
      
      const colors = { success: '#4CAF50', error: '#F44336', info: '#2196F3' };
      messageBox.style.backgroundColor = colors[type] || colors.info;
      messageBox.style.color = 'white';
      messageBox.textContent = message;
      
      document.body.appendChild(messageBox);
      setTimeout(() => { messageBox.style.opacity = '1'; }, 10);
      setTimeout(() => {
        messageBox.style.opacity = '0';
        messageBox.addEventListener('transitionend', () => messageBox.remove());
      }, 3000);
    }

  };
}