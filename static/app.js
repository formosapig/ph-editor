import { request } from './request.js';

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
        
        // 在 petite-vue 的狀態物件中
        showWishing: false,
        wishes: [],
        newWishType: '📙',
        newWishContent: '',
        messages: [],
        
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
                const serial_numbers = this.selectedSet.map(f => encodeURIComponent(f)).join(',');
                window.open(`/compare?serial_numbers=${serial_numbers}`, 'CompareSelectedFile');
            }
        },
        
        arrangeSelected() {
        if (this.selectedSet.length >= 2) {
            const files = this.selectedSet.map(f => encodeURIComponent(f)).join(',');
            window.open(`/arrange?files=${files}`, 'ArrangeSelectedFile');
        }
        },

        // 編輯 character
        editSelected() {
            if (this.selectedSet.length === 1) {
                const sn = this.selectedSet[0];
                const windowName = `edit_file_${sn}`;
                window.open(`/edit/${encodeURIComponent(sn)}`, windowName);
            }
        },

        // 修改 character 的 檔名(file_id)
        async renameSelected() {
            if (this.selectedSet.length !== 1) return;
      
            const sn = this.selectedSet[0];
            
            try {
                // 1. 向後端請求建議檔名
                const suggestionRes = await fetch(`api/characters/${encodeURIComponent(sn)}/suggest`, {method: 'GET'});

                if (!suggestionRes.ok) {
                    this.showMessage('無法取得建議檔名: ' + (suggestionRes.error || suggestionRes.statusText));
                    return;
                }

                const suggestionData = await suggestionRes.json();
                const suggestedFilename = suggestionData.suggested;
                const newFilenameInput = prompt('請輸入新的檔名：', suggestedFilename);

                if (!newFilenameInput || newFilenameInput.trim() === '') {
                    console.log("取消或空白");
                    return;
                }
      
                const oldFileName = this.allImages.find(img => img.sn === sn).file_id;
                if (newFilenameInput === oldFileName) {
                    this.showMessage("新舊同名.");
                    return;
                }

                const newFilename = newFilenameInput.trim();
                const renameRes = await fetch(`/api/characters/${encodeURIComponent(sn)}/rename`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ new_file_id: newFilename })
                });

                if (!renameRes.ok) {
                    const err = await renameRes.json();
                    this.showMessage('重新命名失敗: ' + (err.error || renameRes.statusText));
                    return;
                }

                const renamedImage = this.allImages.find(img => img.sn === sn);
                if (renamedImage) {
                    renamedImage.file_id = newFilename;
                }
                
                const renamedDisplayedImage = this.displayedImages.find(img => img.sn === sn);
                if (renamedDisplayedImage) {
                    renamedDisplayedImage.file_id = newFilename;
                }

                this.selectedSet = [];
                this.showMessage(`檔案已成功重新命名為：${newFilename}`);
            } catch (e) {
                this.showMessage('網路或伺服器錯誤');
                console.error(e);
            }
        }, // renameSelected
    
        async cloneSelected() {
            if (this.selectedSet.length !== 1) return;

            const originalSN = this.selectedSet[0];
            
            try {
                const url = `/api/characters/${encodeURIComponent(originalSN)}/clone`;
                const data = await request(url, {method: 'POST'});
                const newChar = data.new_data;
                
                const idx = this.allImages.findIndex(img => img.sn === originalSN);
                if (idx !== -1) {
                    this.allImages.splice(idx + 1, 0, newChar);
                } else {
                    this.allImages.push(newChar);
                }

                const idx2 = this.displayedImages.findIndex(img => img.sn === originalSN);
                if (idx2 !== -1) {
                    this.displayedImages.splice(idx2 + 1, 0, newChar);
                } else {
                    this.displayedImages.push(newChar);
                }

                this.selectedSet = [newChar.sn];
                this.showMessage(`複製成功: ${newChar.file_id}`)
            } catch (err) {
                this.showMessage(err.displayMessage || '系統錯誤');
            }
        }, // cloneSelected
    
        async deleteSelected() {
            if (this.selectedSet.length === 0 || !confirm('確定要刪除選取的圖片？')) return;
      
            const serial_numbers = [...this.selectedSet]; // 確保傳送的是純 sn 陣列
      
            try {
                const data = await request('/api/characters', {
                    method: 'DELETE',
                    body: JSON.stringify({ serial_numbers })
                });
                
                const results = data.results || [];
                const successfullyDeletedSNs = results
                    .filter(r => r.status === 'success')
                    .map(r => r.sn);
            
                // --- 更新響應式資料 ---
                this.selectedSet = [];
                this.allImages = this.allImages.filter(img => !successfullyDeletedSNs.includes(img.sn));
                this.displayedImages = this.displayedImages.filter(img => !successfullyDeletedSNs.includes(img.sn));
                this.showMessage(`成功刪除 ${successfullyDeletedSNs.length} 個角色`);
            } catch (err) {
                this.showMessage(err.displayMessage || '系統錯誤');
            }
        },

        // 全域設定
        openGeneral() {
            window.open('/general', 'EditGeneralSetting');
        },
        
        // 時空因果矩陣 Chronos Causality Matrix 
        openCCM() {
            window.open('/ccm', 'EditCCM');
        },

        // 歲月編輯器
        openEpoch() {
            window.open('/epoch', 'EditEpoch');
        },
        
        // 許願噴泉
        async openWishing() {
            this.showWishing = !this.showWishing;
            if (this.showWishing) {
                const res = await fetch('/wishes');
                this.wishes = await res.json();
            }
            },

            async submitWish() {
            if (!this.newWishContent.trim()) return;
            const res = await fetch('/wishes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: this.newWishType, content: this.newWishContent })
            });
            const saved = await res.json();
            //console.log("Saved:", saved);
            console.log("原本第一筆:", this.wishes[0]?.content);
            this.wishes.push(saved);
            console.log("現在第一筆:", this.wishes[0]?.content);
            
            console.log("新資料 ID 類型:", typeof saved.id);
            console.log("舊資料 ID 類型:", typeof this.wishes[1]?.id);
            
            
            this.newWishContent = ''; // 清空輸入框
        
        // 選擇性：自動捲動到底部，讓使用者看到剛投進去的願望
            this.$nextTick(() => {
                const el = document.querySelector('.wish-list');
                if (el) el.scrollTop = el.scrollHeight;
            });
        },

        async deleteWish(id) {
        if (!confirm('確定要移除這個願望？')) return;
        await fetch(`/wishes/${id}`, { method: 'DELETE' });
        this.wishes = this.wishes.filter(w => w.id !== id);
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

        // 經由 bc 傳來要更新某一個 character ...
        async refrechCharacter(sn) {
            if (!sn) {
                console.error("無法重新載入檔案，沒有 sn 。");
                return;
            }

            try {
                const url = `/api/characters/${encodeURIComponent(sn)}/refresh?view=gallery`;
                const response = await fetch(url, {method: 'GET'});
                if (!response.ok) {
                    throw new Error(`HTTP 錯誤! 狀態碼: ${response.status}`);
                }

                const newData = await response.json();
                const allIndex = this.allImages.findIndex(c => c.sn === sn);
                
                if (allIndex !== -1) {
                    console.log(`[Sync] 更新原始資料 allImages[${allIndex}]，狀態為: ${newData.status}`);
                    this.allImages[allIndex] = { ...this.allImages[allIndex], ...newData };
                    this.applyFilter(this.filterKey);
                    return true;
                } else {
                    console.error(`在原始資料庫中找不到 SN: ${sn}，同步失敗。`);
                    return false;
                }

            } catch (error) {
                console.error(`重新載入 SN: ${sn} 失敗:`, error);
                return false;
            }
        }, // refreshCharacter
    
        toggleStatus() {
            // 透過 setTimeout 讓執行順序排在 v-model 寫入變數之後
            setTimeout(() => {
                this.applyFilter(this.filterKey);
            }, 0);
        },

        showMessage(text) {
            const id = Date.now();
            this.messages.push({ id, text });

            // 3秒後自動移除該筆訊息
            setTimeout(() => {
                this.messages = this.messages.filter(m => m.id !== id);
            }, 3000);
        },

    }); // const app = PetiteVue.reactive({

    // 接收 editor 資料
    const bc = new BroadcastChannel('edit_file_sync_bus');
    bc.onmessage = (e) => {
        console.log("bus data:", e.data);
        const {sn, action} = e.data;
        if (action === "updated") {
            app.refrechCharacter(sn);
        }
    };
  
    // inital petiteVue
    PetiteVue.createApp(app).mount('[v-scope]');

}); // window.addEventListener('DOMContentLoaded', () => {