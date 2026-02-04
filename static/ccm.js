window.addEventListener('DOMContentLoaded', () => {
  const { profiles, scenarios, metadatas, tag_styles, tag_list, profile_group } = window.rawData;

  const app = {
	profiles,
    scenarios,
    metadatas,
	tag_styles,
	tag_list,
    profile_group,
	
    hoveredScenarioId: null,
	hoveredTitle: '',
	hoveredYear: '',
	hoveredPilot: '',
	isLocked: false,
	
	// 私有輔助方法：統一處理資料更新與清空
    _updateHoverState(scId = null) {
      const sc = this.scenarios[scId];
      this.hoveredScenarioId = scId;
      this.hoveredTitle = sc ? sc.title : (scId ? '未命名事件' : '');
      this.hoveredYear  = sc ? sc.year  : '';
      this.hoveredPilot = sc ? sc.pilot : (scId ? '暫無劇情簡介' : '');
    },

	handleMouseEnter(scId) {
	  if (this.isLocked) return;
	  this._updateHoverState(scId);
	},

	handleMouseLeave() {
	  if (this.isLocked) return;
	  this._updateHoverState(null);
	},

	toggleLock(scId) {
	  // 如果點擊已鎖定的同一個對象 -> 解鎖並清空
	  if (this.isLocked && this.hoveredScenarioId === scId) {
		this.isLocked = false;
		this._updateHoverState(null);
	  } else {
		// 否則 -> 直接鎖定
		this.isLocked = true;
		this._updateHoverState(scId);
	  }
	},
	  
    getBackstagesByScenario(scId) {
      // 1. 找出「所有」這場戲的 metadata (可能有巫子的、也有佐藤的)
      const matchedMetas = Object.values(this.metadatas || {}).filter(
        meta => String(meta["!scenario_id"]) === String(scId)
      );

      // 2. 使用 flatMap 直接攤平並回傳新物件陣列
      return matchedMetas.flatMap(meta => {
        const currentProfileId = meta["!profile_id"];
        const backstage = meta.backstage || {};
	    return {
	      tag_id: backstage["!tag_id"],
	      profile_id: currentProfileId
		
        };
      });
	},		

    // 輔助函式：透過 tag_id 取得完整的 tag 物件與樣式
    getTagInfo(tagId) {
		//console.error(tagId)
      const tag = this.tag_list.find(t => t.id === tagId);
      if (!tag) return null;
      const style = this.tag_styles[tag.type] || {};
      return { ...tag, style };
    },

    // 判斷該 event-box 內的 backstage 資訊是否屬於目前這一橫行的 profile
    isCurrentProfile(backstageItem, currentProfileId) {
      return backstageItem.profile_id === currentProfileId;
    },

    openEditor(fileId, canEdit) {
      if (!canEdit) return;
      console.log("正在開啟編輯器:", fileId);
      // window.open('editor_url/' + fileId);
    },

    // 處理點擊標籤開啟檔案
    handleTagClick(backstageItem, currentProfileId) {
      // 只有當這個標籤屬於目前橫行的 profile 時才執行
      if (backstageItem.profile_id === currentProfileId) {
        const fileId = backstageItem.file_id;
        if (fileId) {
          console.log(`開啟角色 ${currentProfileId} 的檔案: ${fileId}`);
          // 這裡接你的 API 或跳轉連結
          // window.open('https://your-edit-url.com/' + fileId);
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
      const groups = profile_group || [];
      return Object.values(profiles).sort((a, b) => {
        const gA = groups.find(g => g.name.zh === a.group) || { order: 999 };
        const gB = groups.find(g => g.name.zh === b.group) || { order: 999 };
        if (gA.order !== gB.order) return gA.order - gB.order;
        return a.born - b.born;
      }).map(p => {
        const g = groups.find(g => g.name.zh === p.group) || {};
        return {
          ...p,
          groupColor: g.color || '#666',
          groupBg: 'rgba(255,255,255,0.02)'
        };
      });
    },

    getScenariosByYearAndProfile(pId, year) {
      const results = [];
      const yearScs = Object.values(scenarios).filter(s => s.year === year);
      
      yearScs.forEach(sc => {
        const sid = sc["!id"];
        const hasJoined = Object.values(metadatas).some(bs => 
          bs["!profile_id"] === pId && bs["!scenario_id"] === sid
        );

        if (hasJoined) {
          const actors = Object.keys(metadatas).filter(k => 
            metadatas[k]["!scenario_id"] === sid
          );
          results.push({ id: sid, title: sc.title, actors });
        }
      });
      return results;
    },
	
	// 取得當前事件方塊應套用的主題色
	getScenarioStyle(scId, profileId) {
	  // 1. 找到該事件中，屬於當前角色的第一個後台資料
	  const backstages = this.getBackstagesByScenario(scId);
	  const primaryBG = backstages.find(bg => bg.profile_id === profileId && bg.tag_id);
	  
	  // 1. 預設顏色（找不到資料時顯示的顏色，例如原本的深灰色）
      const defaultBorderColor = '#555'; 
      //const defaultBackground = 'rgba(255, 255, 255, 0.03)';
  
      if (scId == 20) { // profileId == 13) {
		  console.log(backstages);
		  console.log(primaryBG);
	  }
  
	  if (primaryBG) {
		const tagInfo = this.getTagInfo(primaryBG.tag_id);
		if (tagInfo && tagInfo.style) {
		  return {
			// 設定左邊框為標籤主色
			borderColor: tagInfo.style.color,
			// 設定一個極淡的背景色（維持你原本的透明質感，但帶一點標籤色調）
			//background: tagInfo.style.background//
			//background: `linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), ${tagInfo.style.background}`
			//background: `linear-gradient(50deg, ${tagInfo.style.background} 0%, rgba(255, 255, 255, 0.03) 100%)`
		  };
		}
	  }
	  
	  return {
		borderLeftColor: defaultBorderColor
	  }; // 若沒找到則回傳空物件，套用 CSS 預設值
	},
	
	// 取得當前事件方塊應套用的主題色
	getScenarioTitleStyle(scId, profileId) {
	  // 1. 找到該事件中，屬於當前角色的第一個後台資料
	  const backstages = this.getBackstagesByScenario(scId);
	  const primaryBG = backstages.find(bg => bg.profile_id === profileId && bg.tag_id);
	  
	  if (primaryBG) {
		const tagInfo = this.getTagInfo(primaryBG.tag_id);
		if (tagInfo && tagInfo.style) {
		  return {
			color: tagInfo.style.color  
			// 設定左邊框為標籤主色
			//borderColor: tagInfo.style.color,
			// 設定一個極淡的背景色（維持你原本的透明質感，但帶一點標籤色調）
			//background: tagInfo.style.background//
			//background: `linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), ${tagInfo.style.background}`
			//background: `linear-gradient(50deg, ${tagInfo.style.background} 0%, rgba(255, 255, 255, 0.03) 100%)`
		  };
		}
	  }
	  return {}; // 若沒找到則回傳空物件，套用 CSS 預設值
	}
  };

  PetiteVue.createApp(app).mount('[v-scope]');
});