# Duck-Chess-Engine
113-2人工智慧概論期末專題，有關於西洋棋變種之鴨子棋的引擎
<br><br>
<img src="https://github.com/user-attachments/assets/b2cfd548-0cea-4844-ad31-40532f032cfc" height="200px" width="400px" >

### 什麼是鴨子棋
可參考這個網址：[什麼是鴨子棋](<https://www.chess.com/terms/duck-chess> "Title")
## 規劃架構
```bash
└─Duck-Chess-Engine
    │  .gitignore
    │  README.md
    │  requirements.txt
    ├─results //store results
    └─src
        │  ChessAI.py //chess nnue part
        │  chessAi_handcraft.py //chess handcraft eval part
        │  ChessEngine.py //chess engine modified for duck one
        │  ChessMain.py //visulization and invoke game
        │  duck-ba21f91f5d81.nnue //model for nnue
        │  fairy-stockfish.exe //for stockfish eval .exe
        │  fairy-stockfish_x86-64 //for stockfish eval x86
        │
        ├─images //store imges for piece
        ├─images2 //easter eggs
        ├─NNUE model
        │      duck-ba21f91f5d81.nnue //model for nnue
```
### 待修復的bug
1. 鴨子開場會直接擺在e4，嚴重歧視王兵玩家 (已解決)
2. 理論上鴨子棋沒有將死一說，勝利條件只有把對面的王吃掉，目前的遊戲結束邏輯仍然是判斷對面的王有沒有被將死，這部分需要更改 (已解決)
3. AI實力有些薄弱，可能需要nerf玩家 (強度已有提升，將規則改好之後可能會強更多) (已解決)

### 參考
來自這位兄弟的原版西洋棋引擎: [chess-engine](<https://github.com/mikolaj-skrzypczak/chess-engine.git> "Title")
