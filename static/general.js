function setupApp() {
  const initData = window.INIT_DATA || {};

  return {
    color_traits: [],
    tag_type_settings_array: [],
    tag_array: [],
    profile_group_array: [],
    mistor_array: [],
    omnion_array: [],

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

      // --- 2. 初始化 mistor ---
      this.mistor_array = initData.mistor?.length > 0
        ? initData.mistor
        : [{ key: '', mist: '' }];

      // --- 3. 初始化 omnion (並自動排序) ---
      const typeWeight = { 'person': 1, 'object': 2, 'special': 3 };
      this.omnion_array = initData.omnion?.length > 0
        ? [...initData.omnion].sort((a, b) => (typeWeight[a.type] || 99) - (typeWeight[b.type] || 99))
        : [{ type: '', key: '', desc: '' }];

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

    // --- 迷幻之霧操作 ---
    addMistor() {
      this.mistor_array.push({ key: '', mist: '' });
    },
    removeMistor(index) {
      this.mistor_array.splice(index, 1);
    },
    // 檢查脫敏關鍵字是否重複
    checkMistorDuplicate(index) {
      const currentKey = this.mistor_array[index].key.trim();
      if (!currentKey) return;

      // 尋找是否有其他行使用了相同的 keyword
      const isDuplicate = this.mistor_array.some((item, idx) => idx !== index && item.key.trim() === currentKey);
      
      if (isDuplicate) {
        this.showMessage(`迷幻之霧關鍵字「${currentKey}」已存在，請勿重複輸入！`, 'error');
        this.mistor_array[index].key = ''; // 清空輸入
      }
    },

    // --- 萬有之書操作 ---
    addOmnion() {
      this.omnion_array.push({ type: '', key: '', desc: '' });
      this.sortOmnion();
    },
    removeOmnion(index) {
      this.omnion_array.splice(index, 1);
    },
    sortOmnion() {
      const typeWeight = { 'person': 1, 'object': 2, 'special': 3 };
      this.omnion_array.sort((a, b) => {
        const weightA = typeWeight[a.category] || 99;
        const weightB = typeWeight[b.category] || 99;
        return weightA - weightB;
      });
    },
    // 檢查大辭典關鍵字是否重複
    checkOmnionDuplicate(index) {
      const currentKey = this.omnion_array[index].key.trim();
      if (!currentKey) return;

      // 尋找是否有其他行使用了相同的 keyword
      const isDuplicate = this.omnion_array.some((item, idx) => idx !== index && item.key.trim() === currentKey);
      
      if (isDuplicate) {
        this.showMessage(`萬有之書關鍵字「${currentKey}」已存在，請勿重複輸入！`, 'error');
        this.omnion_array[index].key = ''; // 清空輸入
      }
    },

    // --- 驗證與提交 ---
    isSubmitDisabled() {
      const colorTraitsInvalid = this.color_traits.some(item => !item.trait.zh.trim() || !item.name.zh.trim());
      const tagTypeSettingsInvalid = this.tag_type_settings_array.some(item => !item.key.trim() || !item.name.zh.trim() || !item.order);
      const tagsInvalid = this.tag_array.some(item => !item.type.trim() || !item.name.zh.trim());
      const profileGroupInvalid = this.profile_group_array.some(item => !item.name.zh.trim() || !item.order);
      
      // 新增：Tab 5 & Tab 6 的驗證
      const mistorInvalid = this.mistor_array.some(item => !item.key.trim() || !item.mist.trim());
      const omnionInvalid = this.omnion_array.some(item => !item.type.trim() || !item.key.trim());
      
      return colorTraitsInvalid || tagTypeSettingsInvalid || tagsInvalid || profileGroupInvalid || mistorInvalid || omnionInvalid;
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
      this.sortOmnion();

      // 最終送出前的防重把關
      const mistorKeys = this.mistor_array.map(i => i.key.trim()).filter(Boolean);
      const hasMistorDup = new Set(mistorKeys).size !== mistorKeys.length;

      const omnionKeys = this.omnion_array.map(i => i.key.trim()).filter(Boolean);
      const hasOmnionDup = new Set(omnionKeys).size !== omnionKeys.length;

      if (hasMistorDup || hasOmnionDup) {
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
        mistor: this.mistor_array.filter(i => i.key.trim()),
        omnion: this.omnion_array.filter(i => i.key.trim())
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