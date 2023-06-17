import time
import json

import requests
from bs4 import BeautifulSoup
import fake_useragent


def get_html(text):
    fake_headers = fake_useragent.UserAgent()
    headers = {'user-agent': fake_headers.random}
    response = requests.get(
        url=f'https://hh.ru/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text={text}&customDomain=1&page=1',
        headers=headers
    )
    if response.status_code != 200:
        print(f"Ошибка {response.status_code}")
        return
    else:
        soup = BeautifulSoup(response.content, 'lxml')
        try:
            pages_count = int(soup.find('div', class_='pager').find_all('span', recursive=False)[-1].find('a').find('span').text)
        except Exception:
            return
        vacancies = {}
        for page in range(pages_count):
            response = requests.get(
                url=f'https://hh.ru/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text={text}&customDomain=1&page={page}',
                headers=headers
            )
            if response.status_code != 200:
                continue
            try:
                soup = BeautifulSoup(response.content, 'lxml')
                # for name in soup.find_all(''):
                #     print()
                # for description in soup.find_all(''):
                #     if 'django' in description.lower() or 'flask' in description.lower():
                #
                for link in soup.find_all('a', class_='serp-item__title'):
                    link = f'{link["href"]}'
                    print(link)
            except Exception as e:
                print(f'{e}')
            time.sleep(1)
    return vacancies


def write_json(vacancies):
    with open ('vacancies.json', 'w') as f:
        json.dumps(vacancies)
        return


if __name__ == "__main__":
    get_html('python')
