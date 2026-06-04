import { request } from './request.js';

document.addEventListener('alpine:init', () => {
    Alpine.data('epochManager', () => ({
        selectedProfile: '',
        profile_options: window.INITIAL_PROFILES || [],
        characters: [],
        epochChain: [],
        draggedChar: null,

        init() {
            const firstValid = this.profile_options.find(opt => !opt.disabled && opt.id);
            if (firstValid) {
                this.selectedProfile = firstValid.id;
                this.fetchCharacters(); // 初始化時呼叫
            }

            // 若你想在 UI 上做一個切換器，記得監聽變化：
            this.$watch('selectedProfile', (value) => {
                this.fetchCharacters(); // 當選中的 Profile 改變時，自動重新抓取
            });
        },

        async fetchCharacters() {
            if (!this.selectedProfile) return;

            console.log("正在獲取 Profile 的角色:", this.selectedProfile);
            
            try {
                // 使用你封裝好的 request 函式
                const url = `/api/characters?profile_id=${encodeURIComponent(this.selectedProfile)}`;
                const response = await request(url);
                
                // 成功處理
                this.characters = response.results;
                console.log("角色載入完成:", this.characters);
                
            } catch (err) {
                // 錯誤處理：因為 request 函式在 !res.ok 時會 throw data
                // 所以這裡的 err 已經是你處理過的物件，包含 displayMessage
                console.error("獲取角色失敗:", err);
                
                // 這裡可以呼叫你前端統一的報錯介面，例如：
                // alert(err.displayMessage || "發生未知的錯誤");
            }
        },
        
        handleDragStart(event, char) {
            this.draggedChar = char;
            // 設定傳輸資料（標準做法）
            event.dataTransfer.setData('text/plain', JSON.stringify(char));
        },

        handleDrop(event, zoneColor) {
            if (!this.draggedChar) return;

            if (zoneColor === 'blue') {
                // 避免重複添加
                if (!this.epochChain.find(c => c.sn === this.draggedChar.sn)) {
                    this.epochChain.push(this.draggedChar);
                }
            } else if (zoneColor === 'red') {
                alert('回溯功能啟動：' + this.draggedChar.file_id);
            }
            
            this.draggedChar = null;
        },

        onScroll(event) {
            const { scrollTop, scrollHeight, clientHeight } = event.target;
            if (scrollTop + clientHeight >= scrollHeight - 5) {
                console.log("觸發無限滾動 - 載入更多角色");
            }
        }
     }));
});