from flask import Blueprint, request, jsonify, render_template
import openai
import datetime
import re
import ast
import pymysql

ai_menu = Blueprint('ai_menu', __name__)


# 최신 OpenAI 클라이언트 (예: openai.OpenAI())
client = openai.OpenAI(api_key='sk')

@ai_menu.route('/ai-menu')
def index():
    # TODO: DB에서 메뉴 불러오기
    # if db_has_data:
    #     return render_template('result.html', ...)
    # else:
    return render_template('ai_menu_empty.html')

@ai_menu.route('/recommend', methods=['POST'])
def recommend():
    # 예시 데이터 → 나중에 DB 저장
    ingredient_dict = {
        '토마토': (2, 1),
        '감자': (5, 10),
        '당근': (3, 5),
        '콜리플라워': (7, 3),
        '올리브유': (30, 1),
        '깨소금': (20, 2),
        '쌀': (365, 5),
    }

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

        f"반환 형식은 아래 별 3개(***) 안의 예시와 동일하게 주석없이 6개의 값을 작성할 것.\n\n"
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

        # 정규표현식으로 파싱
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
                    try:
                        value = ast.literal_eval(value)
                    except Exception:
                        value = []
                parsed[key] = value
            else:
                parsed[key] = None

        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # TODO: DB에서 기존 메뉴 삭제
        # TODO: DB에 parsed + update_time 저장

        return render_template('ai_menu_result.html',
                               update_time=update_time,
                               menu1_name=parsed['menu1_name'],
                               menu1_ingredients=parsed['menu1_ingredients'],
                               menu1_desc=parsed['menu1_desc'],
                               menu2_name=parsed['menu2_name'],
                               menu2_ingredients=parsed['menu2_ingredients'],
                               menu2_desc=parsed['menu2_desc'])

    except Exception as e:
        return jsonify({'error': str(e)}), 500

