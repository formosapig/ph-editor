import { request } from './request.js';

document.addEventListener('alpine:init', () => {
    Alpine.data('phApp', () => ({
        // State
        currentScanPath: '',
        allImages: [],
        selectedSet: [],
        sortAscending: true,
        sortKey: 'filename',
        showSortMenu: false,
        filterKey: 'id',
        filterKeyword: '',
        showFilterMenu: false,
        activeStatuses: ['draft', 'refinement', 'finalized'],
        globalTagStyles: {},
        showWishing: false,
        wishes: [],
        newWishType: '📙',
        newWishContent: '',
        messages: [],

        // Getters (Alpine 內部的 Getters 會自動追蹤響應式)
        get scanPathDisplay() {
            return this.currentScanPath ? this.shortenPath(this.currentScanPath) : '尚未選擇';
        },
        get selectedCount() {
            return this.selectedSet.length;
        },
        get totalFilesCount() {
            return this.filteredAndSortedImages.length;
        },
        get isAnyMenuOpen() {
            return this.showSortMenu || this.showFilterMenu;
        },
        get filteredAndSortedImages() {
            let list = [...this.allImages];

            // --- 1. 優先過濾 Status ---
            list = list.filter(item => {
                const status = item.status || 'draft';
                return this.activeStatuses.includes(status);
            });

            // --- 2. 套用關鍵字 Filter ---
            const rawKw = this.filterKeyword.trim().toLowerCase();
            if (rawKw && this.filterKey) {
                const parts = rawKw.match(/"[^"]*"|\S+/g) || [];
                const searchKeywords = parts.map(part => {
                    const isExact = part.startsWith('"') && part.endsWith('"');
                    return {
                        keyword: isExact ? part.replace(/^"|"$/g, '') : part,
                        isExact: isExact
                    };
                });

                list = list.filter(item => {
                    const val = (item[this.filterKey] || '').toString().toLowerCase();
                    return searchKeywords.some(searchObj => {
                        if (searchObj.isExact) {
                            return val === searchObj.keyword;
                        } else {
                            return val.includes(searchObj.keyword);
                        }
                    });
                });
            }

            // --- 3. 最後進行排序 (穩定排序) ---
            list = list.map((img, idx) => ({ ...img, __originalIndex: idx }))
                .sort((a, b) => {
                    const valA = (a[this.sortKey] || '').toString();
                    const valB = (b[this.sortKey] || '').toString();
                    const cmp = valA.localeCompare(valB, undefined, { sensitivity: 'base' });
                    
                    if (cmp !== 0) {
                        return this.sortAscending ? cmp : -cmp;
                    }
                    // 若值相同，保持原始順序 (穩定排序)
                    return a.__originalIndex - b.__originalIndex;
                })
                .map(({ __originalIndex, ...img }) => img);

            return list;
        },

        async init() {
            try {
                const res = await fetch('/get_scan_path');
                if (res.ok) {
                    const data = await res.json();
                    if (data.scanPath) await this.scan(data.scanPath);
                }
            } catch (e) { console.error('取得掃描路徑失敗', e); }

            const adjustGalleryTop = () => {
                const actionButtons = document.getElementById('actionButtons');
                const gallery = document.getElementById('gallery');
                if (actionButtons && gallery) gallery.style.top = actionButtons.offsetHeight + 'px';
            };
            window.addEventListener('resize', adjustGalleryTop);
            adjustGalleryTop();

            // 接收 editor 資料 (BroadcastChannel)
            const bc = new BroadcastChannel('edit_file_sync_bus');
            bc.onmessage = (e) => {
                console.log("bus data:", e.data);
                const {sn, action} = e.data;
                if (action === "updated") {
                    this.refrechCharacter(sn);
                }
            };

            // 監控畫面最終顯示的結果
            this.$watch('filteredAndSortedImages', (newList) => {
                // 如果目前沒選任何東西，直接跳過節省效能
                if (this.selectedSet.length === 0) return;

                // 建立一個目前可見 SN 的集合 (Set) 提升比對速度
                const visibleSNs = new Set(newList.map(img => img.sn));

                // 過濾選取清單：只留下「還在畫面上」的 SN
                const validSelected = this.selectedSet.filter(sn => visibleSNs.has(sn));

                // 只有在真的有 SN 被踢掉時，才更新狀態（避免觸發無意義的響應）
                if (validSelected.length !== this.selectedSet.length) {
                    this.selectedSet = validSelected;
                }
            });
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
                    return;
                }
                this.globalTagStyles = data.tag_styles || {};
                this.allImages = data.images;
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
            if (this.showSortMenu) this.showFilterMenu = false;
        },

        applySort(key) {
            this.sortKey = key;
        },

        toggleSortOrder() {
            this.sortAscending = !this.sortAscending;
        },

        toggleFilter() {
            this.showFilterMenu = !this.showFilterMenu;
            if (this.showFilterMenu) this.showSortMenu = false;
        },

        applyFilter(key) {
            this.filterKey = key;
            this.selectedSet = [];
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

        editSelected() {
            if (this.selectedSet.length === 1) {
                const sn = this.selectedSet[0];
                window.open(`/edit/${encodeURIComponent(sn)}`, `edit_file_${sn}`);
            }
        },

        async renameSelected() {
            if (this.selectedSet.length !== 1) return;
            const sn = this.selectedSet[0];
            try {
                const suggestionRes = await fetch(`api/characters/${encodeURIComponent(sn)}/suggest`);
                const suggestionData = await suggestionRes.json();
                const newFilenameInput = prompt('請輸入新的檔名：', suggestionData.suggested);

                if (!newFilenameInput || newFilenameInput.trim() === '') return;
                
                const oldFileName = this.allImages.find(img => img.sn === sn).file_id;
                if (newFilenameInput.trim() === oldFileName) {
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

                this.allImages.forEach(list => {
                    const img = list.find(i => i.sn === sn);
                    if (img) img.file_id = newFilename;
                });

                this.selectedSet = [];
                this.showMessage(`檔案已成功重新命名為：${newFilename}`);
            } catch (e) {
                this.showMessage('網路或伺服器錯誤');
            }
        },

        async cloneSelected() {
            if (this.selectedSet.length !== 1) return;
            const originalSN = this.selectedSet[0];
            try {
                const data = await request(`/api/characters/${encodeURIComponent(originalSN)}/clone`, {method: 'POST'});
                const newChar = data.new_data;
                const updateList = (list) => {
                    const idx = list.findIndex(img => img.sn === originalSN);
                    if (idx !== -1) list.splice(idx + 1, 0, newChar);
                    else list.push(newChar);
                };
                updateList(this.allImages);
                this.selectedSet = [newChar.sn];
                this.showMessage(`複製成功: ${newChar.file_id}`);
            } catch (err) {
                this.showMessage(err.displayMessage || '系統錯誤');
            }
        },

        async deleteSelected() {
            if (this.selectedSet.length === 0 || !confirm('確定要刪除選取的圖片？')) return;
            const serial_numbers = [...this.selectedSet];
            try {
                const data = await request('/api/characters', {
                    method: 'DELETE',
                    body: JSON.stringify({ serial_numbers })
                });
                const successfullyDeletedSNs = (data.results || [])
                    .filter(r => r.status === 'success').map(r => r.sn);
                
                //this.selectedSet = [];
                this.allImages = this.allImages.filter(img => !successfullyDeletedSNs.includes(img.sn));
                this.showMessage(`成功刪除 ${successfullyDeletedSNs.length} 個角色`);
            } catch (err) {
                this.showMessage(err.displayMessage || '系統錯誤');
            }
        },

        openGeneral() { window.open('/general', 'EditGeneralSetting'); },
        openCCM() { window.open('/ccm', 'EditCCM'); },
        openEpoch() { window.open('/epoch', 'EditEpoch'); },
        
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
            this.wishes.push(saved);
            this.newWishContent = '';
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

        isSelected(id) { return this.selectedSet.includes(id); },
        
        toggleSelect(id, event) {
            const index = this.selectedSet.indexOf(id);
            if (index !== -1) this.selectedSet.splice(index, 1);
            else this.selectedSet.push(id);
        },

        handleGalleryClick(event) {
            const isBlankClick = event.target === event.currentTarget;
            const isCtrlPressed = event.ctrlKey || event.metaKey;
            if (isCtrlPressed || isBlankClick) {
                if (!isBlankClick) {
                    this.filteredAndSortedImages.forEach(item => {
                         if (!this.selectedSet.includes(item.sn)) this.selectedSet.push(item.sn);
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

        async refrechCharacter(sn) {
            if (!sn) return false;
            try {
                const response = await fetch(`/api/characters/${encodeURIComponent(sn)}/refresh?view=gallery`);
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const newData = await response.json();
                const allIndex = this.allImages.findIndex(c => c.sn === sn);
                if (allIndex !== -1) {
                    // 先丟進去，之後 fileterAndSort 會篩
                    if (!this.selectedSet.includes(sn)) this.selectedSet.push(sn);
                    this.allImages[allIndex] = { ...this.allImages[allIndex], ...newData };
                    return true;
                }
                return false;
            } catch (error) { return false; }
        },

        showMessage(text) {
            const id = Date.now();
            this.messages.push({ id, text });
            setTimeout(() => {
                this.messages = this.messages.filter(m => m.id !== id);
            }, 3000);
        }
    }));
});