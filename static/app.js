window.addEventListener('DOMContentLoaded', () => {
  PetiteVue.createApp(window.app).mount('[v-scope]');
});

window.app = {
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
  
  applyFilter(key) {
    this.filterKey = key;
    const kw = this.filterKeyword.trim().toLowerCase();

    // 這裡是修改處：在執行新的篩選前，將所有選取的項目清空
    this.selectedSet = []; 

    if (!kw || !this.filterKey) {
      this.displayedImages = [...this.allImages];
      return;
    }

    this.displayedImages = this.allImages.filter(item => {
      const val = (item[key] || '').toString().toLowerCase();
      return val.includes(kw);
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
  }
};