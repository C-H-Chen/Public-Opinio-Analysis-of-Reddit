# 簡介:

本專案是一個基於Python的網路論壇之輿論分析專案。針對"電子好球帶"這個議題，於Reddit爬蟲符合所有關鍵字的全部內容並匯入SQL資料庫，接著進行一連串的特徵工程與參數調整，再運行機器學習模型與情感分析技術，獲得輿情趨勢的相關結果，最後透過Tableau展示輿情變化。  

下圖為專案架構，或請見[/docs/architecture.jpg](https://github.com/C-H-Chen/-Reddit---/blob/main/docs/architecture.jpg)。  

![architecture](https://github.com/user-attachments/assets/67228327-dce2-4d0b-9787-049e252f656a)  

# 環境:  

建議於python3.8+中執行，所需要安裝的套件請見[/docs/requirements.txt](https://github.com/C-H-Chen/-Reddit---/blob/main/docs/requirements.txt)。

# 目錄架構說明:  

 ├── core  
 │&emsp;&ensp;&nbsp;├── main.py&emsp;&emsp;&emsp;&emsp;&emsp;<-  
 ├── data  
 │&emsp;&ensp;&nbsp;├── processed_data.csv&emsp;&emsp;&emsp;&emsp;&emsp;<-  
 │&emsp;&ensp;&nbsp;├── raw_data.csv&emsp;&emsp;&emsp;&emsp;&emsp;<-  
