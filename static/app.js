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
  
  editSelected() {
    if (this.selectedSet.length === 1) {
      const fileId = this.selectedSet[0];
      const windowName = `edit_file_${fileId}`;
      window.open(`/edit?file_id=${encodeURIComponent(fileId)}`, windowName);
    }
  },
  
  compareSelected() {
    if (this.selectedSet.length >= 2) {
      const files = this.selectedSet.map(f => encodeURIComponent(f)).join(',');
      window.open(`/compare?files=${files}`, 'CompareSelectedFile');
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