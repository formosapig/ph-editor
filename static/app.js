window.addEventListener('DOMContentLoaded', () => {

  const app = PetiteVue.reactive({
    // State
    currentScanPath: '',
    allImages: [],
    displayedImages: [],
    selectedSet: [],
    sortAscending: true,
    sortKey: 'filename',
    showSortMenu: false,
    filterKey: 'id',
    filterKeyword: '',
    showFilterMenu: false,
    // 新增：最基礎狀態 (預設全選)
    activeStatuses: ['draft', 'refinement', 'finalized'],
    globalTagStyles: {},
    
    // Computed
    get scanPathDisplay() {
      return this.currentScanPath ? this.shortenPath(this.currentScanPath) : '尚未選擇';
    },
    get selectedCount() {
      return this.selectedSet.length;
    },
    get totalFilesCount() {
      return this.displayedImages.length;
    },
    get isAnyMenuOpen() {
      return this.showSortMenu || this.showFilterMenu;
    },
    
    // Methods
    onMounted() {
      this.init(); // 安全執行初始化
    },
    
    async scan(path) {
      if (!path) {
        alert('請輸入路徑');
        return;
      }
      
      this.currentScanPath = path;
      this.selectedSet = [];
      
      try {
        const res = await fetch('/scan', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ path })
        });
        
        if (!res.ok) {
          const err = await res.json();
          alert('掃描錯誤: ' + (err.error || res.statusText));
          return;
        }
        
        const data = await res.json();
        if (!data.images || data.images.length === 0) {
          alert('沒有找到 PNG 檔案');
          this.allImages = [];
          this.displayedImages = [];
          return;
        }
        
        this.globalTagStyles = data.tag_styles || {};
        this.allImages = data.images;
        this.displayedImages = [...data.images];
      this.applyFilter(this.filterKeyword);
      } catch (e) {
        alert('網路或伺服器錯誤');
        console.error(e);
      }
    },
    
    changeFolder() {
      const newPath = prompt('請輸入掃描資料夾絕對路徑：', this.currentScanPath || '');
      if (newPath && newPath.trim() !== '' && newPath.trim() !== this.currentScanPath) {
        this.scan(newPath.trim());
      }
    },
    
    toggleSort() {
      this.showSortMenu = !this.showSortMenu;
      
      if (this.showSortMenu) {
        this.showFilterMenu = false;	  
      }
    },
    
    applySort(key) {
      this.sortKey = key;
      this.stableSortImages();
    },

    toggleSortOrder() {
      this.sortAscending = !this.sortAscending;
      this.stableSortImages();
    },

    stableSortImages() {
      this.displayedImages = this.displayedImages
        .map((img, idx) => ({ ...img, __originalIndex: idx })) // 保留原順序
        .sort((a, b) => {
          const valA = (a[this.sortKey] || '').toString();
          const valB = (b[this.sortKey] || '').toString();
          const cmp = valA.localeCompare(valB, undefined, { sensitivity: 'base' });
          return cmp !== 0
            ? (this.sortAscending ? cmp : -cmp)
            : a.__originalIndex - b.__originalIndex;
        })
        .map(({ __originalIndex, ...img }) => img); // 移除臨時欄位
    },
    
    toggleFilter() {
      this.showFilterMenu = !this.showFilterMenu;
    
      if (this.showFilterMenu) {
          this.showSortMenu = false;
      }
    },
    
    /*applyFilter(key) {
      this.filterKey = key;
      const rawKw = this.filterKeyword.trim().toLowerCase();
      this.selectedSet = [];

      // 如果關鍵字為空，直接顯示所有圖片
      if (!rawKw || !this.filterKey) {
        this.displayedImages = [...this.allImages];
        return;
      }

      // 1. 解析輸入字串，分離出精確關鍵字和模糊關鍵字
      const parts = rawKw.match(/"[^"]*"|\S+/g) || [];
    
      const searchKeywords = parts.map(part => {
        // 判斷是否為精確比對
        const isExact = part.startsWith('"') && part.endsWith('"');
      
        return {
          keyword: isExact ? part.replace(/^"|"$/g, '') : part,
          isExact: isExact
        };
      });

      // 如果處理後的關鍵字陣列為空，直接返回所有圖片
      if (searchKeywords.length === 0) {
        this.displayedImages = [...this.allImages];
        return;
      }

      // 2. 執行篩選邏輯，使用 OR 邏輯比對
      this.displayedImages = this.allImages.filter(item => {
        const val = (item[key] || '').toString().toLowerCase();

        // 使用 .some() 方法來實現 OR 邏輯
        // 只要 val 包含 searchKeywords 陣列中的任一關鍵字，就回傳 true
        return searchKeywords.some(searchObj => {
          if (searchObj.isExact) {
            // 精確比對邏輯
            return val === searchObj.keyword;
          } else {
            // 模糊比對邏輯
            return val.includes(searchObj.keyword);
          }
        });
      });
    },*/
    
    applyFilter(key) {
      this.filterKey = key;
      const rawKw = this.filterKeyword.trim().toLowerCase();
      this.selectedSet = [];

      // --- 核心邏輯修改：先過濾狀態，再過濾關鍵字 ---
      
      // 1. 根據「草稿/潤飾/定稿」勾選狀況過濾 (最基礎過濾)
      let filteredBase = this.allImages.filter(item => {
        // 如果 item.status 未定義，預設視為 'draft'
        const status = item.status || 'draft'; 
        return this.activeStatuses.includes(status);
      });

      // 2. 如果沒有關鍵字，直接返回符合狀態的結果
      if (!rawKw || !this.filterKey) {
        this.displayedImages = filteredBase;
        return;
      }

      // 3. 解析搜尋關鍵字 (維持你原有的 OR 邏輯)
      const parts = rawKw.match(/"[^"]*"|\S+/g) || [];
      const searchKeywords = parts.map(part => {
        const isExact = part.startsWith('"') && part.endsWith('"');
        return {
          keyword: isExact ? part.replace(/^"|"$/g, '') : part,
          isExact: isExact
        };
      });

      // 4. 在符合狀態的基礎上，執行關鍵字篩選
      this.displayedImages = filteredBase.filter(item => {
        const val = (item[key] || '').toString().toLowerCase();
        return searchKeywords.some(searchObj => {
          if (searchObj.isExact) {
            return val === searchObj.keyword;
          } else {
            return val.includes(searchObj.keyword);
          }
        });
      });
    },

    clearFilter() {
      this.filterKeyword = '';
      this.displayedImages = [...this.allImages];
    },
    
    compareSelected() {
      if (this.selectedSet.length >= 2) {
        const files = this.selectedSet.map(f => encodeURIComponent(f)).join(',');
        window.open(`/compare?files=${files}`, 'CompareSelectedFile');
      }
    },
    
    arrangeSelected() {
      if (this.selectedSet.length >= 2) {
        const files = this.selectedSet.map(f => encodeURIComponent(f)).join(',');
        window.open(`/arrange?files=${files}`, 'ArrangeSelectedFile');
      }
    },
    
    editSelected() {
      if (this.selectedSet.length === 1) {
        const fileId = this.selectedSet[0];
        const windowName = `edit_file_${fileId}`;
        window.open(`/edit?file_id=${encodeURIComponent(fileId)}`, windowName);
      }
    },
    
    async renameSelected() {
      if (this.selectedSet.length !== 1) {
        alert('請選擇一個檔案進行重新命名。');
        return;
      }

      const fileId = this.selectedSet[0];
      const oldFilename = `${fileId}.png`;

      try {
        // 1. 向後端請求建議檔名
        const suggestionRes = await fetch('/suggest_filename', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fileId: fileId })
        });

        if (!suggestionRes.ok) {
          const err = await suggestionRes.json();
          alert('無法取得建議檔名: ' + (err.error || suggestionRes.statusText));
          return;
        }

        const suggestionData = await suggestionRes.json();
        const suggestedFilename = suggestionData.suggested_filename;
        const newFilenameInput = prompt('請輸入新的檔名：', suggestedFilename);

        // 如果使用者取消或輸入空白，則停止
        if (!newFilenameInput || newFilenameInput.trim() === '') {
          console.log("取消或空白");
          return;
        }
      
        // 如果新檔名與舊檔名相同，也停止
        if (newFilenameInput === oldFilename) {
          console.log("新舊同名.");
          return;
        }

        const newFilename = newFilenameInput.trim();

      console.log("do rename.");

        // 2. 向後端發送請求來執行重新命名
        const renameRes = await fetch('/rename_file', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ old_filename: oldFilename, new_filename: newFilename })
        });

        if (!renameRes.ok) {
          const err = await renameRes.json();
          alert('重新命名失敗: ' + (err.error || renameRes.statusText));
          return;
        }

        const renameData = await renameRes.json();
        const newId = renameData.new_id;

        // 3. 成功後更新本地端的資料
        // 更新 allImages 中的物件
        const renamedImage = this.allImages.find(img => img.id === fileId);
        if (renamedImage) {
          renamedImage.id = newId;
          renamedImage.filename = newFilename;
        }

        // 更新 displayedImages 中的物件
        const renamedDisplayedImage = this.displayedImages.find(img => img.id === fileId);
        if (renamedDisplayedImage) {
          renamedDisplayedImage.id = newId;
          renamedDisplayedImage.filename = newFilename;
        }

        // 更新選取集合中的 ID
        const selectedIndex = this.selectedSet.indexOf(fileId);
        if (selectedIndex !== -1) {
          this.selectedSet.splice(selectedIndex, 1, newId);
        }
      
        alert(`檔案已成功重新命名為：${newFilename}`);

        this.scan(this.currentScanPath);

      } catch (e) {
        alert('網路或伺服器錯誤');
        console.error(e);
      }
    },
    
    async copySelected() {
      if (this.selectedSet.length !== 1) return;

      const originalId = this.selectedSet[0];
      const filename = originalId + '.png';

      try {
        const res = await fetch('/copy_file', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filename })
        });

        const data = await res.json();

        if (data.status === 'success') {
          console.log(`複製成功: ${data.new_file}`);
          
          if (this.currentScanPath) {
            // 2. 直接重掃整個 Gallery，讓後端重新回傳最新的檔案列表
            await this.scan(this.currentScanPath);
          }

          // 3. 清空選取狀態
          this.selectedSet = [];
        } else {
          alert(`複製失敗: ${data.message}`);
        }
      } catch (err) {
        alert('操作失敗');
        console.error(err);
      }
    },
    
    async deleteSelected() {
      if (this.selectedSet.length === 0 || !confirm('確定要刪除選取的圖片？')) return;
      
      const filenames = this.selectedSet.map(name => name + '.png');
      
      try {
        const res = await fetch('/delete_files', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ filenames })
        });
        
        const data = await res.json();
        const results = data.results || [];
        
        // 收集成功刪除的檔案 ID，以便後續更新響應式資料
        const successfullyDeletedIds = [];

        // 遍歷後端回傳的每個刪除結果
        results.forEach(r => {
          // 如果刪除狀態是 'success'
          if (r.status === 'success') {
            const deletedId = r.filename.replace('.png', ''); // 取得被刪除的檔案 ID
            successfullyDeletedIds.push(deletedId); // 將成功刪除的 ID 加入列表
          } else {
            // 如果刪除失敗，可以考慮在這裡給使用者一些提示
            console.warn(`檔案 ${r.filename} 刪除失敗: ${r.message || '未知錯誤'}`);
          }
        });

        // --- 更新響應式資料 ---
        // 使用 filter 篩選掉所有已成功刪除的 ID
        this.selectedSet = this.selectedSet.filter(id => !successfullyDeletedIds.includes(id));

        // 更新 allImages：保留那些 ID 不在 successfullyDeletedIds 裡的圖片
        this.allImages = this.allImages.filter(img => !successfullyDeletedIds.includes(img.id));

        // 更新 displayedImages：保留那些 ID 不在 successfullyDeletedIds 裡的圖片
        this.displayedImages = this.displayedImages.filter(img => !successfullyDeletedIds.includes(img.id));

      } catch (err) {
        alert('刪除失敗');
        console.error(err);
      }
    },
    
    // 時空因果矩陣 Chronos Causality Matrix 
    openCCM() {
      window.open('/ccm', 'EditCCM');
    },

    // 全域設定
    openGeneral() {
      window.open('/general', 'EditGeneralSetting');
    },
    
    isSelected(id) {
      return this.selectedSet.includes(id);
    },
    
    toggleSelect(id, event) {
      const index = this.selectedSet.indexOf(id);
      if (index !== -1) {
        this.selectedSet.splice(index, 1);
      } else {
        this.selectedSet.push(id);
      }
    },

    
    handleGalleryClick(event) {
      const isBlankClick = event.target === event.currentTarget;
    const isCtrlPressed = event.ctrlKey || event.metaKey;
    if (isCtrlPressed || isBlankClick) {
      const shouldSelectAll = !isBlankClick;

      if (shouldSelectAll) {
          this.displayedImages.forEach(item => {
            if (!this.selectedSet.includes(item.id)) {
              this.selectedSet.push(item.id);
            }
          });
        } else {
          this.selectedSet = [];
        }
    }
    },
    
    getTagStyle(tagStyleKey) {
      if (!tagStyleKey || !this.globalTagStyles[tagStyleKey]) return {};
      const style = this.globalTagStyles[tagStyleKey];
      return {
        color: style.color,
        backgroundColor: style.bg_color,
        border: `2px solid ${style.color}`
      };
    },
    
    shortenPath(path, maxLen = 100) {
      if (path.length <= maxLen) return path;
      const parts = path.split(/[\\/]/);
      if (parts.length < 3) return path.slice(0, maxLen - 3) + '...';
      return `${parts[0]}\\${parts[1]}\\...\\${parts[parts.length - 1]}`;
    },
    
    async init() {
      try {
        const res = await fetch('/get_scan_path');
        if (res.ok) {
          const data = await res.json();
          if (data.scanPath) {
            await this.scan(data.scanPath);
          }
        }
      } catch (e) {
        console.error('取得掃描路徑失敗', e);
      }
      
      // Adjust gallery position
      const adjustGalleryTop = () => {
        const actionButtons = document.getElementById('actionButtons');
        const gallery = document.getElementById('gallery');
        if (actionButtons && gallery) {
          gallery.style.top = actionButtons.offsetHeight + 'px';
        }
      };
      
      window.addEventListener('resize', adjustGalleryTop);
      adjustGalleryTop();
    },

    // --- 修改開始：新增 reload 單個檔案函式 ---
    reloadFile(fileId) {
      // 檢查 fileId 是否為空，避免發送無效請求
      if (!fileId) {
         console.error("無法重新載入檔案：缺少 fileId。");
         return;
      }

      fetch(`/reload_file/${encodeURIComponent(fileId)}`)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP 錯誤! 狀態碼: ${response.status}`);
          }
          return response.json();
        })
        .then(newData => {
          // 直接更新原始資料,然後重跑 filter
      // 1. 更新唯一的真理來源：allImages
          const allIndex = this.allImages.findIndex(c => c.id === fileId);

          if (allIndex !== -1) {
            console.log(`[Sync] 更新原始資料 allImages[${allIndex}]，狀態為: ${newData.status}`);
            this.allImages[allIndex] = newData;
      
            // 2. 讓過濾器根據最新的 allImages 重新產生 displayedImages
            // 這樣不管狀態是變更、隱藏還是排序，都會一次到位
            this.applyFilter(this.filterKey);
          } else {
            console.error(`[Sync] 在原始資料庫中找不到 ID: ${fileId}，同步失敗。`);
          }
      
          // 在 displayedImages 中找到對應的物件
          //const index = this.displayedImages.findIndex(c => c.id === fileId);

          //if (index !== -1) {
          //  this.displayedImages[index] = newData;
          //}
        })
        .catch(error => {
          console.error(`重新載入檔案 ${fileId} 失敗:`, error);
        });
    },
    
    toggleStatus() {
      // 透過 setTimeout 讓執行順序排在 v-model 寫入變數之後
      setTimeout(() => {
        this.applyFilter(this.filterKey);
      }, 0);
    },
});


  // --- 修改開始：加入 postMessage 監聽 ---
  window.addEventListener("message", (event) => {
    // 確認訊息來源安全
    if (event.origin !== window.location.origin) return;

    const { file_id, action } = event.data;
    if (action === "updated") {
      app.reloadFile(file_id);
	  //window.location.reload();
    }
  });
  
  // 接收 editor 資料
  const bc = new BroadcastChannel('edit_file_sync_bus');
  bc.onmessage = (e) => {
    const {file_id, action} = e.data;
    if (action === "updated") {
      app.reloadFile(file_id);
    }
  };
  
  // inital petiteVue
  PetiteVue.createApp(app).mount('[v-scope]');

});