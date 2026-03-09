import { request } from './request.js';

document.addEventListener('alpine:init', () => {
    Alpine.data('epochManager', () => ({
        selectedProfile: '',
        profile_options: [
            { id: 1, name: '存檔 A' },
            { id: 2, name: '存檔 B' }
        ],
        characters: [],
        epochChain: [],
        draggedChar: null,

        init() {
            console.log("Epoch Manager 啟動");
            // 模擬初始抓取資料
            this.fetchCharacters();
        },

        fetchCharacters() {
            console.log("正在獲取 Profile 的角色:", this.selectedProfile);
            // 這裡模擬從 Flask API 獲取資料
            // 範例資料：
            this.characters = [
                { sn: 1, file_id: 'C001', parent_sn: null },
                { sn: 2, file_id: 'C002', parent_sn: 1 },
                { sn: 3, file_id: 'C003', parent_sn: null }
            ];
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