from flask import Blueprint, request, jsonify, render_template
import pymysql

ingredient_crud = Blueprint("ingredient_crud", __name__)

def get_db():
    return pymysql.connect(
        host='127.0.0.1', user='root', password='happy0102', db='mydb', charset='utf8'
    )

@ingredient_crud.route("/ingredient-search")
def ingredient_search():
    return render_template("ingredient_search.html")

@ingredient_crud.route("/api/ingredients")
def api_ingredients():
    query = request.args.get("q", "")
    db = get_db()
    cursor = db.cursor()
    sql = "SELECT id, ingredient, date, amount, type FROM ingredient_logs"
    if query:
        sql += " WHERE ingredient LIKE %s"
        cursor.execute(sql, ('%' + query + '%',))
    else:
        cursor.execute(sql)
    rows = cursor.fetchall()
    db.close()
    data = [
        {'id': r[0], 'ingredient': r[1], 'date': str(r[2]), 'amount': r[3], 'type': r[4]}
        for r in rows
    ]
    return jsonify(data)

@ingredient_crud.route("/api/ingredients", methods=['POST'])
def add_ingredient():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO ingredient_logs (ingredient, date, amount, type) VALUES (%s, %s, %s, %s)",
        (data['ingredient'], data['date'], data['amount'], data['type'])
    )
    db.commit()
    db.close()
    return jsonify({'result': 'success'})

@ingredient_crud.route("/api/ingredients/<int:log_id>", methods=['PUT'])
def edit_ingredient(log_id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE ingredient_logs SET ingredient=%s, date=%s, amount=%s, type=%s WHERE id=%s",
        (data['ingredient'], data['date'], data['amount'], data['type'], log_id)
    )
    db.commit()
    db.close()
    return jsonify({'result': 'success'})

@ingredient_crud.route("/api/ingredients/<int:log_id>", methods=['DELETE'])
def delete_ingredient(log_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM ingredient_logs WHERE id=%s", (log_id,))
    db.commit()
    db.close()
    return jsonify({'result': 'success'})
