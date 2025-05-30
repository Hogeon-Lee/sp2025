from flask import Flask, render_template, jsonify, request
import pymysql

app = Flask(__name__)

def get_db():
    return pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='password',
        db='mydb',
        charset='utf8'
    )

@app.route('/')
def index():
    return render_template('index.html')

# 월별 소비량 (1~12월)
@app.route('/api/month-stats')
def api_month_stats():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT MONTH(date) AS m, SUM(amount) AS total
        FROM ingredient_logs
        WHERE type='소비'
        GROUP BY m
        ORDER BY m
    """)
    rows = cursor.fetchall()
    db.close()
    # 1~12월 데이터로 맞추기
    month_totals = [0]*12
    for m, total in rows:
        month_totals[m-1] = int(total)
    return jsonify({'data': month_totals})

# 제일 많이 쓴 재료 (특정 월)
@app.route('/api/top-ingredients')
def api_top_ingredients():
    month = int(request.args.get('month', 5))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT ingredient, SUM(amount) AS total
        FROM ingredient_logs
        WHERE type='소비' AND MONTH(date)=%s
        GROUP BY ingredient
        ORDER BY total DESC
        LIMIT 5
    """, (month,))
    rows = cursor.fetchall()
    db.close()
    labels = [row[0] for row in rows]
    data = [int(row[1]) for row in rows]
    return jsonify({'labels': labels, 'data': data})

# 태그별 사용량 (예시: 태그는 ingredient별로 미리 지정)
@app.route('/api/tag-stats')
def api_tag_stats():
    month = int(request.args.get('month', 5))
    tag_map = {
        '참치캔': '통조림',
        '우유': '유제품',
        '계란': '유제품',
        '치즈': '유제품',
        '소고기': '고기',
        '돼지고기': '고기',
        '사과': '과일',
        '배': '과일'
    }
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT ingredient, SUM(amount) AS total
        FROM ingredient_logs
        WHERE type='소비' AND MONTH(date)=%s
        GROUP BY ingredient
    """, (month,))
    rows = cursor.fetchall()
    db.close()
    tag_totals = {}
    for ing, total in rows:
        tag = tag_map.get(ing, '기타')
        tag_totals[tag] = tag_totals.get(tag, 0) + int(total)
    labels = list(tag_totals.keys())
    data = list(tag_totals.values())
    return jsonify({'labels': labels, 'data': data})

if __name__ == '__main__':
    app.run(debug=True)
