# 資料來源:Reddit
import praw
import mysql.connector
import os
import time
import re
from datetime import datetime, timezone
from praw.exceptions import ClientException


# 連接MySQL資料庫
db = mysql.connector.connect(
    host = "localhost", 
    port = 3306,
    user = "root", 
    password = "passwords"
)
cursor = db.cursor()

# 創建資料庫
cursor.execute("CREATE DATABASE IF NOT EXISTS reddit;")

PROGRESS_FILE = "fetch_progress.txt" # 進度文件

# 讀取進度文件
def load_last_progress():
    if os.path.exists(PROGRESS_FILE):
        print(f"進度文件 '{PROGRESS_FILE}' 存在，嘗試讀取...")
        try:
            with open(PROGRESS_FILE, "r") as f:
                lines = f.readlines()
                
                # 確保進度文件有兩行
                if len(lines) < 2:
                    print("進度文件格式錯誤，將從頭開始抓取。")
                    return None, 0  # 表示從頭開始

                # 讀取並檢查 first line（last_submission）和 second line（total_comments_fetched）
                after = lines[0].strip() if lines[0].strip() else None
                total_comments_fetched = int(lines[1].strip()) if lines[1].strip().isdigit() else 0

                # 檢查 last_submission 是否有效
                if after is None or not isinstance(after, str):
                    print("進度文件中的 last_submission 格式錯誤，將從頭開始抓取。")
                    return None, 0

                print(f"進度已讀取: {after}，已抓取留言數: {total_comments_fetched}")
                return after, total_comments_fetched
        except Exception as e:
            print(f"讀取進度文件時發生錯誤: {e}")
            return None, 0  # 返回預設值，表示從頭開始抓取
    else:
        print(f"進度文件 '{PROGRESS_FILE}' 不存在，從頭開始抓取。")
        return None, 0  # 如果進度文件不存在，返回預設值

# 存取進度文件
def save_progress(last_submission_full_name, total_comments_fetched):
    try:
        with open(PROGRESS_FILE, "w") as f:
            f.write(f"{last_submission_full_name}\n{total_comments_fetched}")
        print(f"進度已保存: {last_submission_full_name}，已抓取留言數: {total_comments_fetched}")
    except Exception as e:
        print(f"保存進度時發生錯誤: {e}")

cursor.execute("USE reddit;")

# 創建表格
cursor.execute("""
    CREATE TABLE IF NOT EXISTS reddit_table (
        comment_id VARCHAR(255), # 留言的識別碼
        post_title VARCHAR(1024), # 貼文標題
        subreddit VARCHAR(255), # 討論版名稱
        author VARCHAR(255), # 作者
        body TEXT, # 留言的內容
        created_utc DATETIME, # 創建時間
        score INT, # 分數 (類似於讚數)
        UNIQUE (comment_id)  # comment_id設置為唯一索引
    );
""")

# Reddit API的連接設置 
reddit = praw.Reddit(
    client_id = 'sQWu6dHo5V_BQ7crFXROKw',
    client_secret = 'zPDUvfBfuHIqn94rPWKPaXO02RYzeg',
    username = 'Pitiful_Box_6265',
    user_agent = 'my_reddit_app/1.0_Pitiful_Box_6265'
)

# 欲搜尋的所有關鍵字
keywords = ["automated ball-strike", "automated strike zone", "Electronic strike zone", "Automated pitch call",
            "Automatic Ball-Strike", "strike zone automation", "robotic strike zone", "AI strike zone", "automatic strike zone",
            "automated ball strike", "Automatic Ball Strike", "electronic ball strike", "electronic ball-strike", "robotic ball strike",
            "automatic ball/strike", "Automatic ball/strike", "electronic ball/strike", "robotic ball/strike", "robotic ball-strike"]

# 將關鍵字列表轉換為正規表達式，以確保完整匹配任何一個關鍵字
regex = r"\b(" + "|".join(map(re.escape, keywords)) + r")\b"

