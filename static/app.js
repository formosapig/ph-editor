const pathInput = document.getElementById('pathInput');
const scanBtn = document.getElementById('scanBtn');
const gallery = document.getElementById('gallery');

const folderBtn = document.getElementById('folderBtn');
const sortBtn = document.getElementById('sortBtn');
const filterBtn = document.getElementById('filterBtn');
const editBtn = document.getElementById('editBtn');
const compareBtn = document.getElementById('compareBtn');
const deleteBtn = document.getElementById('deleteBtn');

let currentScanPath = '';
let selectedSet = new Set();
let totalFilesCount = 0; // 全域變數，記錄總檔案數
let allImages = [];

// 將掃描邏輯封裝成函式
async function scan(path) {
  if (!path) {
    alert('請輸入路徑');
    return;
  }
  localStorage.setItem('scanPath', path);
  try {
    const res = await fetch('/scan', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ path })
    });
    if (!res.ok) {
      const err = await res.json();
      alert('掃描錯誤: ' + (err.error || res.statusText));
      return;
    }
    const data = await res.json();
    if (!data.images || data.images.length === 0) {
      alert('沒有找到 PNG 檔案');
      gallery.innerHTML = '';
      return;
    }
    currentScanPath = path;
    selectedSet.clear();
    updateActionButtons();
	
	// 新存一份完整 images 陣列
	allImages = data.images;
	
    renderGallery(data.images);
	// 更新路徑
	document.getElementById('scanPathText').textContent = `📂 掃描路徑：${path}`;
  } catch (e) {
    alert('網路或伺服器錯誤');
    console.error(e);
  }
}

// 頁面載入時從後端取得掃描路徑，並自動掃描
window.addEventListener('DOMContentLoaded', async () => {
  try {
    const res = await fetch('/get_scan_path');
    if (res.ok) {
      const data = await res.json();
      if (data.scanPath) {
        currentScanPath = data.scanPath;
        await scan(currentScanPath);
      }
    }
  } catch (e) {
    console.error('取得掃描路徑失敗', e);
  }
});

function adjustGalleryTop() {
  const actionButtons = document.getElementById('actionButtons');
  const gallery = document.getElementById('gallery');
  if (actionButtons && gallery) {
    const height = actionButtons.offsetHeight;
    gallery.style.top = height + 'px';
  }
}

window.addEventListener('load', adjustGalleryTop);
window.addEventListener('resize', adjustGalleryTop);

// folder 按鈕點擊改路徑並自動掃描
folderBtn.addEventListener('click', () => {
  const newPath = prompt('請輸入掃描資料夾絕對路徑：', currentScanPath || '');
  if (newPath && newPath.trim() !== '' && newPath.trim() !== currentScanPath) {
    scan(newPath.trim());
  }
});

let sortAscending = true; // 初始為正序

sortBtn.addEventListener('click', () => {
  const sorted = [...allImages].sort((a, b) => {
    const nameA = a.profile_name || '';
    const nameB = b.profile_name || '';

    if (nameA === '' && nameB === '') return 0;
    // 空白不特別往前或往後丟.
	//if (nameA === '') return 1;
    //if (nameB === '') return -1;

    const cmp = nameA.localeCompare(nameB, undefined, { sensitivity: 'base' });
    return sortAscending ? cmp : -cmp;
  });

  renderGallery(sorted);

  sortAscending = !sortAscending; // 切換排序方向
});

// filter 按鈕
filterBtn.addEventListener('click', () => {
  const keyword = prompt('請輸入篩選關鍵字（空白顯示全部）：', '');
  if (keyword === null) return;  // 使用者按取消就不動作
  const trimmed = keyword.trim();
  filterGallery(trimmed);  // 呼叫之前提到的 filterGallery 函式
});

editBtn.addEventListener('click', () => {
  if (selectedSet.size === 1) {
    const characterId = Array.from(selectedSet)[0];
    const url = `/edit?character_id=${encodeURIComponent(characterId)}`;
    window.open(url, 'editWindow');
  }
});

// 比較按鈕點擊跳轉，前提是2個以上選
compareBtn.addEventListener('click', () => {
  if (selectedSet.size >= 2) {
    const files = Array.from(selectedSet).map(f => encodeURIComponent(f)).join(',');
    window.location.href = `/compare?files=${files}`;
  }
});

