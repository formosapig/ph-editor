window.addEventListener('DOMContentLoaded', () => {
  const { profiles, scenarios, backstages } = window.rawData;
  
  const app = PetiteVue.reactive({
  //createApp({
    profiles,
    scenarios,
    backstages,
    editingScene: null,
    currentActors: [],

    //async fetchData() {
    //  // 這裡模擬從 Flask 獲取資料
    //  const res = await fetch('/api/ccm/read-data');
    //  const data = await res.json();
    //  this.profiles = data.profiles;
    //  this.scenarios = data.scenarios.sort((a,b) => a.year - b.year);
    //  this.backstages = data.backstages;
    //},

    getBS(pid, sid) {
      return this.backstages.find(b => b.profile_id === pid && b.scenario_id === sid);
    },

    openEditor(sid) {
      this.editingScene = this.scenarios.find(s => s.id === sid);
      // 找出該場景所有參與的女角
      const pids = this.backstages.filter(b => b.scenario_id === sid).map(b => b.profile_id);
      this.currentActors = this.profiles.filter(p => pids.includes(p.id));
    }
  });
  
  // inital petiteVue
  PetiteVue.createApp(app).mount('[v-scope]');

});
