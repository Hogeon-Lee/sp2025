from flask import Blueprint, request, jsonify, render_template
import openai
import datetime
import re
import ast
import pymysql

ai_menu = Blueprint('ai_menu', __name__)

client = openai.OpenAI(api_key='__')

def get_db():
    return pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='root',
        db='mydb',
        charset='utf8'
    )

@ai_menu.route('/ai-menu')
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT ai_update_time, ai_recommendation FROM Ingredients WHERE ai_recommendation IS NOT NULL ORDER BY ai_update_time DESC LIMIT 1")
    result = cursor.fetchone()
    db.close()

    if result:
        update_time, recommendation = result
        try:
            parsed = ast.literal_eval(recommendation)
            return render_template('ai_menu_result.html',
                                   update_time=update_time.strftime('%Y-%m-%d %H:%M'),
                                   menu1_name=parsed['menu1_name'],
                                   menu1_ingredients=parsed['menu1_ingredients'],
                                   menu1_desc=parsed['menu1_desc'],
                                   menu2_name=parsed['menu2_name'],
                                   menu2_ingredients=parsed['menu2_ingredients'],
                                   menu2_desc=parsed['menu2_desc'])
        except Exception as e:
            return jsonify({'error': '파싱 오류', 'detail': str(e)}), 500
    else:
        return render_template('ai_menu_empty.html')

@ai_menu.route('/recommend', methods=['POST'])
def recommend():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT name, expiration_date, quantity FROM Ingredients")
    rows = cursor.fetchall()

    if not rows:
        db.close()
        return render_template('ai_menu_empty.html', message='재료가 없어요!')

    now = datetime.datetime.now().date()
    ingredient_dict = {}
    for name, exp_date, qty in rows:
        if exp_date:
            days_left = (exp_date - now).days
        else:
            days_left = 9999
        ingredient_dict[name] = (days_left, qty)

    prompt = (
        f"식재료_딕셔너리:\n"
        f"{ingredient_dict}\n\n"
        f"각 항목의 튜플은 (남은 유통기한(일), 현재 수량) 의미야.\n"
        f"이 재료들을 활용해서 만들 수 있는 요리 2개를 추천해줘.\n\n"
        f"조건:\n"
        f"- 메뉴 1은 유통기한이 얼마 남지 않은 재료를 위주로 추천할 것.\n"
        f"- 메뉴 2는 수량이 많이 남은 재료를 위주로 추천할 것.\n"
        f"- 모든 재료를 다 사용할 필요는 없음.\n"
        f"- 각각 요리명(string), 사용 재료(list), 요리 소개(string)을 포함할 것.\n"
        f"- 요리 소개에는 수량과 유통기한을 언급하지 말 것.\n"
        f"- 요리명은 10글자 이내, 요리 소개는 15자 이상 30자 이내로 할 것.\n\n"
        f"***\n"
        f"메뉴1_요리명 = '브로콜리 무침'\n"
        f"메뉴1_사용재료 = ['브로콜리', '올리브유', '소금', '깨']\n"
        f"메뉴1_요리소개 = '브로콜리를 데쳐 소금과 올리브유로 버무린 건강 반찬'\n"
        f"메뉴2_요리명 = '감자 볶음'\n"
        f"메뉴2_사용재료 = ['감자', '올리브유', '소금', '후추']\n"
        f"메뉴2_요리소개 = '감자를 얇게 썰어 바삭하게 볶아낸 간단한 반찬'\n"
        f"***\n"
    )

    try:
        response = client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0
        )
        reply = response.choices[0].message.content

        patterns = {
            'menu1_name': r"메뉴1_요리명\s*=\s*['\"](.*?)['\"]",
            'menu1_ingredients': r"메뉴1_사용재료\s*=\s*(\[.*?\])",
            'menu1_desc': r"메뉴1_요리소개\s*=\s*['\"](.*?)['\"]",
            'menu2_name': r"메뉴2_요리명\s*=\s*['\"](.*?)['\"]",
            'menu2_ingredients': r"메뉴2_사용재료\s*=\s*(\[.*?\])",
            'menu2_desc': r"메뉴2_요리소개\s*=\s*['\"](.*?)['\"]",
        }

        parsed = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, reply, re.DOTALL)
            if match:
                value = match.group(1)
                if 'ingredients' in key:
                    value = ast.literal_eval(value)
                parsed[key] = value
            else:
                parsed[key] = None

        update_time = datetime.datetime.now()

        # DB에 모든 항목에 동일한 결과 저장 (가장 최근 것만 쓰기 때문)
        cursor.execute("UPDATE Ingredients SET ai_recommendation=%s, ai_update_time=%s", (str(parsed), update_time))
        db.commit()
        db.close()

        return render_template('ai_menu_result.html',
                               update_time=update_time.strftime('%Y-%m-%d %H:%M'),
                               menu1_name=parsed['menu1_name'],
                               menu1_ingredients=parsed['menu1_ingredients'],
                               menu1_desc=parsed['menu1_desc'],
                               menu2_name=parsed['menu2_name'],
                               menu2_ingredients=parsed['menu2_ingredients'],
                               menu2_desc=parsed['menu2_desc'])

    except Exception as e:
        return jsonify({'error': str(e)}), 500
