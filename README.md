![image](https://github.com/user-attachments/assets/0e97c51a-82fc-4482-9f39-77a9c6c0b95c)# Duck-Chess-Engine
113-2人工智慧概論期末專題，有關於西洋棋變種之鴨子棋的引擎
![image](https://github.com/user-attachments/assets/b2cfd548-0cea-4844-ad31-40532f032cfc)

### 什麼是鴨子棋
可參考這個網址：[什麼是鴨子棋](<https://www.chess.com/terms/duck-chess> "Title")
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
