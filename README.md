# Duck-Chess-Engine
113-2人工智慧概論期末專題，有關於西洋棋變種之鴨子棋的引擎
<br><br>
<img src="https://github.com/user-attachments/assets/b2cfd548-0cea-4844-ad31-40532f032cfc" height="200px" width="400px" >

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
├── plaintextGame/
│   ├── images             # 棋類圖檔
│   │   └── ...
│   ├── ChessAI.py         # 遊戲AI實作
│   ├── ChessEngine.py     # 遊戲引擎與行棋邏輯
│   └── ChessMain.py       # 遊戲執行主程式
├── requirements.txt
└── README.md
```
### 待修復的bug
1. 鴨子開場會直接擺在e4，嚴重歧視王兵玩家
2. 理論上鴨子棋沒有將死一說，勝利條件只有把對面的王吃掉，目前的遊戲結束邏輯仍然是判斷對面的王有沒有被將死，這部分需要更改
3. AI實力有些薄弱，可能需要nerf玩家

### 參考
來自這位兄弟的原版西洋棋引擎: [chess-engine](<https://github.com/mikolaj-skrzypczak/chess-engine.git> "Title")
