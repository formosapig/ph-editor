import { request } from './request.js'

document.addEventListener('alpine:init', () => {
    Alpine.data('ccmApp', (params) => ({

//function ccmApp() {
//    return {
        // 資料屬性
        profiles: params.profiles,
        scenarios: params.scenarios,
        metadatas: params.metadatas,
        profile_group: params.profile_group,
        
        // UI 狀態
        hoveredScenarioId: null,
        hoveredScene: '',
        hoveredYear: '',
        hoveredPlot: '',
        basePlot: '',
        hoveredCharacters: [],
        isLocked: false,
        collapsedGroups: [],
        version: 0,
        
        // 初始化
        init() {
            // 從全域變數載入資料
            //if (window.rawData) {
            //    this.profiles = window.rawData.profiles || {};
            //    this.scenarios = window.rawData.scenarios || {};
            //    this.metadatas = window.rawData.metadatas || {};
            //    this.profile_group = window.rawData.profile_group || [];
            //    this.collapsedGroups = this.profile_group.map(g => g.id);
            //}
            this.collapsedGroups = this.profile_group.map(g => g.id);
            
            // 設定 BroadcastChannel 監聽
            const bc = new BroadcastChannel('edit_file_sync_bus');
            bc.onmessage = (e) => {
                const { file_id, action } = e.data;
                if (action === "updated") {
                    this.reloadData();
                }
            };
        },
        
        // 計算屬性
        get sortedGroups() {
            return this.profile_group
                .filter(group => true)
                .sort((a, b) => a.order - b.order);
        },
        
        get sortedYears() {
            if (!this.scenarios) return [];
            const years = Object.values(this.scenarios).map(s => s.year);
            return [...new Set(years)].sort((a, b) => a - b);
        },
        
        get sortedProfiles() {
            const groups = this.profile_group || [];
            return Object.values(this.profiles).sort((a, b) => {
                const gA = groups.find(g => g.id === a['!group_id']) || { order: 999 };
                const gB = groups.find(g => g.id === b['!group_id']) || { order: 999 };
                if (gA.order !== gB.order) return gA.order - gB.order;
                return (a.born || 0) - (b.born || 0);
            }).map(p => {
                const g = groups.find(g => g.id === p['!group_id']) || {};
                return {
                    ...p,
                    group_id: p['!group_id'],
                    groupColor: g.color || '#666',
                    groupBg: 'rgba(255,255,255,0.02)'
                };
            });
        },
        
        // 群組方法
        toggleGroup(groupId) {
            const index = this.collapsedGroups.indexOf(groupId);
            if (index > -1) {
                this.collapsedGroups.splice(index, 1);
            } else {
                this.collapsedGroups.push(groupId);
            }
        },
        
        isCollapsed(groupId) {
            return this.collapsedGroups.includes(groupId);
        },
        
        getProfilesByGroup(groupId) {
            return this.sortedProfiles.filter(p => p.group_id === groupId);
        },
        
        // 場景相關方法
        getScenariosByYearAndProfile(pId, year) {
            const results = [];
            if (!this.scenarios || !this.metadatas) return results;
            
            const yearScs = Object.values(this.scenarios).filter(s => s.year === year);
            
            yearScs.forEach(sc => {
                const sid = sc["!id"];
                const hasJoined = Object.values(this.metadatas).some(bs => 
                    bs["!profile_id"] === pId && bs["!scenario_id"] === sid
                );
                
                if (hasJoined) {
                    const actors = Object.keys(this.metadatas).filter(k => 
                        this.metadatas[k]["!scenario_id"] === sid
                    );
                    results.push({ id: sid, scene: sc.scene, actors });
                }
            });
            return results;
        },
        
        getBackstagesByScenario(scId, currentProfileId = null, maxItems = 5) {
            if (!this.metadatas) return [];
            
            const matchedMetas = Object.entries(this.metadatas || {})
                .filter(([sn, meta]) => meta["!scenario_id"] === scId)
                .map(([sn, meta]) => {
                    const backstage = meta.backstage || {};
                    return {
                        sn: sn,
                        title: backstage["title"],
                        tag_id: backstage["!tag_id"],
                        profile_id: meta["!profile_id"],
                        scenario_color: backstage["scenario_color"],
                        color: backstage["color"] || '#555',
                        background: '#333'
                    };
                });

            // 排序：自己的排最前面
            if (currentProfileId) {
                matchedMetas.sort((a, b) => {
                    if (a.profile_id === currentProfileId) return -1;
                    if (b.profile_id === currentProfileId) return 1;
                    return 0;
                });
            }
    
            // 限制顯示數量
            return matchedMetas.slice(0, maxItems);

            //return matchedMetas;
        },
        
        getScenarioStyle(scId, profileId) {
            const backstages = this.getBackstagesByScenario(scId);
            let fallback = null;
            
            for (let i = 0; i < backstages.length; i++) {
                const bg = backstages[i];
                if (bg.profile_id !== profileId) continue;
                
                if (bg.scenario_color) return { borderColor: bg.scenario_color };
                if (!fallback && bg.color) fallback = bg.color;
            }
            
            return { borderColor: fallback || '#555' };
        },
        
        // 更新 hover 狀態
        _updateHoverState(scId = null, currentProfileId = null) {
            const sc = this.scenarios[scId];
            this.hoveredScenarioId = scId;
            this.hoveredScene = sc ? sc.scene : (scId ? '未命名事件' : '');
            this.hoveredYear = sc 
                ? sc.year + ({"spring":"🌸","summer":"☀️","autumn":"🍁","winter":"❄️"}[sc.season?.toLowerCase()] || '') 
                : '';
            
            this.basePlot = sc ? sc.plot : (scId ? '暫無劇情簡介' : '');
            
            this.hoveredCharacters = [];
            if (scId && this.metadatas) {
                this.hoveredCharacters = Object.entries(this.metadatas)
                    .filter(([_, meta]) => String(meta["!scenario_id"]) === String(scId))
                    .map(([sn, meta]) => {
                        const bg = meta.backstage || {};
                        const profile = this.profiles ? this.profiles[meta["!profile_id"]] : null;
                        
                        return {
                            sn: sn,
                            name: profile ? profile.name : "未知角色",
                            title: bg.title ?? "",
                            detail: bg.detail ?? "",
                            avatar: `/api/character/${encodeURIComponent(sn)}/thumbnail`,
                            me: meta["!profile_id"] === currentProfileId,
                            tag_id: bg["!tag_id"] ?? 9999,
                            age: bg.age ?? null,
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
                            sColor: bg["!shadow_code"] || '#43AD2B'
                        };
                    }
                
                )
                .sort((a, b) => {
                    //if (currentProfileId) {                    
                    //    const aIsSelf = a.profile_id === currentProfileId;
                    //    const bIsSelf = b.profile_id === currentProfileId;
                        if (a.me !== b.me) {
                            return a.me ? -1 : 1;
                        }
                    //}
                    if (a.tag_id !== b.tag_id) 
                        return a.tag_id - b.tag_id;
                    else
                        return a.age - b.age;
                });
            }
        },
        
        // 事件處理
        handleMouseEnter(scId, currentProfileId) {
            if (this.isLocked) return;
            this._updateHoverState(scId, currentProfileId);
        },
        
        handleMouseLeave() {
            if (this.isLocked) return;
            this._updateHoverState(null);
        },
        
        toggleLock(scId, currentProfileId) {
            if (this.isLocked && this.hoveredScenarioId === scId) {
                this.isLocked = false;
                this.hoveredScenarioId = null;
            } else {
                this.isLocked = true;
                this.hoveredScenarioId = scId;
                this._updateHoverState(scId, currentProfileId);
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
        
        // 輔助方法
        getBadgeStyle(color) {
            if (!color) return {};
            return {
                background: `${color}22`,
                color: color,
                border: `1px solid ${color};`
            };
        },
        
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
        
        // 資料重新載入
        async reloadData() {
            console.log("正在從伺服器同步資料...");
            try {
                const url = "/ccm/reload";
                const newData = await request(url);
                
                this.profiles = newData.profiles;
                this.scenarios = newData.scenarios;
                this.metadatas = newData.metadatas;
                this.profile_group = newData.profile_group;
                
                if (this.hoveredScenarioId) {
                    this._updateHoverState(this.hoveredScenarioId);
                }
                
                this.version++;
                console.log("資料同步完成！");
            } catch (err) {
                console.error("網路請求出錯:", err.displayMessage || '系統錯誤');
            }
        }
    }));
});
//     };
// }

// // 註冊到全域
// window.ccmApp = ccmApp;