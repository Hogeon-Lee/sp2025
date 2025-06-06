from flask import Blueprint, request, jsonify, render_template
import pymysql
from datetime import datetime


ingredient_crud = Blueprint("ingredient_crud", __name__)

def get_db():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        db='mydb',
        charset='utf8'
    )

# 로그 추가
def insert_log(cursor, ingredient_id, name, log_type, amount):
    cursor.execute("""
        INSERT INTO ingredient_logs (ingredient_id, ingredient, type, amount, date)
        VALUES (%s, %s, %s, %s, CURDATE())
    """, (ingredient_id, name, log_type, amount))


@ingredient_crud.route("/ingredient-search")
def ingredient_search():
    return render_template("ingredient_search.html")

# 전체 목록 + 실시간 검색
@ingredient_crud.route("/api/ingredients")
def api_ingredients():
    query = request.args.get("q", "")
    db = get_db()
    cursor = db.cursor()
    sql = "SELECT id, name, expiration_date, quantity, type_tag FROM Ingredients"
    if query:
        sql += " WHERE name LIKE %s"
        cursor.execute(sql, ('%' + query + '%',))
    else:
        cursor.execute(sql)
    rows = cursor.fetchall()
    db.close()
    data = [
        {
            'id': r[0],
            'name': r[1],
            'expiration_date': r[2].strftime('%Y-%m-%d') if r[2] else None,
            'quantity': r[3],
            'type_tag': r[4]
        }
        for r in rows
    ]
    return jsonify(data)

# 신규 데이터 추가 (POST)
# 로그 작성하도록 수정
@ingredient_crud.route("/api/ingredients", methods=['POST'])
def add_ingredient():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    now = datetime.now().strftime("%Y-%m-%d")

    # 재료 추가
    cursor.execute(
        "INSERT INTO Ingredients (name, register_date, expiration_date, quantity, type_tag, status_tag) VALUES (%s, %s, %s, %s, %s, %s)",
        (data["name"], now, data.get("expiration_date"), data["quantity"], data["type_tag"], data.get("status_tag", ""))
    )
    ingredient_id = cursor.lastrowid

    # 로그 추가
    insert_log(cursor, ingredient_id, data["name"], "구매", data["quantity"])

    db.commit()
    db.close()
    return jsonify({'result': 'success'})


# 기존 데이터 수정 (PUT)
# 로그 추가한 버전
@ingredient_crud.route("/api/ingredients/<int:ingredient_id>", methods=['PUT'])
def edit_ingredient(ingredient_id):
    data = request.json
    db = get_db()
    cursor = db.cursor()

    # 현재 수량 가져오기
    cursor.execute("SELECT name, quantity FROM Ingredients WHERE id=%s", (ingredient_id,))
    result = cursor.fetchone()
    if not result:
        db.close()
        return jsonify({'result': 'not found'}), 404

    name, old_quantity = result
    new_quantity = data['quantity']
    diff = old_quantity - new_quantity

    # 수량 업데이트
    cursor.execute(
        "UPDATE Ingredients SET name=%s, expiration_date=%s, quantity=%s, type_tag=%s, status_tag=%s WHERE id=%s",
        (data['name'], data['expiration_date'], new_quantity, data['type_tag'], data['status_tag'], ingredient_id)
    )

    # 로그 기록 (소비 or 버림만)
    if data['status_tag'] in ['consumed', 'discarded'] and diff > 0:
        log_type = '소비' if data['status_tag'] == 'consumed' else '버림'
        insert_log(cursor, ingredient_id, data['name'], log_type, diff)

    db.commit()
    db.close()
    return jsonify({'result': 'success'})


# 데이터 삭제 (DELETE)
@ingredient_crud.route("/api/ingredients/<int:ingredient_id>", methods=['DELETE'])
def delete_ingredient(ingredient_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Ingredients WHERE id=%s", (ingredient_id,))
    db.commit()
    db.close()
    return jsonify({'result': 'success'})
