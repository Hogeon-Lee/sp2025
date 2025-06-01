from flask import Blueprint, request, jsonify, render_template
import pymysql

ingredient_crud = Blueprint("ingredient_crud", __name__)

def get_db():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='happy0102',   # 실제 DB 비밀번호로 변경
        db='mydb',
        charset='utf8'
    )

@ingredient_crud.route("/ingredient-search")
def ingredient_search():
    return render_template("ingredient_search.html")

# 전체 목록 + 실시간 검색
@ingredient_crud.route("/api/ingredients")
def api_ingredients():
    query = request.args.get("q", "")
    db = get_db()
    cursor = db.cursor()
    sql = "SELECT id, ingredient, date, amount, type, consumed_amount, discarded_amount FROM ingredient_logs"
    if query:
        sql += " WHERE ingredient LIKE %s"
        cursor.execute(sql, ('%' + query + '%',))
    else:
        cursor.execute(sql)
    rows = cursor.fetchall()
    db.close()
    data = [
        {
            'id': r[0],
            'ingredient': r[1],
            'date': r[2].strftime('%Y-%m-%d') if hasattr(r[2], 'strftime') else str(r[2]),
            'amount': r[3],
            'type': r[4],
            'consumed_amount': r[5],
            'discarded_amount': r[6]
        }
        for r in rows
    ]
    return jsonify(data)

# 신규 데이터 추가 (POST)
@ingredient_crud.route("/api/ingredients", methods=['POST'])
def add_ingredient():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO ingredient_logs (ingredient, date, amount, type, consumed_amount, discarded_amount) VALUES (%s, %s, %s, %s, %s, %s)",
        (data['ingredient'], data['date'], data['amount'], data['type'], data.get('consumed_amount', 0), data.get('discarded_amount', 0))
    )
    db.commit()
    db.close()
    return jsonify({'result': 'success'})

# 기존 데이터 수정 (PUT)
@ingredient_crud.route("/api/ingredients/<int:log_id>", methods=['PUT'])
def edit_ingredient(log_id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE ingredient_logs SET ingredient=%s, date=%s, amount=%s, type=%s, consumed_amount=%s, discarded_amount=%s WHERE id=%s",
        (data['ingredient'], data['date'], data['amount'], data['type'], data.get('consumed_amount', 0), data.get('discarded_amount', 0), log_id)
    )
    db.commit()
    db.close()
    return jsonify({'result': 'success'})

# 데이터 삭제 (DELETE)
@ingredient_crud.route("/api/ingredients/<int:log_id>", methods=['DELETE'])
def delete_ingredient(log_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM ingredient_logs WHERE id=%s", (log_id,))
    db.commit()
    db.close()
    return jsonify({'result': 'success'})