// 刪除按扭呼叫刪除, 選了一個以上即可觸發
deleteBtn.addEventListener('click', () => {
  if (selectedSet.size === 0) return;
  if (!confirm('確定要刪除選取的圖片？')) return;

  const filenames = Array.from(selectedSet).map(name => name + '.png');

  fetch('/delete_files', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filenames })
  })
  .then(res => res.json())
  .then(data => {
    const results = data.results || [];
    results.forEach(r => {
      if (r.status === 'success') {
        const thumb = document.querySelector(`.thumb-container[data-name="${r.filename.replace('.png', '')}"]`);
        if (thumb) thumb.remove();
        selectedSet.delete(r.filename.replace('.png', ''));
      }
    });
    updateActionButtons();
  })
  .catch(err => {
    alert('刪除失敗');
    console.error(err);
  });
});


// 更新按鈕狀態
function updateActionButtons() {
  editBtn.disabled = selectedSet.size !== 1;
  compareBtn.disabled = selectedSet.size < 2;
  deleteBtn.disabled = selectedSet.size === 0;
  
  // 更新總檔案數（理論上 renderGallery 時更新）
  // 這邊用 totalFilesCount
  const selectionCountSpan = document.getElementById('selectionCount');
  selectionCountSpan.textContent = `選擇: ${selectedSet.size} / 總數: ${totalFilesCount}`;
}

// 新增一個篩選函式，從 allImages 篩選
function filterGallery(keyword) {
  const gallery = document.getElementById('gallery');
  const lowerKeyword = keyword.toLowerCase();

  const filtered = !keyword
    ? allImages
    : allImages.filter(name => name.toLowerCase().includes(lowerKeyword));

  renderGallery(filtered);

  requestAnimationFrame(() => {
    gallery.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// 渲染圖片列表（含勾選功能）
function renderGallery(images) {
  gallery.innerHTML = '';
  totalFilesCount = images.length;

  // 在现有代码的 renderGallery 函数内添加：
  gallery.addEventListener('click', (e) => {
    const isBlankClick = e.target === gallery;
    const isCtrlPressed = e.ctrlKey || e.metaKey; // 兼容 Mac 的 Command 键

    if (isCtrlPressed || isBlankClick) {
      // 空白处：取消全选 | Ctrl+图片：全选, 再點還是全選
      const shouldSelectAll = !isBlankClick;// && selectedSet.size < totalFilesCount;
    
      document.querySelectorAll('.thumb-container').forEach(el => {
        const name = el.dataset.name;
        el.classList.toggle('selected', shouldSelectAll);
      });
    
      selectedSet = shouldSelectAll ? new Set(allImages) : new Set();
      updateActionButtons();
    }
  });
  
  images.forEach(item => {
    //const baseName = imgName.replace(/^thumb_/, '').replace(/\.[^.]+$/, '');
	const imgName = item.thumb; // thumb_*.jpg
	const baseName = item.id;   // character_id
	const profileName = item.profile_name || '';
  
    const container = document.createElement('div');
    container.className = 'thumb-container';
	container.dataset.name = baseName;

    // 勾選標示
    const checkmark = document.createElement('div');
    checkmark.className = 'checkmark';
    checkmark.textContent = '✅';
    container.appendChild(checkmark);

    const thumbWrapper = document.createElement('div');
	thumbWrapper.className = 'thumb-wrapper';
	thumbWrapper.addEventListener('click', (e) => {
      e.stopPropagation(); // 避免冒泡重複觸發
      container.click();   // 轉給 thumb-container 處理
    });

	const img = document.createElement('img');
	img.src = `/cache/${imgName}`;
	img.className = 'thumb';
	img.alt = baseName;
	img.width = 252;
	img.height = 352;
	img.draggable = false;

	thumbWrapper.appendChild(img);

	if (profileName) {
	  const badge = document.createElement('div');
	  badge.className = 'profile-badge';
	  badge.textContent = profileName;
	  thumbWrapper.appendChild(badge);
	}

	container.appendChild(thumbWrapper);

    // ✅ 顯示檔名（補回來）
    const filenameLabel = document.createElement('div');
    filenameLabel.className = 'filename-label';
    filenameLabel.textContent = baseName;
    container.appendChild(filenameLabel);

    // 點擊圖片切換選中
    container.addEventListener('click', () => {
      if (selectedSet.has(baseName)) {
        selectedSet.delete(baseName);
        container.classList.remove('selected');
      } else {
        selectedSet.add(baseName);
        container.classList.add('selected');
      }
      updateActionButtons();
    });

    gallery.appendChild(container);
  });

  updateActionButtons();
}
