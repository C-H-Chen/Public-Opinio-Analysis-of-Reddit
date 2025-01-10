import mysql.connector
import pandas as pd
import numpy as np
import nltk
import re
import matplotlib.pyplot as plt
import seaborn as sns


from nltk.corpus import stopwords 
from sqlalchemy import create_engine
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from umap import UMAP
from hdbscan import HDBSCAN

#nltk.download('stopwords')

# 讀取資料 :
host = 'localhost'
username = 'root'
password = 'passwords'
database='reddit'

# 創建 SQLAlchemy 引擎
engine = create_engine(f'mysql+mysqlconnector://{username}:{password}@{host}/{database}')

# 使用Pandas將所有資料查詢結果讀取到 DataFrame
query = "SELECT * FROM `reddit_table`"
df = pd.read_sql(query, engine)

# 資料處理 :
stop = set(stopwords.words('english')) # 用於過濾對語義沒有太大幫助的單字(停用詞)
snow = nltk.stem.SnowballStemmer('english') # 用於將單字還原為其基本形式，以統一處理詞形變化(詞幹提取)

def stop_words(text):
    text = text.lower() # 全小寫
    text = re.sub(r'http\S+', '', text) # 刪除網址
    text = re.sub(r'<.*?>', ' ', text) # 移除 HTML 標籤
    text = re.sub(r'[^A-Za-z\s]', ' ', text)  # 移除符號和數字
    text = re.sub(r'[^\x00-\x7F]+', '', text)# 去除非ASCII字符（包括表情符號）
    text = re.sub(r'\s+', ' ', text)# 去除多個空格
    text = ' '.join([snow.stem(word) for word in text.split() if word not in stop]) # 移除停用詞並提取詞幹
    return text
	
# 將 VADER 的情感得分應用於 Clean_Body 欄位
def sentiment_analysis(text):
    return analyzer.polarity_scores(text)

# 原始資料1236筆
df['Clean_Body'] = df['body'].apply(stop_words) # 清理貼文標題和正文

# 將Clean_Body中只包含"delet"或空格的資料設為缺失值
df['Clean_Body'] = df['Clean_Body'].apply(lambda x: np.nan if (x.strip() == '' or x.strip() == 'delet') else x)
# 共43個缺失值

# 移除Clean_Body為缺失值的資料
df_dropn = df.dropna(subset=['Clean_Body'])

# 將作者、貼文標題和版名皆相同時的多則有效留言合併
df_cleaned = df_dropn.groupby(['author', 'post_title', 'subreddit']).agg({
    'Clean_Body': ' '.join,  # 將該作者的所有留言合併為一條
    'subreddit': 'first',    # 取每組的第一筆討論版名稱
    'created_utc': 'last',   # 取每組的最後一筆創建時間
    'score': 'mean'          # 取分數的平均值 (Reddit的分數類似於讚數)
}).reset_index(drop=True)
# 處理後資料為616筆

# 情感分析:
analyzer = SentimentIntensityAnalyzer() # 初始化VADER
df_cleaned['Sentiment'] = df_cleaned['Clean_Body'].apply(sentiment_analysis) # 計算情感分數

# 分割情感分數為正向、中性、負向和綜合分數
df_cleaned['Pos_Sentiment'] = df_cleaned['Sentiment'].apply(lambda x: x['pos']) # 正面
df_cleaned['Neu_Sentiment'] = df_cleaned['Sentiment'].apply(lambda x: x['neu']) # 中立
df_cleaned['Neg_Sentiment'] = df_cleaned['Sentiment'].apply(lambda x: x['neg']) # 負面
df_cleaned['Compound_Sentiment'] = df_cleaned['Sentiment'].apply(lambda x: x['compound']) # 綜合情感分數

df_cleaned.drop(columns=['Sentiment'], inplace=True) # 刪除多餘的 Sentiment 欄位

# 模型訓練:
embedding_model = SentenceTransformer("all-MiniLM-L6-v2") # 載入文本轉換為嵌入向量的模型
embeddings = embedding_model.encode(df_cleaned['Clean_Body'].tolist(), show_progress_bar=True) # 將每筆文本轉換為嵌入向量

# 設定UMAP和HDBSCAN參數
umap_model = UMAP(n_neighbors=13, min_dist=0.1, metric="cosine", random_state=42) # 降維
hdbscan_model = HDBSCAN(min_cluster_size=10, min_samples=5) # 聚類

# 設定 BERTopic 模型
topic_model = BERTopic(
    umap_model=umap_model,
    hdbscan_model=hdbscan_model,
    nr_topics='optimal',  # 自動選擇最佳的主題數量
    top_n_words=10,  # 每個主題顯示的詞彙數量為10
    verbose=True
)
topics, probs = topic_model.fit_transform(df_cleaned['Clean_Body'], embeddings=embeddings) # 訓練模型

# 各主題的代表性詞彙與文本
represent_words = topic_model.get_topics()
represent_docs = topic_model.get_representative_docs()

# 查看結果
print(topic_model.get_topic_info())
print("-"*30)
print("Topic 0:", represent_words[0])
print("-"*30)
print("Topic 1:", represent_words[1])
print("-"*30)
print("Representative Docs for Topic 0:")
for doc in represent_docs[0]:
    print("Topic 0 Representative_Docs :", doc)
print("-"*30)
for doc in represent_docs[1]:
    print("Topic 1 Representative_Docs :", doc)
print("-"*30)

df_cleaned['Topic'] = topics # 將主題標籤加入清理後的資料中

# 按主題分組，並計算每個主題的平均情感分數
topic_sentiment = df_cleaned.groupby('Topic').agg({
    'Pos_Sentiment': 'mean',
    'Neu_Sentiment': 'mean',
    'Neg_Sentiment': 'mean',
    'Compound_Sentiment': 'mean'
}).reset_index()
topic_sentiment = topic_sentiment[topic_sentiment['Topic'] != -1] # 確保過濾掉-1(雜訊資料)的主題
print(topic_sentiment) # 顯示每個主題的情感分數

# 保存處理完的輸出結果至MySQL
df_cleaned.to_sql('reddit_topic_sentiment_analysis', con=engine, if_exists='replace', index=False)

fig = topic_model.visualize_barchart(n_words=10, width=600, height=600) # 生成主題的長條圖

# 調整圖表
fig.update_layout(
    title='各主題的前10大代表詞之權重',
	  title_x=0.5,  # 標題置中
    title_font=dict(size=42)  # 設置字體大小
)
fig.write_image("代表詞.pdf", width=1700, height=810) # 存檔
fig.show() # 顯示圖表
