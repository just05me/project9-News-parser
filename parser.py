import requests
from bs4 import BeautifulSoup
import pandas as pd
import mysql.connector
from datetime import datetime

# Функция для парсинга
def get_news():
    url = "https://news.ycombinator.com/"
    
    response = requests.get(url)
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    news_list = []
    
    titles = soup.find_all("span", class_="titleline")
    scores = soup.find_all("span", class_="score")
    
    for i in range(min(len(titles), len(scores))):
        title = titles[i].text
        
        score = int(scores[i].text.replace(" points", ""))
        
        news_list.append({
            "title": title,
            "score": score,
            "date": datetime.now().strftime("%Y-%m-%d")
        })
    
    return news_list

# Функция для подключения к БД
def connect_to_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="itsmyfirstlinux",
        database="news_db"
    )

    cursor = db.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            score INT,
            date VARCHAR(50)
        )
    """)
    db.commit()
    
    return db, cursor

# Функция для сохранения данных
def save_news(news_list, cursor, db):
    for news in news_list:
        cursor.execute("INSERT INTO news (title, score, date) VALUES (%s, %s, %s)", (news["title"], news["score"], news["date"]))
    
    db.commit()

# Функция для анализа
def analyze_news(cursor):
    cursor.execute("SELECT date, score FROM news")

    data = cursor.fetchall()

    df = pd.DataFrame(data, columns=["date", "score"])

    news_per_day = df["date"].value_counts().to_dict()

    avg_score = df["score"].mean()

    return {"news_per_day": news_per_day, "average_score": avg_score}

# Главная функция
def main():
    news = get_news()
    
    db, cursor = connect_to_db()
    
    save_news(news, cursor, db)
    
    stats = analyze_news(cursor)
    
    print("Статистика:")
    
    print(f"Новостей по дням: {stats["news_per_day"]}")
    
    print(f"Средний рейтинг: {round(stats["average_score"], 1)}")
    
    db.close()

if __name__ == "__main__":
    main()