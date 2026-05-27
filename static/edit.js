import { request } from './request.js';
import { nameMap, searchRegex } from './mapping.js';

document.addEventListener('alpine:init', () => {
    Alpine.data('characterEditor', (params) => ({
        sn: params.sn,
        file_id: params.file_id,
        correct: params.correct,
        appearance: params.appearance,
        clothing: params.clothing,
        snapshot: params.snapshot,
        globalParsedData: params.initialData || {},

        activeMainTab: 'story',
        activeSubTab: 'profile',
        dropdowns: [],
        
        // 訊息系統
        messageText: '',
        messageType: 'success',
        
        // Timer
        autoSaveTimer: null,
        remarkTimer: null,
        remarkHasChanged: false,
        hasChanged: false,

        // 請求令牌
        currentRequestId: 0,
        
        messages: [],

        mainTabs: {
            story: '故事', hair: '頭髮', face: '臉部',
            body: '身體', clothing: '服裝', accessory: '配件'
        },

        subTabsConfig: {
            hair: [ { key: 'back_hair', label: '後髮' }, { key: 'front_hair', label: '前髮' }, { key: 'side_hair', label: '側髮' } ],
            face: [ { key: 'overall', label: '全体' }, { key: 'ears', label: '耳朵' }, { key: 'eyebrows', label: '眉毛' }, { key: 'eyelashes', label: '睫毛' }, { key: 'eyes', label: '眼睛' }, { key: 'eyeballs', label: '眼球' }, { key: 'nose', label: '鼻子' }, { key: 'cheeks', label: '臉頰' }, { key: 'mouth', label: '嘴唇' }, { key: 'chin', label: '下巴' }, { key: 'mole', label: '痣' }, { key: 'makeup', label: '化妝' }, { key: 'tattoo', label: '刺青' } ],
            body: [ { key: 'overall', label: '全体' }, { key: 'breast', label: '胸部' }, { key: 'upper_body', label: '上半身' }, { key: 'lower_body', label: '下半身' }, { key: 'arms', label: '腕' }, { key: 'legs', label: '腳' }, { key: 'nails', label: '指甲' }, { key: 'pubic_hair', label: '陰毛' }, { key: 'tan_lines', label: '曬痕' }, { key: 'tattoo', label: '刺青' } ],
            clothing: [ { key: 'top', label: '上衣' }, { key: 'bottom', label: '下著' }, { key: 'bra', label: '胸罩' }, { key: 'panty', label: '內褲' }, { key: 'swimsuit', label: '泳衣' }, { key: 'swimsuit_top', label: '泳衣-上衣' }, { key: 'swimsuit_bottom', label: '泳衣-下著' }, { key: 'gloves', label: '手套' }, { key: 'pantyhose', label: '褲襪' }, { key: 'socks', label: '襪子' }, { key: 'shoes', label: '鞋子' } ],
            accessory: Array.from({length: 10}, (_, i) => ({ key: `accessory_${(i+1).toString().padStart(2, '0')}`, label: (i+1).toString().padStart(2, '0') })),
            story: [ { key: 'profile', label: '簡介' }, { key: 'scenario', label: '場景' }, { key: 'backstage', label: '幕後' } ]
        },

        init() {
            window.app = this; // 除錯使用
            this.switchMainTab('story');
            this.showMessage('角色資料預載完成。');
        },

        // --- Tab 切換 ---
        switchMainTab(key) {
            this.activeMainTab = key;
            const firstSub = this.subTabsConfig[key]?.[0]?.key;
            if (firstSub) this.switchSubTab(firstSub);
        },

        switchSubTab(key) {
            this.activeSubTab = key;
            this.renderContent();
            this.fetchDropdowns();
        },

        // --- 內容渲染與儲存 ---
        renderContent() {
            const data = this.globalParsedData[this.activeMainTab]?.[this.activeSubTab];
            const displayData = {};
            if (data) {
                // 過濾掉 ! 開頭的 key
                Object.keys(data).forEach(k => {
                    if (!k.startsWith('!')) displayData[k] = data[k];
                });
            }
            console.error("render", this.activeMainTab, this.activeSubTab, displayData);
            //let jsonString = JSON.stringify(displayData, null, 2);
            //this.$refs.mainContent.textContent = jsonString.replace(/^\{\s*/, '').replace(/\s*\}$/, '');
            this.$refs.mainContent.textContent = JSON.stringify(displayData, null, 2);
        },

        handleContentInput() {
            this.hasChanged = true;
            clearTimeout(this.autoSaveTimer);
            this.autoSaveTimer = setTimeout(() => this.saveContent(), 30000);
        },

        translateSelection(event) {
            const selection = window.getSelection();
            if (!selection.rangeCount) return;

            const range = selection.getRangeAt(0);
            const selectedText = range.toString();

            // 進行轉換
            const translated = selectedText.replace(searchRegex, (matched) => nameMap[matched]);

            if (translated !== selectedText) {
                // 核心邏輯：刪除當前選取的內容節點，並插入新節點
                range.deleteContents(); 
                range.insertNode(document.createTextNode(translated));
                
                this.handleContentInput();
                selection.removeAllRanges();
            }
        },

        async saveContent() {
            if (!this.hasChanged) return;
            
            const currentMainTab = this.activeMainTab;
            const currentSubTab = this.activeSubTab;

            //let rawContent = this.$refs.mainContent.textContent.trim();
            let newData;
            try {
                //newData = JSON.parse(`{ ${rawContent} }`);
                newData = JSON.parse(this.$refs.mainContent.textContent);
            } catch (e) {
                return this.showMessage('JSON 格式錯誤', 'error');
            }

            // 補回 ! 開頭的隱藏資料
            const originalData = this.globalParsedData[this.activeMainTab][this.activeSubTab];
            for (let k in originalData) {
                if (k.startsWith('!')) newData[k] = originalData[k];
            }

            await this.uploadData(newData, currentMainTab, currentSubTab);
            this.hasChanged = false;
        },

        async uploadData(newData, mainTab, subTab) {
            const url = `/api/characters/${encodeURIComponent(this.sn)}/data/${mainTab}/${subTab}`;
            try {
                const result = await request(url, {
                    method: 'PATCH',
                    body: JSON.stringify({ data: newData })
                });
                this.globalParsedData[mainTab][subTab] = newData;
                this.showMessage(result.message || '更新成功');
                this.notifyParent();
                // 根據後端需求重新載入選單
                if (result.need_update_profile_dropdown || result.need_update_scenario_dropdown) {
                    this.fetchDropdowns();
                }
            } catch (e) {
                this.showMessage(e.displayMessage || '儲存失敗', 'error');
            }
        },

        // --- 下拉選單邏輯 ---
        async fetchDropdowns() {
            const requestId = ++this.currentRequestId;

            this.dropdowns = [];
            let apiUrl = `/api/ui_config/options/${this.activeMainTab}/${this.activeSubTab}`;
            if (this.activeMainTab === 'story') {
                if (this.activeSubTab === 'profile') apiUrl = `/api/ui_config/profiles`;
                if (this.activeSubTab === 'scenario') apiUrl = `/api/ui_config/${encodeURIComponent(this.sn)}/scenarios`;
                if (this.activeSubTab === 'backstage') apiUrl = `/api/ui_config/backstage_options`;
            }

            try {
                const result = await request(apiUrl);
                if (requestId !== this.currentRequestId) {
                    console.warn("捨棄過時的請求結果");
                    return;
                }
                this.dropdowns = result.dropdowns || [];
            } catch (e) {
                if (requestId === this.currentRequestId) {
                    this.dropdowns = [];
                    this.showMessage(e.displayMessage, 'warning');
                }
            }
        },

        async handleDropdownChange(config, event) {
            const targetTab = this.activeMainTab;
            const targetSub = this.activeSubTab;
            const val = JSON.parse(event.target.value);
            const selectedOption = event.target.options[event.target.selectedIndex];
            const optObj = config.options.find(o => JSON.stringify(o.value) === event.target.value);
            const label = optObj ? (optObj.pureLabel || optObj.label) : selectedOption.text;

            // 預設需要走通用更新
            let shouldPerformGeneralUpdate = true;

            // 1. 處理 Profile/Scenario ID 抓取
            if (config.dataKey === "!id" && val !== "") {
                const type = this.activeSubTab === 'profile' ? 'profile' : 'scenario';
                const res = await fetch(`/api/${type}/detail/${val}`);
                const detailData = await res.json();
                this.globalParsedData[targetTab][targetSub] = detailData;
                
                // 既然已經替換了整個物件，通常就不需要再走後面的 Key 賦值
                shouldPerformGeneralUpdate = false; 

            // 2. 處理 Year 的特殊 API 邏輯
            } else if (config.dataKey === "year" && val !== "" && targetSub === 'scenario') {
                const res = await fetch(`/api/scenario/reverberation/${val}?sn=${encodeURIComponent(this.sn)}`);
                if (res.status === 200) {
                    this.globalParsedData[targetTab][targetSub] = await res.json();
                    // 如果後端回傳的是完整的新資料，就不需要走通用更新
                    shouldPerformGeneralUpdate = false;
                } else if (res.status === 204) {
                    shouldPerformGeneralUpdate = true;
                } else {
                    // 如果 API 失敗 (例如 404/500)，旗標保持 true，讓它流向通用更新
                    console.warn("API 失敗，改走通用更新流程");
                    return;
                }
            }

            // 3. 通用更新 (原本的 else 區塊)
            if (shouldPerformGeneralUpdate) {
                const dataRef = this.globalParsedData[targetTab][targetSub];
                if (val === "") {
                    delete dataRef[config.dataKey];
                    if (config.labelKey) delete dataRef[config.labelKey];
                } else {
                    dataRef[config.dataKey] = val;
                    if (config.labelKey && config.labelKey !== config.dataKey) {
                        dataRef[config.labelKey] = label;
                    }
                }
            }

            // 4. 後續工作 (不受影響，必定執行)
            if (this.activeMainTab === targetTab && this.activeSubTab === targetSub) {
                this.renderContent();
            }
            this.hasChanged = true;
            this.saveContent();
        },

        isOptionSelected(config, opt) {
            const current = this.globalParsedData[this.activeMainTab]?.[this.activeSubTab]?.[config.dataKey];
            return JSON.stringify(current) === JSON.stringify(opt.value);
        },

        // --- 備註 (Remark) 處理 ---
        handleRemarkInput() {
            this.remarkHasChanged = true;
            clearTimeout(this.remarkTimer);
            // 10秒防抖動自動儲存
            this.remarkTimer = setTimeout(() => {
                this.saveRemark();
            }, 10000);
        },

        async saveRemark() {
            if (!this.remarkHasChanged) return;
            const newRemark = this.$refs.remark.innerText.trim();
            const url = `/api/characters/${encodeURIComponent(this.sn)}/remark`;

            try {
                const result = await request(url, {
                    method: 'PATCH',
                    body: JSON.stringify({ remark: newRemark })
                });

                this.showMessage('備註更新成功');
                this.remarkHasChanged = false;
                this.notifyParent();
            } catch (error) {
                this.showMessage(error.displayMessage, 'error');
            }
        },

        async reload(imgElement) {
            // 取得原本的網址（不含參數部分）
            const baseUrl = imgElement.src.split('?')[0];
            // 加上時間戳記，強制瀏覽器重新請求
            imgElement.src = `${baseUrl}?t=${new Date().getTime()}`;

            try {
                const data = await request(`/edit/${encodeURIComponent(this.sn)}`, {
                    method: 'PATCH'
                });

                // 成功更新狀態
                this.file_id = data.file_id;
                this.correct = data.correct;
                this.appearance = data.appearance;
                this.clothing = data.clothing;
                this.snapshot = data.snapshot;
                
                this.showMessage('資料重載成功');
            } catch (err) {
                this.showMessage(error.displayMessage, 'error');
            }
        },

        notifyParent() {
            const bc = new BroadcastChannel('edit_file_sync_bus');
            bc.postMessage({ sn: this.sn, action: "updated" });
        },
        
        showMessage(text, type = 'success') {
            const id = Date.now();
            //console.error("id : ", id);
            this.messages.push({ id, text, type });
            setTimeout(() => {
                this.messages = this.messages.filter(m => m.id !== id);
            }, 3000);
        }

    }));
});