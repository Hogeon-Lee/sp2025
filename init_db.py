import pymysql

# DB 접속
conn = pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='root',
    charset='utf8'
)
cursor = conn.cursor()

# 데이터베이스 생성 (없으면)
db_name = 'mydb'
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
print(f"Database '{db_name}' 생성(또는 이미 존재).")

# 새로 만든 DB로 접속 전환
cursor.execute(f"USE {db_name}")

# Ingredients 테이블 생성 (없으면)
create_table_query = """
CREATE TABLE IF NOT EXISTS Ingredients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    register_date DATE,
    quantity INT DEFAULT 0,
    type_tag VARCHAR(50),
    status_tag VARCHAR(50),
    expiration_date DATE,
    ai_recommendation TEXT,
    ai_update_time DATETIME
)
"""
cursor.execute(create_table_query)
print("Ingredients 테이블 생성(또는 이미 존재).")


create_logs_table = create_logs_table = """
CREATE TABLE ingredient_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_id INT,
    ingredient VARCHAR(255) NOT NULL,
    type ENUM('소비', '구매', '버림') NOT NULL,
    amount INT NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(id) ON DELETE SET NULL
)
"""

cursor.execute(create_logs_table)
print("ingredient_logs 테이블 생성(또는 이미 존재).")



conn.commit()
cursor.close()
conn.close()
