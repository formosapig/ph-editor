import { request } from './request.js';

document.addEventListener('alpine:init', () => {
    Alpine.data('epochManager', () => ({
        selectedProfile: '',
        profile_options: window.INITIAL_PROFILES || [],
        characters: [],  // 只留 parent === "" 的根角色
        epochChain: [],  // parent 有值的通通進來 (包含 "ROOT" 與 8 碼 "SNNUMBER")
        draggedChar: null,

        init() {
            const firstValid = this.profile_options.find(opt => !opt.disabled && opt.id);
            if (firstValid) {
                this.selectedProfile = firstValid.id;
                this.fetchCharacters(); 
            }

            this.$watch('selectedProfile', (value) => {
                this.fetchCharacters(); 
            });
        },

        async fetchCharacters() {
            if (!this.selectedProfile) return;

            console.log("正在獲取 Profile 的角色:", this.selectedProfile);
            
            try {
                const url = `/api/characters?profile_id=${encodeURIComponent(this.selectedProfile)}`;
                const response = await request(url);
                const rawResults = response.results || [];
                
                // 【重新修正的分流邏輯】
                // 1. parent 為空字串 "" 或不存在的，留在 characters
                this.characters = rawResults
                    .filter(char => char.parent === '' || !char.parent)
                    .sort((a, b) => Number(a.age) - Number(b.age));;
                
                // 2. parent 有值的 ("ROOT" 或 "SNNUMBER")，全部串進 epochChain
                this.epochChain = rawResults.filter(char => char.parent && char.parent !== '');
                
                console.log("留在外部的角色 (characters):", this.characters);
                console.log("進入鏈條的角色 (epochChain):", this.epochChain);
                
            } catch (err) {
                console.error("獲取角色失敗:", err);
            }
        },

        get ageColumns() {
            const ages = [...new Set(this.epochChain.map(item => item.age))];
            ages.sort((a, b) => Number(a) - Number(b));
            return ages;
        },
        
        get columnCount() {
            return this.ageColumns.length;
        },
        
        getAgeColIndex(age) {
            return this.ageColumns.indexOf(age);
        },
        
        get tableRows() {
            const nodeMap = new Map();
            // 先把 epochChain 所有節點對應表建立起來
            this.epochChain.forEach(item => {
                nodeMap.set(item.sn, { sn: item.sn, age: item.age, parent: item.parent, children: [] });
            });
            
            const roots = [];
            // 建立樹狀父子關係
            this.epochChain.forEach(item => {
                const node = nodeMap.get(item.sn);
                
                // 【核心修改】明確指定 parent === "ROOT" 的才是這張表格最頂層的樹狀起點
                if (item.parent === 'ROOT') {
                    roots.push(node);
                } else {
                    const parent = nodeMap.get(item.parent);
                    if (parent) parent.children.push(node);
                }
            });
            
            const orderMap = new Map();
            this.epochChain.forEach((item, idx) => orderMap.set(item.sn, idx));
            const sortRec = (n) => {
                n.children.sort((a,b) => (orderMap.get(a.sn)||0) - (orderMap.get(b.sn)||0));
                n.children.forEach(sortRec);
            };
            roots.forEach(sortRec);
            
            const colsCount = this.columnCount;
            const rows = [];
            
            const process = (node, level, sharedRow, shareMode) => {
                const ageIdx = this.getAgeColIndex(node.age);
                
                if (shareMode && sharedRow) {
                    if (ageIdx !== -1) sharedRow.cols[ageIdx] = node.sn;
                    for (let i = 0; i < node.children.length; i++) {
                        const child = node.children[i];
                        if (i === 0) process(child, level+1, sharedRow, true);
                        else process(child, level+1, null, false);
                    }
                } else {
                    const newRow = { cols: new Array(colsCount).fill(null) };
                    if (ageIdx !== -1) newRow.cols[ageIdx] = node.sn;
                    rows.push(newRow);
                    for (let i = 0; i < node.children.length; i++) {
                        const child = node.children[i];
                        if (i === 0) process(child, level+1, newRow, true);
                        else process(child, level+1, null, false);
                    }
                }
            };
            
            roots.forEach(root => process(root, 0, null, false));
            return rows;
        },
        
        handleDragStart(event, char) {
            this.draggedChar = char;
            event.dataTransfer.setData('text/plain', JSON.stringify(char));
        },

        // 在 Alpine.data('epochManager', () => ({ ... })) 裡面修改：

        handleDrop(event, targetSn = null) {
            if (!this.draggedChar) return;

            event.stopPropagation();

            // 檢查是否已經存在於鏈條中
            const exists = this.epochChain.find(c => c.sn === this.draggedChar.sn);

            if (targetSn) {
                // 【核心邏輯 A】丟到某個角色身上 -> 變成該角色的子代
                
                // 防呆 1：不能自己認自己當爸爸
                if (this.draggedChar.sn === targetSn) {
                    console.log("不能把自己設定為自己的子代！");
                    this.draggedChar = null;
                    return;
                }

                // 【新增防呆 2】檢查年齡（Age）關係
                // 從鏈條中找到目標父親的角色資料
                const parentChar = this.epochChain.find(c => c.sn === targetSn);
                
                if (parentChar) {
                    // 確保兩者轉為數字進行比對
                    const parentAge = Number(parentChar.age);
                    const childAge = Number(this.draggedChar.age);

                    // 如果孩子的年齡大於或等於父親，則攔截
                    if (childAge <= parentAge) {
                        alert(`時空悖論！孩子的年齡 (${childAge}) 不能大於或等於父母的年齡 (${parentAge})！`);
                        this.draggedChar = null;
                        return; // 中斷操作，不進行轉移
                    }
                }

                // 檢查通過，設定父子關係
                this.draggedChar.parent = targetSn;
                
                if (!exists) {
                    this.epochChain.push(this.draggedChar);
                    this.characters = this.characters.filter(c => c.sn !== this.draggedChar.sn);
                }
                console.log(`角色 ${this.draggedChar.sn} (Age: ${this.draggedChar.age}) 成功變成 ${targetSn} (Age: ${parentChar.age}) 的子代`);

            } else {
                // 【核心邏輯 B】丟在空白處 -> 變成 ROOT（新的一列）
                if (event.target.closest('.has-character')) {
                    this.draggedChar = null;
                    return;
                }

                this.draggedChar.parent = 'ROOT';
                
                if (!exists) {
                    this.epochChain.push(this.draggedChar);
                    this.characters = this.characters.filter(c => c.sn !== this.draggedChar.sn);
                }
                console.log(`角色 ${this.draggedChar.sn} 丟至空白處，設定為 ROOT`);
            }

            this.draggedChar = null;
        },

        handleDropBack(event) {
            if (!this.draggedChar) return;

            event.stopPropagation();

            // 1. 準備一個陣列，用來收集所有需要被打包帶走的角色（包含自己與所有後代）
            const targetsToRemove = [];

            // 2. 寫一個遞迴函式，找出當前角色所有的子子孫孫
            const collectDescendants = (parentSn) => {
                // 找出所有 parent 是當前這個 parentSn 的小孩
                const children = this.epochChain.filter(c => c.parent === parentSn);
                
                children.forEach(child => {
                    targetsToRemove.push(child);
                    // 繼續往下找這個小孩的孩子（孫代...）
                    collectDescendants(child.sn);
                });
            };

            // 3. 把自己跟後代通通收集起來
            targetsToRemove.push(this.draggedChar);
            collectDescendants(this.draggedChar.sn);

            // 4. 開始批次處理轉移
            targetsToRemove.forEach(char => {
                // 防呆：如果原本的 characters 列表裡面已經有了（理論上不會），就不重複加
                const exists = this.characters.find(c => c.sn === char.sn);
                
                if (!exists) {
                    // 所有滾回來的角色，父節點全部洗白變回空字串 ""
                    char.parent = '';
                    this.characters.push(char);
                }
            });

            // 5. 一口氣把所有收集到的角色從 Table 鏈條 (epochChain) 中拔除
            const targetSns = targetsToRemove.map(c => c.sn);
            this.epochChain = this.epochChain.filter(c => !targetSns.includes(c.sn));

            console.log(`成功將角色 ${this.draggedChar.sn} 及其後代（共 ${targetsToRemove.length} 個角色）一併回收`);

            // 重置拖曳狀態
            this.draggedChar = null;
        }
     }));
});