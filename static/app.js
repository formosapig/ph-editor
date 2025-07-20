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
	  console.log("原始資料順序:", this.allImages.map(item => item.id));
      this.displayedImages = [...data.images];
	  console.log("原始資料順序:", this.displayedImages.map(item => item.id));
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
    //this.sortAscending = !this.sortAscending;
    //this.displayedImages.sort((a, b) => {
    //  const nameA = a.profile_name || '';
    //  const nameB = b.profile_name || '';
	//  console.log("compare : " + a.profile_name + "-" + b.profile_name);
      
    //  if (nameA === '' && nameB === '') return 0;
    //  const cmp = nameA.localeCompare(nameB, undefined, { sensitivity: 'base' });
    //  return this.sortAscending ? cmp : -cmp;
    //});
	// 方法 1：完全重新賦值
    //const newArray = [...this.displayedImages].sort((a, b) => {
    //  const cmp = (a.profile_name || '').localeCompare(b.profile_name || '');
    //  return this.sortAscending ? cmp : -cmp;
    //});
    
    //this.displayedImages = newArray;
    //this.sortAscending = !this.sortAscending;
  },
  
  filterImages() {
    const keyword = prompt('請輸入篩選關鍵字（空白顯示全部）：', '');
    if (keyword === null) return;
    
    const trimmed = keyword.trim().toLowerCase();
    this.displayedImages = trimmed 
      ? this.allImages.filter(item => 
          (item.id.toLowerCase().includes(trimmed) || 
          (item.profile_name && item.profile_name.toLowerCase().includes(trimmed))))
      : [...this.allImages];
  },
  
  editSelected() {
    if (this.selectedSet.length === 1) {
      const characterId = this.selectedSet[0];
      const windowName = `edit_character_${characterId}`;
      window.open(`/edit?character_id=${encodeURIComponent(characterId)}`, windowName);
    }
  },
  
  compareSelected() {
    if (this.selectedSet.length >= 2) {
      const files = this.selectedSet.map(f => encodeURIComponent(f)).join(',');
      window.location.href = `/compare?files=${files}`;
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
      
      results.forEach(r => {
        if (r.status === 'success') {
          this.selectedSet.delete(r.filename.replace('.png', ''));
          this.allImages = this.allImages.filter(img => img.id !== r.filename.replace('.png', ''));
          this.displayedImages = this.displayedImages.filter(img => img.id !== r.filename.replace('.png', ''));
        }
      });
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
    event.stopPropagation();
    const index = this.selectedSet.indexOf(id);
    if (index !== -1) {
      this.selectedSet.splice(index, 1);
    } else {
      this.selectedSet.push(id);
    }
  },

  
  handleGalleryClick(event) {
    if (event.target === event.currentTarget || event.ctrlKey || event.metaKey) {
      const shouldSelectAll = event.target !== event.currentTarget;
      
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