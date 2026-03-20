import { request } from './request.js'

window.addEventListener('DOMContentLoaded', () => {
    const { profiles, scenarios, metadatas, profile_group } = window.rawData;

    const app = PetiteVue.reactive({
        profiles,
        scenarios,
        metadatas,
        profile_group,

        hoveredScenarioId: null,
        hoveredScene: '',
        hoveredYear: '',
        hoveredPlot: '',
        basePlot: '',
        hoveredCharacters: [],
        isLocked: false,
        // 預設全部收縮...
        collapsedGroups: profile_group.map(g => g.id), //[], //
        version: 0,


        get sortedGroups() {
            return this.profile_group
                .filter(group => {
                    return true;
                })
                .sort((a, b) => a.order - b.order);		
        },


        toggleGroup(groupId) {
            const index = this.collapsedGroups.indexOf(groupId);
            if (index > -1) {
                this.collapsedGroups.splice(index, 1); // 移除 = 展開
            } else {
                this.collapsedGroups.push(groupId); // 加入 = 縮起
            }
        },

        isCollapsed(groupId) {
            return this.collapsedGroups.includes(groupId);
        },

        // 輔助方法：根據 group 過濾 profile
        getProfilesByGroup(groupId) {
            return this.sortedProfiles.filter(p => p.group_id === groupId);
        },

        _updateHoverState(scId = null) {
            const sc = this.scenarios[scId];
            this.hoveredScenarioId = scId;
            this.hoveredScene = sc ? sc.scene : (scId ? '未命名事件' : '');
            this.hoveredYear = sc 
            ? sc.year + ({"spring":"🌸","summer":"☀️","autumn":"🍁","winter":"❄️"}[sc.season?.toLowerCase()] || '') 
            : '';

            //this.hoveredYear = sc 
            //? sc.year + ({"spring":"🌸","summer":"☀️","autumn":"🍁","winter":"❄️"}[sc.season?.toLowerCase()] ? ' ' + {"spring":"🌸","summer":"☀️","autumn":"🍁","winter":"❄️"}[sc.season?.toLowerCase()] : '') 
            //: '';
            // 1. 處理基礎劇情
            this.basePlot = sc ? sc.plot : (scId ? '暫無劇情簡介' : '');

            // 2. 準備角色清單 (不再拼接字串)
            this.hoveredCharacters = [];
            if (scId && this.metadatas) {
                this.hoveredCharacters = Object.entries(this.metadatas)
                .filter(([_, meta]) => String(meta["!scenario_id"]) === String(scId))
                .map(([sn, meta]) => {
                    const bg = meta.backstage || {};
                    const profile = this.profiles ? this.profiles[meta["!profile_id"]] : null;
                    //const tagInfo = this.getTagInfo(bg["!tag_id"]);

                    // 預先計算好所有顯示邏輯
                    return {
                        sn: sn,
                        //fileId: sn,
                        name: profile ? profile.name : "未知角色",
                        title: bg.title ?? "",
                        detail: bg.detail ?? "",
                        avatar: `/api/characters/${encodeURIComponent(sn)}/thumbnail`,
                        age: bg.age ?? null, // (profile?.born && sc?.year) ? (parseInt(sc.year) - parseInt(profile.born || 0)) : null,
                        // 標籤樣式物件
                        tag: (bg.tag) ? {
                            name: bg.tag,
                            style: {
                                background: bg.background || '#aaa',
                                color: bg.color || '#555',
                                borderColor: bg.color || '#555'
                            }
                        } : null,
                        persona: bg.persona || null,
                        pColor: bg["!persona_code"] || '#B87333',
                        shadow: bg.shadow || null,
                        sColor: bg["!shadow_code"] || '#43AD2B',
                        //notes: bg.notes || ''
                    };
                });
            }
        }, // _updateHoverState

        getBadgeStyle(color) {
            if (!color) return {};
            return {
                background: `${color}22`,
                color: color,
                border: `1px solid ${color};`
            };
        },

        // 在 petite-vue 的 app 物件內
        openFile(sn) {
            if (!sn) {
                alert('無效的檔案 ID');
                return;
            }
            const windowName = `edit_file_${sn}`;
            const url = `/edit/${encodeURIComponent(sn)}`;
            console.log(`開啟編輯: ${sn}`);
            window.open(url, windowName);
        },


        handleMouseEnter(scId) {
        //this.hoveredScenarioId = scId;
        if (this.isLocked) return;
        this._updateHoverState(scId);
        },

        handleMouseLeave() {
        //this.hoveredScenarioId = null;
        if (this.isLocked) return;
        this._updateHoverState(null);
        },

        toggleLock(scId) {
        // 如果點擊已鎖定的同一個對象 -> 解鎖並清空
        if (this.isLocked && this.hoveredScenarioId === scId) {
            this.isLocked = false;
            //this._updateHoverState(null);
            this.hoveredScenarioId = null;
        } else {
            // 否則 -> 直接鎖定
            this.isLocked = true;
            this.hoveredScenarioId = scId;
            this._updateHoverState(scId);
        }
        },
        
        toggleLockOnHeader() {
        this.isLocked = !this.isLocked;
        },
        
        onTooltipMouseLeave() {
        if (!this.isLocked) {
            this._updateHoverState(null);
        }
        },
    
        getBackstagesByScenario(scId) {
            const matchedMetas = Object.entries(this.metadatas || {}).filter(
                ([sn, meta]) => meta["!scenario_id"] === scId
            ).flatMap(([sn, meta]) => {
                const backstage = meta.backstage || {};
                return {
                    sn: sn,
                    title: backstage["title"],
                    tag_id: backstage["!tag_id"],
                    profile_id: meta["!profile_id"],
                    color: backstage["color"] || '#555',
                    background: backstage["background"] || '#aaa'
                };
            });
            return matchedMetas;
        },

        // 判斷該 event-box 內的 backstage 資訊是否屬於目前這一橫行的 profile
        isCurrentProfile(backstageItem, currentProfileId) {
            return backstageItem.profile_id === currentProfileId;
        },

        // 處理點擊標籤開啟檔案
        handleTagClick(backstageItem, currentProfileId) {
        console.log("handleTagClick:", backstageItem);		
            
        // 只有當這個標籤屬於目前橫行的 profile 時才執行
        if (backstageItem.profile_id === currentProfileId) {
            const fileId = backstageItem.file_id;
            if (fileId) {
            // 情況 A：已有 metadata file_id，開啟編輯
            const windowName = `edit_file_${fileId}`;
            const url = `/edit?file_id=${encodeURIComponent(fileId)}`;
            console.log(`開啟編輯: ${fileId}`);
            window.open(url, windowName);
            } else {
            alert('該標籤未設定 file_id');
            }
        }
        },
    
        get sortedYears() {
        const years = Object.values(scenarios).map(s => s.year);
        return [...new Set(years)].sort((a, b) => a - b);
        },

        get sortedProfiles() {
            const groups = this.profile_group || [];
            // 將 Object 轉為 Array
            return Object.values(this.profiles).sort((a, b) => {
                // 1. 先用 !group_id 找對應的 group 定義
                const gA = groups.find(g => g.id === a['!group_id']) || { order: 999 };
                const gB = groups.find(g => g.id === b['!group_id']) || { order: 999 };

                // 2. 比較 Group 的 order
                if (gA.order !== gB.order) return gA.order - gB.order;

                // 3. 同組內按出生年份排序
                return (a.born || 0) - (b.born || 0);
            }).map(p => {
                // 注入顏色等樣式資訊，方便模板使用
                const g = groups.find(g => g.id === p['!group_id']) || {};
                return {
                    ...p,
                    group_id: p['!group_id'], // 簡化一個 key 給模板用
                    groupColor: g.color || '#666',
                    groupBg: 'rgba(255,255,255,0.02)' // 維持你喜歡的低調底色
                };
            });
        },

        getScenariosByYearAndProfile(pId, year) {
            const results = [];
            const yearScs = Object.values(this.scenarios).filter(s => s.year === year);
        
            yearScs.forEach(sc => {
                const sid = sc["!id"];
                const hasJoined = Object.values(this.metadatas).some(bs => 
                    bs["!profile_id"] === pId && bs["!scenario_id"] === sid
                );

                if (hasJoined) {
                    const actors = Object.keys(this.metadatas).filter(k => 
                        metadatas[k]["!scenario_id"] === sid
                    );
                    results.push({ id: sid, scene: sc.scene, actors });
                }
            });
            return results;
        },
	
        // 取得當前事件方塊應套用的主題色
        getScenarioStyle(scId, profileId) {
            const backstages = this.getBackstagesByScenario(scId);
            const primaryBG = backstages.find(bg => bg.profile_id === profileId && bg.color);
            return {
                borderColor: (primaryBG && primaryBG.color) || '#555'
            };
        },
	
        async reloadData() {
            console.log("正在從伺服器同步資料...");
            try {
                const url = "/ccm/reload";
                const newData = await request(url);

                this.profiles = newData.profiles;
                this.scenarios = newData.scenarios;
                this.metadatas = newData.metadatas;
                this.profile_group = newData.profile_group;
                
                // plot
                if (this.hoveredScenarioId) {
                    this._updateHoverState(this.hoveredScenarioId);
                }
                
                this.version++;
                console.log("資料同步完成！");
            } catch (err) {
                console.error("網路請求出錯:", err.displayMessage || '系統錯誤');
            }
        },
	
    }); // const app = PetiteVue.reactive({

    // 接收 editor 資料
    const bc = new BroadcastChannel('edit_file_sync_bus');
    bc.onmessage = (e) => {
        const {file_id, action} = e.data;
        if (action === "updated") {
            // 不管改了什麼, 預設 reload
            app.reloadData();
        }
    };

    PetiteVue.createApp(app).mount('[v-scope]');
});