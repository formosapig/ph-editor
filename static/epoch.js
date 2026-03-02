function EpochManager() {
    return {
        profile_options: window.profile_options || [], // 從 Flask 傳入
        selectedProfile: null,
        characters: [],
        epochChain: [], // 存放藍區中的角色鏈
        draggedItem: null,

        init() {
            console.log('Epoch Manager Ready');
        },

        async fetchCharacters() {
            // 這裡實作 AJAX 向 Flask 拿資料
            // const resp = await fetch(`/api/chars/${this.selectedProfile}`);
            // this.characters = await resp.json();
        },

        handleDragStart(e, char) {
            this.draggedItem = char;
            e.dataTransfer.setData('text/plain', char.sn);
        },

        handleDrop(e, zone) {
            const char = this.draggedItem;
            if (!char) return;

            if (zone === 'blue') {
                // 規則：有父代不能直接拉進藍區起點/中繼（除非是邏輯上的子代追加）
                if (char.parent_sn && this.epochChain.length === 0) {
                    alert("此角色非始祖，不能作為歲月起點！");
                    return;
                }
                this.epochChain.push(char);
            } 
            
            else if (zone === 'red') {
                // 規則：作為結尾，觸發回溯（此處示範邏輯，實際可能需 call API）
                this.traceBackParent(char);
            }
        },

        traceBackParent(char) {
            // 假設這裡做一個遞迴或請求，將所有祖先找出來並更新到 epochChain
            // 邏輯：[祖父, 父親, 自己]
            console.log("正在從紅區回溯父代...", char.sn);
            // 範例更新：
            // this.epochChain = fetchedAncestors;
        }
    }
}