# IntroToAI_DuckChessEngine
113-2人工智慧概論期末專題，有關於鴨子棋引擎的設計

## 架構
```bash
duck-chess-engine/
├── engine/
│   ├── board.py           # 棋盤邏輯 + 鴨子支援
│   ├── move_generator.py  # 走法產生器
│   ├── search.py          # 搜尋演算法（Minimax, Alpha-Beta）
│   └── nnue_eval.py       # 評估函數（使用 PyTorch）
├── api/
│   ├── main.py            # FastAPI 伺服器
│   └── websocket.py       # WebSocket 互動邏輯
├── web/                   # 前端（React 或其他）
│   └── ...
├── models/
│   └── nnue_model.pth     # 預訓練模型檔
├── tests/
│   └── test_engine.py
├── requirements.txt
└── README.md
```