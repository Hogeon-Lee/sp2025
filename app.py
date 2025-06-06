from flask import Flask, render_template, jsonify, request
from ingredient_crud import ingredient_crud
from ai_menu_page import ai_menu
import pymysql

app = Flask(__name__)
app.register_blueprint(ingredient_crud, url_prefix='/')
app.register_blueprint(ai_menu, url_prefix='/')

def get_db():
    return pymysql.connect(
        host='127.0.0.1',
        # port=3306,
        user='root',
        password='root',   # 실제 DB 비밀번호로 변경
        db='mydb',
        charset='utf8'
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/month-stats')
def api_month_stats():
    db = get_db()
    cursor = db.cursor()
    # 월별 소비량
    cursor.execute("""
        SELECT YEAR(date) AS y, MONTH(date) AS m, SUM(amount) AS total
        FROM ingredient_logs
        WHERE type='소비'
        GROUP BY y, m
        ORDER BY y, m
    """)
    rows_consume = cursor.fetchall()
    # 월별 버린 양
    cursor.execute("""
        SELECT YEAR(date) AS y, MONTH(date) AS m, SUM(amount) AS total
        FROM ingredient_logs
        WHERE type='버림'
        GROUP BY y, m
        ORDER BY y, m
    """)
    rows_discard = cursor.fetchall()
    db.close()
    # 모든 연도-월 조합 라벨 만들기 (예: 2025년 1월 ~ 2025년 12월)
    labels = []
    consume_map = {}
    discard_map = {}
    for y, m, total in rows_consume:
        key = f"{y}년 {m}월"
        consume_map[key] = int(total)
        if key not in labels:
            labels.append(key)
    for y, m, total in rows_discard:
        key = f"{y}년 {m}월"
        discard_map[key] = int(total)
        if key not in labels:
            labels.append(key)
    labels = sorted(labels, key=lambda x: (int(x.split('년')[0]), int(x.split('년')[1].replace('월',''))))
    consume_data = [consume_map.get(label, 0) for label in labels]
    discard_data = [discard_map.get(label, 0) for label in labels]
    return jsonify({'labels': labels, 'consume': consume_data, 'discard': discard_data})


@app.route('/api/top-ingredients')
def api_top_ingredients():
    year = int(request.args.get('year', 2025))
    month = int(request.args.get('month', 5))
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT ingredient, SUM(amount) AS total
        FROM ingredient_logs
        WHERE type='소비' AND YEAR(date)=%s AND MONTH(date)=%s
        GROUP BY ingredient
        ORDER BY total DESC
        LIMIT 5
    """, (year, month))
    rows = cursor.fetchall()
    db.close()
    labels = [row[0] for row in rows]
    data = [int(row[1]) for row in rows]
    return jsonify({'labels': labels, 'data': data})

@app.route('/api/tag-stats')
def api_tag_stats():
    year = int(request.args.get('year', 2025))
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
        WHERE type='소비' AND YEAR(date)=%s AND MONTH(date)=%s
        GROUP BY ingredient
    """, (year, month))
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
