import json


def write_json(vacancies):
    with open('vacancies.json', 'w', encoding='utf-8') as f:
        json.dump(vacancies, f, indent=4, ensure_ascii=False)
        return
