import { request } from './request.js';

document.addEventListener('alpine:init', () => {
    Alpine.data('epochManager', () => ({
        selectedProfile: '',
        profile_options: window.INITIAL_PROFILES || [],
        characters: [],  // 只留 upstream === "" 的根角色
        epochChain: [],  // upstream 有值的通通進來 (包含 "ROOT" 與 8 碼 "SNNUMBER")
        draggedChar: null,

        init() {
            //const firstValid = this.profile_options.find(opt => !opt.disabled && opt.id);
            //if (firstValid) {
            //    this.selectedProfile = firstValid.id;
            //    this.fetchCharacters(); 
           // }

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
                // 1. upstream 為空字串 "" 或不存在的，留在 characters
                this.characters = rawResults
                    .filter(char => char.upstream === '' || !char.upstream)
                    .sort((a, b) => Number(a.age) - Number(b.age));;
                
                // 2. upstream 有值的 ("ROOT" 或 "SNNUMBER")，全部串進 epochChain
                this.epochChain = rawResults.filter(char => char.upstream && char.upstream !== '');
                
                console.log("留在外部的角色 (characters):", this.characters);
                console.log("進入鏈條的角色 (epochChain):", this.epochChain);
                
            } catch (err) {
                console.error("獲取角色失敗:", err);
            }
        },

        get ageColumns() {
            const ages = [...new Set(this.epochChain.map(item => item.age))];
            ages.sort((a, b) => Number(a) - Number(b));
            
            const result = [];

            result.push('α');

            if (ages.length === 0) {
                return result;
            }

            for (let i = 0; i < ages.length; i++) {
                result.push(ages[i]);      // 真正的 age 欄位
                if (i < ages.length - 1) {
                    result.push('');

                }
            }
            return result;
        },

        get columnCount() {
            return Math.max(1, this.ageColumns.length);
        },
        
        getAgeColIndex(age) {
            const idx = this.ageColumns.indexOf(age);
            return idx;
        },
        
        get tableRows() {
            const nodeMap = new Map();
            // 先把 epochChain 所有節點對應表建立起來
            this.epochChain.forEach(item => {
                nodeMap.set(item.sn, { sn: item.sn, age: item.age, upstream: item.upstream, children: [] });
            });
            
            const roots = [];
            // 建立樹狀父子關係
            this.epochChain.forEach(item => {
                const node = nodeMap.get(item.sn);
                
                // 【核心修改】明確指定 upstream === "ROOT" 的才是這張表格最頂層的樹狀起點
                if (item.upstream === 'ROOT') {
                    roots.push(node);
                } else {
                    const upstream = nodeMap.get(item.upstream);
                    if (upstream) upstream.children.push(node);
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
        
        get tableRowsWithLines() {
            const rows = this.tableRows;
            if (!rows.length) {
                const colsCount = this.columnCount;
                return [{
                    nodes: new Array(colsCount).fill(null),
                    connectors: new Array(colsCount).fill(null)
                }];
            }

            const colsCount = this.columnCount;
            // 建立 grid，複製原本的節點
            const grid = rows.map(row => ({
                nodes: [...row.cols],
                connectors: new Array(colsCount).fill(null)
            }));
            
            // 建立節點位置 Map
            const nodePos = new Map();
            rows.forEach((row, rowIdx) => {
                row.cols.forEach((sn, colIdx) => {
                    if (sn) nodePos.set(sn, { row: rowIdx, col: colIdx });
                });
            });
            
            // 建立父子關係
            const nodeMap = new Map();
            this.epochChain.forEach(item => {
                nodeMap.set(item.sn, { sn: item.sn, age: item.age, upstream: item.upstream, children: [] });
            });
            this.epochChain.forEach(item => {
                const node = nodeMap.get(item.sn);
                if (item.upstream === 'ROOT') return;
                const upstream = nodeMap.get(item.upstream);
                if (upstream) upstream.children.push(node);
            });
            
            // 畫線
            
            const drawLines = (node) => {
                const to2Pos = nodePos.get(node.sn);
                if (!to2Pos) return;
                console.error("node", node);
                console.error("nodePos", nodePos);

                if (node.upstream === "ROOT") {
                    for (let col = to2Pos.col - 1; col > 0; col--) {
                        grid[to2Pos.row].connectors[col] = "-";
                    }
                    grid[to2Pos.row].connectors[0] = "o-";
                }

                
                for (const child of node.children) {
                    const fromPos = nodePos.get(child.sn);
                    if (!fromPos) continue;
                    
                    const end2Col = to2Pos.col + 1;
                    const startCol = fromPos.col - 1;

                    if (to2Pos.row !== fromPos.row) {
                        for (let col = startCol; col >= end2Col; col--) {
                            if (col === end2Col) {
                                const existing = grid[fromPos.row].connectors[col];
                                if (existing === '|') {
                                    grid[fromPos.row].connectors[col] = '|-';
                                    break;  // 結束，不繼續畫
                                } else if (!existing || existing === '') {
                                    grid[fromPos.row].connectors[col] = 'L';
                                    //firstCellProcessed = true;
                                    // 啟動父親追殺令
                                    let killRow = fromPos.row - 1;
                                    let killCol = col;
                                    let killActive = true;
                                    
                                    while (killActive && killRow >= to2Pos.row) {
                                        const cellContent = grid[killRow]?.connectors[killCol];
                                        
                                        if (cellContent === 'L') {
                                            grid[killRow].connectors[killCol] = '|-';
                                            killActive = false;
                                        } else if (cellContent === '-') {
                                            grid[killRow].connectors[killCol] = 'T';
                                            killActive = false;
                                        } else if (!cellContent || cellContent === '') {
                                            grid[killRow].connectors[killCol] = '|';
                                            killRow--;
                                        } else {
                                            killActive = false;  // 其他情況裝死
                                        }
                                    }
                                } else {
                                    break;
                                }
                            } 
                            else {
                                grid[fromPos.row].connectors[col] = '-';
                            }
                        }
                    } 
                    else {
                        for (let col = startCol; col >= end2Col; col--) {
                            grid[fromPos.row].connectors[col] = '-';
                        }
                    }
                    
                    drawLines(child);
                }
            };
           
            const roots = this.epochChain.filter(item => item.upstream === 'ROOT');
            roots.forEach(root => {
                const node = nodeMap.get(root.sn);
                if (node) drawLines(node);
            });
            
            return grid;
        },

        handleDragStart(event, char) {
            this.draggedChar = char;
            event.dataTransfer.setData('text/plain', JSON.stringify(char));
        },

        // 在 Alpine.data('epochManager', () => ({ ... })) 裡面修改：

        handleDrop(event, targetSn = null) {
            event.preventDefault();  // ✅ 加上這行

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
                const upstreamChar = this.epochChain.find(c => c.sn === targetSn);
                
                if (upstreamChar) {
                    // 確保兩者轉為數字進行比對
                    const upstreamAge = Number(upstreamChar.age);
                    const childAge = Number(this.draggedChar.age);

                    // 如果孩子的年齡大於或等於父親，則攔截
                    if (childAge <= upstreamAge) {
                        alert(`時空悖論！孩子的年齡 (${childAge}) 不能大於或等於父母的年齡 (${upstreamAge})！`);
                        this.draggedChar = null;
                        return; // 中斷操作，不進行轉移
                    }
                }

                // 檢查通過，設定父子關係
                this.draggedChar.upstream = targetSn;

                this.updateCharacterUpstream(this.draggedChar.sn, targetSn, "透過拖曳設定");
                
                if (!exists) {
                    this.epochChain.push(this.draggedChar);
                    this.characters = this.characters.filter(c => c.sn !== this.draggedChar.sn);
                }
                console.log(`角色 ${this.draggedChar.sn} (Age: ${this.draggedChar.age}) 成功變成 ${targetSn} (Age: ${upstreamChar.age}) 的子代`);

            } else {
                // 【核心邏輯 B】丟在空白處 -> 變成 ROOT（新的一列）
                if (event.target.closest('.has-character')) {
                    this.draggedChar = null;
                    return;
                }

                this.draggedChar.upstream = 'ROOT';

                this.updateCharacterUpstream(this.draggedChar.sn, 'ROOT', "透過拖曳設定");
                
                if (!exists) {
                    this.epochChain.push(this.draggedChar);
                    this.characters = this.characters.filter(c => c.sn !== this.draggedChar.sn);
                }
                console.log(`角色 ${this.draggedChar.sn} 丟至空白處，設定為 ROOT`);
            }

            this.draggedChar = null;
        },

        handleDropBack(event) {
            event.preventDefault();  // ✅ 加上這行

            if (!this.draggedChar) return;

            event.stopPropagation();

            // 1. 準備一個陣列，用來收集所有需要被打包帶走的角色（包含自己與所有後代）
            const targetsToRemove = [];

            // 2. 寫一個遞迴函式，找出當前角色所有的子子孫孫
            const collectDescendants = (upstreamSn) => {
                // 找出所有 upstream 是當前這個 upstreamSn 的小孩
                const children = this.epochChain.filter(c => c.upstream === upstreamSn);
                
                children.forEach(child => {
                    targetsToRemove.push(child);
                    // 繼續往下找這個小孩的孩子（孫代...）
                    collectDescendants(child.sn);
                });
            };

            // 3. 把自己跟後代通通收集起來
            targetsToRemove.push(this.draggedChar);
            collectDescendants(this.draggedChar.sn);

            // 4. ✅ 批量清除所有角色的 upstream
            const snList = targetsToRemove.map(c => c.sn);
            this.batchClearUpstream(snList);

            // 4. 開始批次處理轉移
            targetsToRemove.forEach(char => {
                // 防呆：如果原本的 characters 列表裡面已經有了（理論上不會），就不重複加
                const exists = this.characters.find(c => c.sn === char.sn);
                
                if (!exists) {
                    // 所有滾回來的角色，父節點全部洗白變回空字串 ""
                    char.upstream = '';
                    this.characters.push(char);
                }
            });

            // 5. 一口氣把所有收集到的角色從 Table 鏈條 (epochChain) 中拔除
            const targetSns = targetsToRemove.map(c => c.sn);
            this.epochChain = this.epochChain.filter(c => !targetSns.includes(c.sn));

            // 6. ✅ 按照 age 從小到大排序
            this.characters.sort((a, b) => a.age - b.age);

            console.log(`成功將角色 ${this.draggedChar.sn} 及其後代（共 ${targetsToRemove.length} 個角色）一併回收`);

            // 重置拖曳狀態
            this.draggedChar = null;
        },

        async updateCharacterUpstream(sn, upstreamSn) {
            try {
                const data = await request(`/api/character/${sn}/upstream/${upstreamSn}`, { method: "PATCH" });
                console.log(`✅ upstream 已更新: ${sn} -> ${upstreamSn}`);
                return true;
            } catch (err) {
                console.warn(`設定 upstream 失敗: ${sn} -> ${upstreamSn}`, err.displayMessage || err);
                return false;
            }
        },

        // 新增批量刪除 upstream 的方法
        async batchClearUpstream(snList) {
            try {
                const data = await request(`/api/characters/upstream`, {
                    method: "DELETE",
                    body: JSON.stringify({ sn_list: snList })
                });
                
                if (data.success) {
                    console.log(`✅ 成功清除 ${data.success_count} 個角色的 upstream`);
                    return true;
                } else {
                    console.warn(`⚠️ 批量清除失敗: ${data.message}`);
                    return false;
                }
            } catch (err) {
                console.warn(`批量清除 upstream 失敗`, err.displayMessage || err);
                return false;
            }
        }
     }));
});