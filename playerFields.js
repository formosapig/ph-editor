const fields = [

	// ===== 髮 =====

	// -- 後髮 --
	// 注意,0x0016 開始應該是後髮,若選 Set髮,也是從這邊開始寫入.. 第一套 set 髮有 飾品,所以會多 40 bytes... SET 髮佔了 後髮的位置...
	// 但遊戲怎麼判斷 SET 髮還不知道....


	{ offset: 0x0016, name: "後髮", type: "uint32", comment: "對照 hairCode" },
	{ offset: 0x001E, name: "髮色", type: "rgba", scale: 255, comment: "連續 4 個 float, 應該是 R, G, B, 範圍 0 ~ 255, A 的範圍是 0 ~ 100" },
	// 0x0022 G 值 float
	// 0x0026 B 值 float
	// 0x002A A 值 float 沒有界面,無法修改. 預設為 1, 不然透空顏色就不見了.

	{ offset: 0x002E, name: "光澤1色", type: "rgba", scale: 255, comment: "連續 4 個 float, 應該是 R, G, B, 範圍 0 ~ 255, A 的範圍是 0 ~ 100" },
	// 0x0030 G 值 float
	// 0x0036 B 值 float
	// 0x003A A 值 float 沒有界面,無法修改. 預設為 1, 不然透空顏色就不見了.

    { offset: 0x003E, name: "光澤1濃度", type: "float", scale: 5, comment: "非常奇怪,值是 6 -> 12 似乎是乘 5 倍" },

	{ offset: 0x0042, name: "光澤2色", type: "rgba", scale: 255, comment: "連續 4 個 float, 應該是 R, G, B, 範圍 0 ~ 255, A 的範圍是 0 ~ 100" },
	// 0x0046 G 值 float
	// 0x004A B 值 float
	// 0x004E A 值 float 沒有界面,無法修改. 預設為 1.0f, 設為 0 = 透空 = 看不見.

    { offset: 0x0052, name: "光澤2濃度", type: "float", scale: 12.5, comment: "非常奇怪, 這裏是乘 12.5 倍了" },

	// 注意, 當髮型上面有裝飾時, 會多 40bytes, 分別是裝飾的顏色, 裝飾的光澤, 光澤的濃度, 光澤的質感. 若沒有裝飾就沒有這 40 bytes.

	// -- 前髮 -- 雖然在界面上 前髮在最下面, 但資料在讀的時候卻是在這邊, 可能大多數人不設橫髮...

	{ offset: 0x005A, name: "前髮", type: "uint32", comment: "對照 hairCode" },
	{ offset: 0x0062, name: "髮色", type: "rgba", scale: 255, comment: "連續 4 個 float, 應該是 R, G, B, 範圍 0 ~ 255, A 的範圍是 0 ~ 100" },
	// 0x0066 G 值 float
	// 0x006A B 值 float
	// 0x006E A 值 float 沒有界面,無法修改. 預設為 1, 不然透空顏色就不見了.

	{ offset: 0x0072, name: "光澤1色", type: "rgba", scale: 255, comment: "連續 4 個 float, 應該是 R, G, B, 範圍 0 ~ 255, A 的範圍是 0 ~ 100" },
	// 0x0076 G 值 float
	// 0x007A B 值 float
	// 0x007E A 值 float 沒有界面,無法修改. 預設為 1, 不然透空顏色就不見了.

    { offset: 0x0082, name: "光澤1濃度", type: "float", scale: 5, comment: "非常奇怪,值是 6 -> 12 似乎是乘 5 倍" },

	{ offset: 0x0086, name: "光澤2色", type: "rgba", scale: 255, comment: "連續 4 個 float, 應該是 R, G, B, 範圍 0 ~ 255, A 的範圍是 0 ~ 100" },
	// 0x008A G 值 float
	// 0x008E B 值 float
	// 0x0092 A 值 float 沒有界面,無法修改. 預設為 1.0f, 設為 0 = 透空 = 看不見.

    { offset: 0x0096, name: "光澤2濃度", type: "float", scale: 12.5, comment: "非常奇怪, 這裏是乘 12.5 倍了" },

	// 注意, 當髮型上面有裝飾時, 會多 40bytes, 分別是裝飾的顏色, 裝飾的光澤, 光澤的濃度, 光澤的質感. 若沒有裝飾就沒有這 40 bytes.


	// 0x009A 不知道記什麼....


	// -- 在有後髮,且沒有裝飾的情況下, 橫髮開始位置在這 --
	{ offset: 0x009E, name: "橫髮", type: "uint32", comment: "對照 hairCode" },
	{ offset: 0x00A6, name: "髮色", type: "rgba", scale: 255, comment: "連續 4 個 float, 應該是 R, G, B, 範圍 0 ~ 255, A 的範圍是 0 ~ 100" },
	// 0x00AA G 值 float
	// 0x00AE B 值 float
	// 0x00B2 A 值 float 沒有界面,無法修改. 預設為 1, 不然透空顏色就不見了.

	{ offset: 0x00B6, name: "光澤1色", type: "rgba", scale: 255, comment: "連續 4 個 float, 應該是 R, G, B, 範圍 0 ~ 255, A 的範圍是 0 ~ 100" },
	// 0x00BA G 值 float
	// 0x00BE B 值 float
	// 0x00C2 A 值 float 沒有界面,無法修改. 預設為 1, 不然透空顏色就不見了.

    { offset: 0x00C6, name: "光澤1濃度", type: "float", scale: 5, comment: "非常奇怪,值是 6 -> 12 似乎是乘 5 倍" },

	{ offset: 0x00CA, name: "光澤2色", type: "rgba", scale: 255, comment: "連續 4 個 float, 應該是 R, G, B, 範圍 0 ~ 255, A 的範圍是 0 ~ 100" },
	// 0x00CE G 值 float
	// 0x00D2 B 值 float
	// 0x00D6 A 值 float 沒有界面,無法修改. 預設為 1, 不然透空顏色就不見了.

    { offset: 0x00DA, name: "光澤2濃度", type: "float", scale: 12.5, comment: "非常奇怪, 這裏是乘 12.5 倍了" },

	// 注意, 當髮型上面有裝飾時, 會多 40bytes, 分別是裝飾的顏色, 裝飾的光澤, 光澤的濃度, 光澤的質感. 若沒有裝飾就沒有這 40 bytes.

	// ===== 顏 =====

	// -- 全體 -- 選項及相關數值
	{ offset: 0x00E2, name: "輪廓", type: "uint32", comment: "對照輪廓陣列" },
	{ offset: 0x00E6, name: "肌", type: "uint32", comment: "對照臉的肌肉..." },
	{ offset: 0x00EA, name: "皺紋", type: "uint32", comment: "對照臉的陰影..." },
	{ offset: 0x00EE, name: "皺紋深度", type: "float", scale: 100, min: 0, max: 100,  }, // シワの深さ

	// -- 眉 まゆげ -- 眉形選項, 顏色, 光澤強度, 質感...
	{ offset: 0x00F2, name: "眉毛", type: "uint32", comment: "對照眉毛表" },
	{ offset: 0x00FA, name: "眉毛顏色", type: "rgba", comment: "Alpha 可設定" },
	// 0x00FE G 值 float x 255
	// 0x0102 B 值 float x 255
	// 0x0106 A 值 float x 255 ? 有作用.
	{ offset: 0x011A, name: "光澤強度", type: "float", scale: 100 },
	{ offset: 0x011E, name: "光澤質感", type: "float", scale: 100 },

	// -- 眼球 -- 白目
	{ offset: 0x0122, name: "左之瞳", type: "uint32", comment: "對照瞳表" },
	{ offset: 0x0126, name: "左眼白之色", type: "rgba", comment: "推測有 alpha , 但無效" },
	// 0x012A G 值 float x 255
	// 0x012E B 值 float x 255
	// 0x0132 A 值 float x 255 無作用
	{ offset: 0x0136, name: "左瞳孔之色", type: "rgba", comment: "推測有 alpha , 但無效" },
	// 0x013A G 值 float x 255
	// 0x013E B 值 float x 255
	// 0x0142 A 值 float x 255 無作用
	{ offset: 0x0146, name: "左瞳孔大小", type: "float", scale: 100 },
	{ offset: 0x014A, name: "左瞳孔亮度", type: "float", scale: 100 },

	{ offset: 0x014E, name: "右之瞳", type: "uint32", comment: "對照瞳表" },
	{ offset: 0x0152, name: "右眼白之色", type: "rgba", comment: "推測有 alpha , 但無效" },
	// 0x0156 G 值 float x 255
	// 0x015A B 值 float x 255
	// 0x015E A 值 float x 255 無作用
	{ offset: 0x0162, name: "右瞳孔之色", type: "rgba", comment: "推測有 alpha , 但無效" },
	// 0x0166 G 值 float x 255
	// 0x016A B 值 float x 255
	// 0x016E A 值 float x 255 無作用
	{ offset: 0x0172, name: "右瞳孔大小", type: "float", scale: 100 },
	{ offset: 0x0176, name: "右瞳孔亮度", type: "float", scale: 100 },

	// -- 刺青 --
	{ offset: 0x017A, name: "刺青", type: "uint32", comment: "對照刺青表" },
	{ offset: 0x017E, name: "色", type: "rgba", comment: "Alpha 可設定" },
	// 0x0182 G 值 float x 255
	// 0x0186 B 值 float x 255
	// 0x018A A 值 float x 255 無作用

	// -- 全體 -- 全部都是數值
	{ offset: 0x0192, name: "全体橫幅", type: "float", scale: 100 },
	{ offset: 0x0196, name: "上部前後", type: "float", scale: 100 },
	{ offset: 0x019A, name: "上部上下", type: "float", scale: 100 },
	{ offset: 0x019E, name: "下部前後", type: "float", scale: 100 },
	{ offset: 0x01A2, name: "下部橫幅", type: "float", scale: 100 },

	// -- 下巴 --
	{ offset: 0x01A6, name: "橫幅", type, "float", scale: 100 },
	{ offset: 0x01AA, name: "上下", type, "float", scale: 100 },
	{ offset: 0x01AE, name: "前後", type, "float", scale: 100 },
	{ offset: 0x01B2, name: "角度", type, "float", scale: 100 },
	{ offset: 0x01B6, name: "下部上下", type, "float", scale: 100 },
	{ offset: 0x01BA, name: "先幅", type, "float", scale: 100 },
	{ offset: 0x01BE, name: "先上下", type, "float", scale: 100 },
	{ offset: 0x01C2, name: "先前後", type, "float", scale: 100 },

	// -- 頰 --
	{ offset: 0x01C6, name: "下部上下", type: "float", scale: 100 },
	{ offset: 0x01CA, name: "下部前後", type: "float", scale: 100 },
	{ offset: 0x01CE, name: "下部幅", type: "float", scale: 100 },
	{ offset: 0x01D2, name: "上部上下", type: "float", scale: 100 },
	{ offset: 0x01D6, name: "上部前後", type: "float", scale: 100 },
	{ offset: 0x01DA, name: "上部幅", type: "float", scale: 100 },

	// -- 眉 --
	{ offset: 0x01DE, name: "上下", type: "float", scale: 100 },
	{ offset: 0x01E2, name: "橫位置", type: "float", scale: 100 },
	{ offset: 0x01E6, name: "角度Z軸", type: "float", scale: 100 },
	{ offset: 0x01EA, name: "內側形狀", type: "float", scale: 100 },
	{ offset: 0x01EE, name: "外側形狀", type: "float", scale: 100 },

	// -- 眼周 目元 --
	{ offset: 0x01F2, name: "上下", type, "float", scale: 100 },
	{ offset: 0x01F6, name: "橫位置", type, "float", scale: 100 },
	{ offset: 0x01FA, name: "前後", type, "float", scale: 100 },
	{ offset: 0x01FE, name: "橫幅", type, "float", scale: 100 },
	{ offset: 0x0202, name: "縱幅", type, "float", scale: 100 },
	{ offset: 0x0206, name: "角度Z軸", type, "float", scale: 100 },
	{ offset: 0x020A, name: "角度Y軸", type, "float", scale: 100 },
	{ offset: 0x020E, name: "目頭左右位置", type, "float", scale: 100 },
	{ offset: 0x0212, name: "目尻左右位置", type, "float", scale: 100 },
	{ offset: 0x0216, name: "目頭上下位置", type, "float", scale: 100 },
	{ offset: 0x021A, name: "目尻上下位置", type, "float", scale: 100 },
	{ offset: 0x021E, name: "眼瞼形狀1", type, "float", scale: 100 },	// まぶた
	{ offset: 0x0222, name: "眼瞼形狀2", type, "float", scale: 100 },

	// -- 眼球 -- 基本設定
	{ offset: 0x0226, name: "瞳的上下調整", type, "float", scale: 100 },
	{ offset: 0x022A, name: "瞳的橫幅", type, "float", scale: 100 },
	{ offset: 0x022E, name: "瞳的縱幅", type, "float", scale: 100 },

	// -- 鼻 --
	{ offset: 0x0232, name: "全体上下", type, "float", scale: 100 },
	{ offset: 0x0236, name: "全体前後", type, "float", scale: 100 },
	{ offset: 0x023A, name: "全体角度X軸", type, "float", scale: 100 },
	{ offset: 0x023E, name: "全体橫幅", type, "float", scale: 100 },
	{ offset: 0x0242, name: "鼻筋高度", type, "float", scale: 100 },
	{ offset: 0x0246, name: "鼻筋橫幅", type, "float", scale: 100 },
	{ offset: 0x024A, name: "鼻筋形狀", type, "float", scale: 100 },
	{ offset: 0x024E, name: "小鼻橫幅", type, "float", scale: 100 },
	{ offset: 0x0252, name: "小鼻上下", type, "float", scale: 100 },
	{ offset: 0x0256, name: "小鼻前後", type, "float", scale: 100 },
	{ offset: 0x025A, name: "小鼻角度X軸", type, "float", scale: 100 },
	{ offset: 0x025E, name: "小鼻角度Z軸", type, "float", scale: 100 },
	{ offset: 0x0262, name: "鼻尖高度", type, "float", scale: 100 },
	{ offset: 0x0266, name: "鼻尖角度X軸", type, "float", scale: 100 },
	{ offset: 0x026A, name: "鼻尖大小", type, "float", scale: 100 },

	// -- 口 --
	{ offset: 0x026E, name: "上下", type, "float", scale: 100 },
	{ offset: 0x0272, name: "橫幅", type, "float", scale: 100 },
	{ offset: 0x0276, name: "縱幅", type, "float", scale: 100 },
	{ offset: 0x027A, name: "前後", type, "float", scale: 100 },
	{ offset: 0x027E, name: "形狀上", type, "float", scale: 100 },
	{ offset: 0x0282, name: "形狀下", type, "float", scale: 100 },
	{ offset: 0x0286, name: "形狀口角", type, "float", scale: 100 },

	// -- 耳 --
	{ offset: 0x028A, name: "size", type: "float", scale: 100 },
	{ offset: 0x028E, name: "角度Y軸", type: "float", scale: 100 },
	{ offset: 0x0292, name: "角度Z軸", type: "float", scale: 100 },
	{ offset: 0x0296, name: "上部形狀", type: "float", scale: 100 },
	{ offset: 0x029A, name: "下部形狀", type: "float", scale: 100 },

	// -- 睫毛 まつげ --
	{ offset: 0x029E, name: "睫毛", type: "uint32", comment: "對照眉毛表" },
	{ offset: 0x02A6, name: "睫毛顏色", type: "rgba", comment: "Alpha 可設定" },
	// 0x02AA G 值 float x 255 (0.047059 = 12)
	// 0x02AE B 值 float x 255 (0.050980 = 13)
	// 0x02B2 A 值 float x 255 (0.054902 = 14)
	// 少了四個值 ...?0x02B6, 0x02BA, 0x02BE, 0x02C2
	{ offset: 0x02C6, name: "光澤強度", type: "float", scale: 100 },
	{ offset: 0x02CA, name: "光澤質感", type: "float", scale: 100 },

	// -- 眼影 --
	{ offset: 0x02CE, name: "眼影", type: "uint32", comment: "對照眼影表" },
	{ offset: 0x02D2, name: "色", type: "rgba", comment: "Alpha 可設定" },
	// 0x02D6 G 值 float x 255
	// 0x02DA B 值 float x 255
	// 0x02DE A 值 float x 255 無作用

	// -- 腮紅 --
	{ offset: 0x02E2, name: "腮紅", type: "uint32", comment: "對照腮紅表" },
	{ offset: 0x02E6, name: "色", type: "rgba", comment: "Alpha 可設定" },
	// 0x02EA G 值 float x 255
	// 0x02EE B 值 float x 255
	// 0x02F2 A 值 float x 255 無作用

	// -- 唇膏 --
	{ offset: 0x02F6, name: "唇膏", type: "uint32", comment: "對照唇膏表" },
	{ offset: 0x02FA, name: "色", type: "rgba", comment: "Alpha 可設定" },
	// 0x02FE G 值 float x 255
	// 0x0302 B 值 float x 255
	// 0x0306 A 值 float x 255 無作用

	// -- 痣 --
	{ offset: 0x030A, name: "痣", type: "uint32", comment: "對照痣表" },
	{ offset: 0x030E, name: "色", type: "rgba", comment: "Alpha 可設定" },
	// 0x0312 G 值 float x 255
	// 0x0316 B 值 float x 255
	// 0x031A A 值 float x 255 無作用

	// -- 眼球 -- 高光 highlight
	{ offset: 0x031E, name: "高光", type: "uint32", comment: "對照高光表" },
	{ offset: 0x0326, name: "睫毛顏色", type: "rgba", comment: "Alpha 可設定" },
	// 0x032A G 值 float x 255 (0.047059 = 12)
	// 0x032E B 值 float x 255 (0.050980 = 13)
	// 0x0332 A 值 float x 255 (0.054902 = 14)

	// ===== 体 =====

	// -- 全体 肌 --
	{ offset: 0x034E, name: "肌", type: "uint32", comment: "對照肌表" },
	{ offset: 0x0356, name: "色相", type: "float", scale: 100, min: -50, max: 50 },
	{ offset: 0x035A, name: "彩度", type: "float", scale: 50, min: 0, max: 100 },
	{ offset: 0x035E, name: "明度", type: "float", scale: 50, min: 0, max: 100 },
	// 這裏有透明度, 但無法設定 { offset: 0x0362, name: "透明", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0366, name: "光澤強度", type: "float", scale: 250, min: 0, max: 100 },
	{ offset: 0x036A, name: "光澤質感", type: "float", scale: 125, min: 0, max: 100 },
	{ offset: 0x0372, name: "肉感強度", type: "float", scale: 100, min: 0, max: 100 },

	// -- 陰毛 --
	{ offset: 0x0376, name: "陰毛", type: "uint32", comment: "對照陰毛表" },
	{ offset: 0x037E, name: "陰毛顏色", type: "rgba", comment: "Alpha 可設定" },
	// 0x0382 G 值 float x 255 (0.047059 = 12)
	// 0x0386 B 值 float x 255 (0.050980 = 13)
	// 0x038A A 值 float x 255 (0.054902 = 14)

	// -- 刺青 --
	{ offset: 0x0396, name: "刺青", type: "uint32", comment: "對照刺青表" },
	{ offset: 0x039A, name: "睫毛顏色", type: "rgba", comment: "Alpha 可設定" },
	// 0x039E G 值 float x 255 (0.047059 = 12)
	// 0x03A2 B 值 float x 255 (0.050980 = 13)
	// 0x03A6 A 值 float x 255 (0.054902 = 14)

	// -- 全体 身高 --
	{ offset: 0x03AE, name: "身高", type: "float", scale: 100 },

	// -- 胸 --
	{ offset: 0x03B2, name: "胸部大小", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03B6, name: "胸上下位置", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03BA, name: "胸部左右張開", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03BE, name: "胸部左右位置", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03C2, name: "胸部上下角度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03C6, name: "胸部尖挺", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03CA, name: "乳暈隆起", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03CE, name: "乳頭粗細", type: "float", scale: 100, min: 0, max: 100 },

	// -- 全体 頭大小 --
	{ offset: 0x03D2, name: "頭大小", type: "float", scale: 100 },

	// -- 上半身 --
	{ offset: 0x03D6, name: "脖子寬度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03DA, name: "脖子厚度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03DE, name: "軀幹肩部寬度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03E2, name: "軀幹肩部厚度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03E6, name: "軀幹上部寬度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03EA, name: "軀幹上部厚度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03EE, name: "軀幹下部寬度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03F2, name: "軀幹下部厚度", type: "float", scale: 100, min: 0, max: 100 },

	// -- 下半身 -- 改變 腰的位置時,有可能也改到脖子數值但影響極度微小,可忽略...
	{ offset: 0x03F6, name: "腰部位置", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03FA, name: "腰部以上寬度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x03FE, name: "腰部以上厚度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0402, name: "腰部以下寬度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0406, name: "腰部以下厚度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x040A, name: "臀部大小", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x040E, name: "臀部角度", type: "float", scale: 100, min: 0, max: 100 },

	// -- 脚 --
	{ offset: 0x0412, name: "大腿上部", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0416, name: "大腿下部", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x041A, name: "小腿肚", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x041E, name: "腳踝", type: "float", scale: 100, min: 0, max: 100 },

	// -- 腕 --
	{ offset: 0x0422, name: "肩膀", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0426, name: "上臂", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x042A, name: "前臂", type: "float", scale: 100, min: 0, max: 100 },

	// -- 胸 --
	{ offset: 0x042E, name: "乳頭挺立", type: "float", scale: 100, min: 0, max: 100 },

	// -- 胸 乳首 --
	{ offset: 0x0432, name: "乳頭", type: "uint32", comment: "對照乳頭表" },
	{ offset: 0x043A, name: "色相", type: "float", scale: 100, min: -50, max: 50 },
	{ offset: 0x043E, name: "彩度", type: "float", scale: 50, min: 0, max: 100 },
	{ offset: 0x0442, name: "明度", type: "float", scale: 50, min: 0, max: 100 },
	{ offset: 0x0446, name: "透明", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x044A, name: "光澤強度", type: "float", scale: 250, min: 0, max: 100 },
	{ offset: 0x044E, name: "光澤質感", type: "float", scale: 125, min: 0, max: 100 },

	// -- 曬痕 --
	{ offset: 0x0452, name: "曬痕", type: "uint32", comment: "對照曬痕表" },
	{ offset: 0x0456, name: "色相", type: "float", scale: 100, min: -50, max: 50 },
	{ offset: 0x045A, name: "彩度", type: "float", scale: 50, min: 0, max: 100 },
	{ offset: 0x045E, name: "明度", type: "float", scale: 50, min: 0, max: 100 },
	{ offset: 0x0462, name: "濃度", type: "float", scale: 100, min: 0, max: 100 },



	// -- 爪 --
	{ offset: 0x046A, name: "色相", type: "float", scale: 100, min: -50, max: 50 },
	{ offset: 0x046E, name: "彩度", type: "float", scale: 50, min: 0, max: 100 },
	{ offset: 0x0472, name: "明度", type: "float", scale: 50, min: 0, max: 100 },
	// 不可修改... { offset: 0x0476, name: "透明", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x047A, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x047E, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },

	// -- 爪 指甲油 --
	{ offset: 0x0486, name: "指甲油顏色", type: "rgba", comment: "Alpha 可設定" },
	// 0x048A G 值 float x 255 (0.047059 = 12)
	// 0x048E B 值 float x 255 (0.050980 = 13)
	// 0x0492 A 值 float x 255 (0.054902 = 14)

	// -- 爪 指甲油 --
	{ offset: 0x04A6, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x04AA, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },

	// -- 胸 乳首 --
	{ offset: 0x04AE, name: "乳暈大小", type: "float", scale: 100, min: 0, max: 100 },

	// -- 胸 --
	{ offset: 0x04B2, name: "胸部柔軟", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x04B6, name: "胸部重量", type: "float", scale: 100, min: 0, max: 100 },

	// ===== 衣服 =====
	// 可調顏色的固定多 80 bytes. 位置之間應該有分隔符號?
	// 固定顏色的只有 8 個 bytes, 所以連改顏色進去的機會都沒有.

	// top
	// 有些方服穿了會抑制別的部位穿上衣服,例如不能穿下著,胸罩等等,但資料還是在...
	{ offset: 0x04BE, name: "上衣", type: "uint32", comment: "對照上衣表" },
	// offset: 0x04C2 沒用到...
	{ offset: 0x04C6, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x04CA G 值 float x 255 (0.047059 = 12)
	// 0x04CE B 值 float x 255 (0.050980 = 13)
	// 0x04D2 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x04D6, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x04DA G 值 float x 255 (0.047059 = 12)
	// 0x04DE B 值 float x 255 (0.050980 = 13)
	// 0x04E2 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x04E6, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x04EA, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x04EE, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x04F2 G 值 float x 255 (0.047059 = 12)
	// 0x04F6 B 值 float x 255 (0.050980 = 13)
	// 0x04FA A 值 float x 255 (0.054902 = 14)
	{ offset: 0x04FE, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0502 G 值 float x 255 (0.047059 = 12)
	// 0x0506 B 值 float x 255 (0.050980 = 13)
	// 0x050A A 值 float x 255 (0.054902 = 14)
	{ offset: 0x050E, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0512, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },

	// offset: 0x0516 ... 可能是分隔符號

	// bottom
	{ offset: 0x051A, name: "下著", type: "uint32", comment: "對照下著表" },
	// offset: 0x051E 沒用到...
	{ offset: 0x0522, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0526 G 值 float x 255 (0.047059 = 12)
	// 0x052A B 值 float x 255 (0.050980 = 13)
	// 0x052E A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0532, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0536 G 值 float x 255 (0.047059 = 12)
	// 0x053A B 值 float x 255 (0.050980 = 13)
	// 0x053E A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0542, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0546, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x054A, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x054E G 值 float x 255 (0.047059 = 12)
	// 0x0552 B 值 float x 255 (0.050980 = 13)
	// 0x0556 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x055A, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x055E G 值 float x 255 (0.047059 = 12)
	// 0x0562 B 值 float x 255 (0.050980 = 13)
	// 0x0566 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x056A, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x056E, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },

	// offset: 0x0572 ... 可能是分隔符號

	// bra
	{ offset: 0x0576, name: "胸罩", type: "uint32", comment: "對照下著表" },
	// offset: 0x057A 沒用到...
	{ offset: 0x057E, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0582 G 值 float x 255 (0.047059 = 12)
	// 0x0586 B 值 float x 255 (0.050980 = 13)
	// 0x058A A 值 float x 255 (0.054902 = 14)
	{ offset: 0x058E, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0592 G 值 float x 255 (0.047059 = 12)
	// 0x0596 B 值 float x 255 (0.050980 = 13)
	// 0x059A A 值 float x 255 (0.054902 = 14)
	{ offset: 0x059E, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x05A2, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x05A6, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x05AA G 值 float x 255 (0.047059 = 12)
	// 0x05AE B 值 float x 255 (0.050980 = 13)
	// 0x05B2 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x05B6, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x05BA G 值 float x 255 (0.047059 = 12)
	// 0x05BE B 值 float x 255 (0.050980 = 13)
	// 0x05C2 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x05C6, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x05CA, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },

	// offset: 0x05CE ... 可能是分隔符號

	// panty
	{ offset: 0x05D2, name: "內褲", type: "uint32", comment: "對照下著表" },
	// offset: 0x05D6 沒用到...
	{ offset: 0x05DA, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x05DE G 值 float x 255 (0.047059 = 12)
	// 0x05E2 B 值 float x 255 (0.050980 = 13)
	// 0x05E6 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x05EA, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x05EE G 值 float x 255 (0.047059 = 12)
	// 0x05F2 B 值 float x 255 (0.050980 = 13)
	// 0x05F6 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x05FA, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x05FE, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0602, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0606 G 值 float x 255 (0.047059 = 12)
	// 0x060A B 值 float x 255 (0.050980 = 13)
	// 0x060E A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0612, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0616 G 值 float x 255 (0.047059 = 12)
	// 0x061A B 值 float x 255 (0.050980 = 13)
	// 0x061E A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0622, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0626, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },

	// offset: 0x062A

	// swimsuit
	{ offset: 0x062E, name: "泳裝", type: "uint32", comment: "對照下著表" },
	// offset: 0x0632 沒用到...
	{ offset: 0x0636, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x063A G 值 float x 255 (0.047059 = 12)
	// 0x063E B 值 float x 255 (0.050980 = 13)
	// 0x0642 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0646, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x064A G 值 float x 255 (0.047059 = 12)
	// 0x064E B 值 float x 255 (0.050980 = 13)
	// 0x0652 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0656, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x065A, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x065E, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0662 G 值 float x 255 (0.047059 = 12)
	// 0x0666 B 值 float x 255 (0.050980 = 13)
	// 0x066A A 值 float x 255 (0.054902 = 14)
	{ offset: 0x066E, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0672 G 值 float x 255 (0.047059 = 12)
	// 0x0676 B 值 float x 255 (0.050980 = 13)
	// 0x067A A 值 float x 255 (0.054902 = 14)
	{ offset: 0x067E, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0682, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },

	// offset: 0x0686

	// swimsuit - top
	// 有些方服穿了會抑制別的部位穿上衣服,例如不能穿下著,胸罩等等,但資料還是在...
	{ offset: 0x068A, name: "上衣", type: "uint32", comment: "對照上衣表" },
	// offset: 0x068E 沒用到...
	{ offset: 0x0692, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0696 G 值 float x 255 (0.047059 = 12)
	// 0x069A B 值 float x 255 (0.050980 = 13)
	// 0x069E A 值 float x 255 (0.054902 = 14)
	{ offset: 0x06A2, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x06A6 G 值 float x 255 (0.047059 = 12)
	// 0x06AA B 值 float x 255 (0.050980 = 13)
	// 0x06AE A 值 float x 255 (0.054902 = 14)
	{ offset: 0x06B2, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x06B6, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x06BA, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x06BE G 值 float x 255 (0.047059 = 12)
	// 0x06C2 B 值 float x 255 (0.050980 = 13)
	// 0x06C6 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x06CA, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x06CE G 值 float x 255 (0.047059 = 12)
	// 0x06D2 B 值 float x 255 (0.050980 = 13)
	// 0x06D6 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x06DA, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x06DE, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	
	// offset: 0x06E2

	// swimsuit - top
	// 有些方服穿了會抑制別的部位穿上衣服,例如不能穿下著,胸罩等等,但資料還是在...
	{ offset: 0x06E6, name: "上衣", type: "uint32", comment: "對照上衣表" },
	// offset: 0x06EA 沒用到...
	{ offset: 0x06EE, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x06F2 G 值 float x 255 (0.047059 = 12)
	// 0x06F6 B 值 float x 255 (0.050980 = 13)
	// 0x06FA A 值 float x 255 (0.054902 = 14)
	{ offset: 0x06FE, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0702 G 值 float x 255 (0.047059 = 12)
	// 0x0706 B 值 float x 255 (0.050980 = 13)
	// 0x070A A 值 float x 255 (0.054902 = 14)
	{ offset: 0x070E, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0712, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0716, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x071A G 值 float x 255 (0.047059 = 12)
	// 0x071E B 值 float x 255 (0.050980 = 13)
	// 0x0722 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0726, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x072A G 值 float x 255 (0.047059 = 12)
	// 0x072E B 值 float x 255 (0.050980 = 13)
	// 0x0732 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0736, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x073A, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	
	// offset: 0x73E
	
	// gloves
	{ offset: 0x0742, name: "手套", type: "uint32", comment: "對照下著表" },
	// offset: 0x0746 沒用到...
	{ offset: 0x074A, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x074E G 值 float x 255 (0.047059 = 12)
	// 0x0752 B 值 float x 255 (0.050980 = 13)
	// 0x0756 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x075A, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x075E G 值 float x 255 (0.047059 = 12)
	// 0x0762 B 值 float x 255 (0.050980 = 13)
	// 0x0766 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x076A, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x076E, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0772, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0776 G 值 float x 255 (0.047059 = 12)
	// 0x077A B 值 float x 255 (0.050980 = 13)
	// 0x077E A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0782, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0786 G 值 float x 255 (0.047059 = 12)
	// 0x078A B 值 float x 255 (0.050980 = 13)
	// 0x078E A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0792, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0796, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },

	// offset: 0x079A

	// pantyhose
	{ offset: 0x079E, name: "褲襪", type: "uint32", comment: "對照下著表" },
	// offset: 0x07A2 沒用到...
	{ offset: 0x07A6, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x07AA G 值 float x 255 (0.047059 = 12)
	// 0x07AE B 值 float x 255 (0.050980 = 13)
	// 0x07B2 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x07B6, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x07BA G 值 float x 255 (0.047059 = 12)
	// 0x07BE B 值 float x 255 (0.050980 = 13)
	// 0x07C2 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x07C6, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x07CA, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x07CE, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x07D2 G 值 float x 255 (0.047059 = 12)
	// 0x07D6 B 值 float x 255 (0.050980 = 13)
	// 0x07DA A 值 float x 255 (0.054902 = 14)
	{ offset: 0x07DE, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x07E2 G 值 float x 255 (0.047059 = 12)
	// 0x07E6 B 值 float x 255 (0.050980 = 13)
	// 0x07EA A 值 float x 255 (0.054902 = 14)
	{ offset: 0x07EE, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x07F2, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	
	// offset: 0x07F6
	
	// socks
	{ offset: 0x07FA, name: "襪子", type: "uint32", comment: "對照下著表" },
	// offset: 0x07FE 沒用到...
	{ offset: 0x0802, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0806 G 值 float x 255 (0.047059 = 12)
	// 0x080A B 值 float x 255 (0.050980 = 13)
	// 0x080E A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0812, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0816 G 值 float x 255 (0.047059 = 12)
	// 0x081A B 值 float x 255 (0.050980 = 13)
	// 0x081E A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0822, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0826, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x082A, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x082E G 值 float x 255 (0.047059 = 12)
	// 0x0832 B 值 float x 255 (0.050980 = 13)
	// 0x0836 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x083A, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x083E G 值 float x 255 (0.047059 = 12)
	// 0x0842 B 值 float x 255 (0.050980 = 13)
	// 0x0846 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x084A, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x084E, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	
	// offset: 0x0852
	
	// shoes
	{ offset: 0x0856, name: "鞋子", type: "uint32", comment: "對照下著表" },
	// offset: 0x085A 沒用到...
	{ offset: 0x085E, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0862 G 值 float x 255 (0.047059 = 12)
	// 0x0866 B 值 float x 255 (0.050980 = 13)
	// 0x086A A 值 float x 255 (0.054902 = 14)
	{ offset: 0x086E, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0872 G 值 float x 255 (0.047059 = 12)
	// 0x0876 B 值 float x 255 (0.050980 = 13)
	// 0x087A A 值 float x 255 (0.054902 = 14)
	{ offset: 0x087E, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0882, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0886, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x088A G 值 float x 255 (0.047059 = 12)
	// 0x088E B 值 float x 255 (0.050980 = 13)
	// 0x0892 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0896, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x089A G 值 float x 255 (0.047059 = 12)
	// 0x089E B 值 float x 255 (0.050980 = 13)
	// 0x08A2 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x08A6, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x08AA, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	
	
	
	// offset: 0x08AE 0x00 0x00 0x00 0x00 分隔用?
	
	// ===== 配飾 =====
	// 0x08B2 ?
	// 0x08B3
	// 0x08B4
	// 0x08B5
	// 0x08B6
	// 0x08B7
	// 0x08B8
	
	
	// 配戴位置改變時, 只有 0x08B9 改變, 讀 08B6 的話很怪...
	// 0x08BA
	// 0x08BB
	// 0x08BC
	
	// 0x08BD ~ 0x08C0, 位置 x 軸, x 100
	// 0x08C1 ~ 0x08C4, 位置 y 軸, x 100 
	// 0x08C5 ~ 0x08C8, 位置 z 軸, x 100
	// 0x08C9 ~ 0x08CC, 角度 x 軸, x 1
	// 0x08CD ~ 0x08D0, 角度 y 軸, x 1
	// 0x08D1 ~ 0x08D4, 角度 z 軸, x 1
	// 0x08D5 ~ 0x08D8, 縮放 x 軸, x 1
	// 0x08D9 ~ 0x08DC, 縮放 y 軸, x 1
	// 0x08DD ~ 0x08E0, 縮放 z 軸, x 1
	
	// 0x08E1 ~ 0x08E4 ????
	
	// 0x08E5 ~ 0x08E8, 主色 R
	// 0x08E9 ~ 0x08EC, 主色 G
	// 0x08ED ~ 0x08F0, 主色 B
	// 0x08F1 ~ 0x08F4, 主色 A
	// 0x08F5 ~ 0x08F8, 光澤 R
	// 0x08F9 ~ 0x08FC, 光澤 G
	// 0x08FD ~ 0x0900, 光澤 B
	// 0x0901 ~ 0x0904, 光澤 A
	// 0x0905 ~ 0x0908, 強度
	// 0x0909 ~ 0x090C, 質感

	// 0x090D ~ 0x0910, 副色 R
	// 0x0911 ~ 0x0914, 副色 G
	// 0x0915 ~ 0x0918, 副色 B
	// 0x0919 ~ 0x091C, 副色 A
	// 0x091D ~ 0x0920, 光澤 R
	// 0x0921 ~ 0x0924, 光澤 G
	// 0x0925 ~ 0x0928, 光澤 B
	// 0x0929 ~ 0x092C, 光澤 A
	// 0x092D ~ 0x0930, 強度
	// 0x0931 ~ 0x0934, 質感
	
	// 0x093D ~ 位置唷 ~~
	
	// 0x0941 ~ 0x0944 位置 x

	{ offset: 0x08B2, name: "種類", type: "uint32" },
	{ offset: 0x08B6, name: "配飾ID", type: "uint32" },
	
	{ offset: 0x08BA, name: "特殊值", type: "uint32" },
	{ offset: 0x08BE, name: "配戴位置", type: "uint32" },
	{ offset: 0x08C2, name: "位置調整x", type: "float32", scale: 1 },
	{ offset: 0x08C6, name: "位置調整y", type: "float32", scale: 1 },
	{ offset: 0x08CA, name: "位置調整z", type: "float32", scale: 1 },
	{ offset: 0x08CE, name: "角度調整x", type: "float32", scale: 1 },
	{ offset: 0x08D2, name: "角度調整y", type: "float32", scale: 1 },
	{ offset: 0x08D6, name: "角度調整z", type: "float32", scale: 1 },
	{ offset: 0x08DA, name: "伸縮調整x", type: "float32", scale: 1 },
	{ offset: 0x08DE, name: "伸縮調整y", type: "float32", scale: 1 },
	{ offset: 0x08E2, name: "伸縮調整z", type: "float32", scale: 1 },
	{ offset: 0x08E6, name: "主色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x08EA G 值 float x 255 (0.047059 = 12)
	// 0x08EE B 值 float x 255 (0.050980 = 13)
	// 0x08F2 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x08F6, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x08FA G 值 float x 255 (0.047059 = 12)
	// 0x08FE B 值 float x 255 (0.050980 = 13)
	// 0x0902 A 值 float x 255 (0.054902 = 14)
	{ offset: 0x0906, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x090A, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x090E, name: "輔色", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0912 G 值 float x 255 (0.047059 = 12)
	// 0x0916 B 值 float x 255 (0.050980 = 13)
	// 0x091A A 值 float x 255 (0.054902 = 14)
	{ offset: 0x091E, name: "光澤", type: "rgba", comment: "Alpha 不可設定" },
	// 0x0922 G 值 float x 255 (0.047059 = 12)
	// 0x0926 B 值 float x 255 (0.050980 = 13)
	// 0x092A A 值 float x 255 (0.054902 = 14)
	{ offset: 0x092E, name: "光澤強度", type: "float", scale: 100, min: 0, max: 100 },
	{ offset: 0x0932, name: "光澤質感", type: "float", scale: 100, min: 0, max: 100 },
	
	// offset: 0x0936 分隔符號, 接下一個
	
	
];