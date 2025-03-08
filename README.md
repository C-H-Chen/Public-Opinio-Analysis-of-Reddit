# 簡介:

本專案是一個基於Python的網路論壇之輿論分析專案。針對"電子好球帶"議題，於Reddit爬蟲符合所有關鍵字的全部內容並匯入SQL資料庫，接著進行一連串的特徵工程與參數調整，再運行機器學習模型與情感分析技術，獲得輿情趨勢的相關結果，最後透過Tableau展示輿情變化。  

下圖為專案架構，或請見[/docs/architecture.jpg](https://github.com/C-H-Chen/-Reddit---/blob/main/docs/Architecture.jpg)。  

 ![architecture](https://github.com/user-attachments/assets/98915b62-1938-4639-b14f-233bc8e9bd5b)

# 環境:  

建議於python3.8+中執行，所需要安裝的套件請見[/docs/requirements.txt](https://github.com/C-H-Chen/-Reddit---/blob/main/docs/requirements.txt)。

# 目錄結構說明:  

 ``` 
 ├── core
 │   ├── main.py               <- 核心程式碼(特徵工程、資料匯入、情感分析與模型訓練)
 │ 
 ├── data  
 │   ├── processed_data.csv    <- 特徵工程後且含情感分數的資料
 │   ├── raw_data.csv          <- 原始資料
 │
 ├── docs  
 │   ├── Architecture.jpg      <- 專案架構圖
 │   ├── requirements.txt      <- 所需套件清單
 │
 ├── sql & scraping
 │   ├── sql_scraping.py       <- 爬蟲程式碼(Reddit爬蟲、sql資料表建立與資料插入)
 │
 ├── tableau
 │   ├── README.md             <- tableau線上連結
 │   ├── tableau.twbx          <- tableau檔案
 │
 ├── README.md                 <-  專案說明文檔
 ``` 