# 抓取Reddit任一討論版的數據
def fetch_comments(subreddit, keywords, regex):
    comments_data = [] # 儲存數據
    last_submission_full_name, total_comments_fetched = load_last_progress() # 讀取進度

    # 根據關鍵字於指定討論版搜尋所有相關貼文
    for submission in subreddit.search(" OR ".join(keywords), time_filter='all', limit=None, params={"after": last_submission_full_name}):
        try:
            post_title = submission.title # 貼文標題
            created_time = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc) # 貼文的創建時間

            #  檢查貼文標題是否完整匹配關鍵字(不分大小寫)
            if re.search(regex, post_title, re.IGNORECASE): 
                post_data = (
                    submission.id,  # submission.id為唯一索引
                    post_title,
                    submission.subreddit.display_name,
                    submission.author.name if submission.author else 'deleted', # 處理作者(帳號)刪除的情況
                    submission.selftext,  # 貼文內容
                    created_time.strftime('%Y-%m-%d %H:%M:%S'),
                    submission.score
                )
                # 將貼文所有數據視為一筆資料
                comments_data.append(post_data)
                total_comments_fetched += 1         
            
                submission.comments.replace_more(limit=None)  # 抓取所有留言
                comments = submission.comments.list()  # 將根留言和所有回覆合併為單一列表，利於處理所有的留言

                # 處理每一筆留言
                for comment in comments:
                    if isinstance(comment, praw.models.Comment): # 檢查是否為Reddit留言
                        comment_data = (
                            comment.id,
                            post_title,
                            submission.subreddit.display_name,  # 討論版名稱
                            comment.author.name if comment.author else 'deleted',
                            comment.body,
                            created_time.strftime('%Y-%m-%d %H:%M:%S'),
                            comment.score
                        )
                        # 儲存數據
                        comments_data.append(comment_data)
                        total_comments_fetched += 1

                        # 爬取留言的每一筆回覆
                        if comment.replies:
                            for reply in comment.replies.list():  # 利於處理所有回復
                                if isinstance(reply, praw.models.Comment):
                                    comment_data_reply = (
                                        reply.id,
                                        post_title,
                                        submission.subreddit.display_name,
                                        reply.author.name if reply.author else 'deleted',
                                        reply.body,
                                        created_time.strftime('%Y-%m-%d %H:%M:%S'),
                                        reply.score
                                    )
                                    comments_data.append(comment_data_reply)
                                    total_comments_fetched += 1
                            print(f"已抓取留言來自貼文: '{submission.title}'")
            print(f"目前已抓取留言總數: {total_comments_fetched}")
            
            # 更新last_submission_full_name為當前抓取的最後一篇submission的full_name
            last_submission_full_name = submission.fullname
            print(f"最後抓取的提交 full_name: {last_submission_full_name}")

            # 儲存進度
            save_progress(last_submission_full_name, total_comments_fetched)
                     
             # 根據 Reddit API 返回的剩餘請求數量動態調整延遲時間
            remaining_requests = reddit.auth.limits['remaining']  # 獲取剩餘的API請求數
            print(f"剩餘 API 請求數量: {remaining_requests}")
            
            if remaining_requests < 10:  # 如果剩餘請求少於 10，則增加延遲
                sleep_time = 61  # 增加延遲時間，讓 Reddit API 重置
            else:
                sleep_time = 2  # 如果剩餘請求數量足夠，則保持較短的延遲
            time.sleep(sleep_time)  # 根據情況調整延遲時間
       # 錯誤處理     
        except ClientException as e:
            print(f"Reddit API error: {e}")
            time.sleep(120)
            continue
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    return comments_data

# 抓取指定討論版的資料
comments_data = []
comments_data += fetch_comments(reddit.subreddit("all"), keywords, regex) # 爬取所有討論版的資料
#comments_data += fetch_comments(reddit.subreddit("baseball"), keywords, regex)
#comments_data += fetch_comments(reddit.subreddit("mlb"), keywords, regex)

# 分批插入資料
batch_size = 1000
total_inserted = 0  # 計算總插入筆數
for i in range(0, len(comments_data), batch_size):
    batch = comments_data[i:i+batch_size]
    try:
        cursor.executemany("""
            INSERT INTO reddit_table (comment_id, post_title, subreddit, author, body, created_utc, score)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE # 根據表格欄位comment_id檢查並避免重複爬取重複的資料
            post_title = VALUES(post_title),
            subreddit = VALUES(subreddit),
            author = VALUES(author),
            body = VALUES(body),
            created_utc = VALUES(created_utc),
            score = VALUES(score);
        """, batch)
        db.commit()
        total_inserted += len(batch)  # 更新總插入筆數
        print(f"Inserted {len(batch)} comments into the database.")
   # 錯誤處理
    except mysql.connector.Error as err:
        print(f"Error inserting batch: {err}")
        db.rollback()
# 最後輸出總共插入的筆數
print(f"Total inserted comments: {total_inserted}")

# 結束
print("Reddit comments extraction completed.")

cursor.close()
db.close()
