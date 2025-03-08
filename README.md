# 簡介:

本專案是一個基於Python的網路論壇之輿論分析專案。針對"電子好球帶"這個議題，於Reddit爬蟲符合所有關鍵字的全部內容並匯入SQL資料庫，接著進行一連串的特徵工程與參數調整，再運行機器學習模型與情感分析技術，獲得輿情趨勢的相關結果，最後透過Tableau展示輿情變化。  

下圖為專案架構，或請見[/docs/architecture.jpg](https://github.com/C-H-Chen/-Reddit---/blob/main/docs/architecture.jpg)。  

![architecture](https://github.com/user-attachments/assets/67228327-dce2-4d0b-9787-049e252f656a)  

# 環境:  

建議於python3.8+中執行，所需要安裝的套件請見[/docs/requirements.txt](https://github.com/C-H-Chen/-Reddit---/blob/main/docs/requirements.txt)。

# 目錄架構說明:  

├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for 
│                         {{ cookiecutter.module_name }} and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── {{ cookiecutter.module_name }}   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes {{ cookiecutter.module_name }} a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    └── plots.py                <- Code to create visualizations   
