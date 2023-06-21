import re
import time
import json

import requests
from bs4 import BeautifulSoup
import fake_useragent


def cached(old_function):
    cache = {}

    def new_function(*args, **kwargs):
        key = f'{args}_{kwargs}'
        if key in cache:
            return cache[key]
        result = old_function(*args, **kwargs)
        cache[key] = result
        return result

    return new_function


@cached
def get_links(text):
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
            pages_count = int(
                soup.find('div', class_='pager').find_all('span', recursive=False)[-1].find('a').find('span').text)
        except Exception:
            return
        links = []
        for page in range(pages_count):
            response = requests.get(
                url=f'https://hh.ru/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text={text}&customDomain=1&page={page}',
                headers=headers
            )
            if response.status_code != 200:
                continue
            try:
                soup = BeautifulSoup(response.content, 'lxml')
                for link in soup.find_all('a', class_='serp-item__title'):
                    link = f'{link["href"]}'
                    links.append(link)
                    # print(link)
            except Exception as e:
                print(f'{e}')
            time.sleep(1)
    return links


def get_vacancies(links):
    fake_user = fake_useragent.UserAgent()
    headers = fake_user.random
    vacancies = []
    for link in links:
        response = requests.get(
            url=link,
            headers={'user-agent': headers}
        )
        if response.status_code != 200:
            print(f"Ошибка {response.status_code}")
            continue
        try:
            soup = BeautifulSoup(response.content, 'lxml')
            description = soup.find('div', class_='g-user-content').text
            if 'django' not in description.lower() \
                    and 'flask' not in description.lower():
                continue
            position = soup.find('div', class_='vacancy-title').find('h1', class_='bloko-header-section-1').text
            company = soup.find('div', class_='vacancy-company-details').find('span',
                                                                              class_='vacancy-company-name').text
            salary = soup.find('div', class_='vacancy-title').find('span',
                                                                   class_='bloko-header-section-2 bloko-header-section-2_lite').text
            if not salary:
                salary = "не указана"
            city = soup.find('div', class_='vacancy-company-redesigned').find("span", attrs={
                "data-qa": "vacancy-view-raw-address"}).text.split()[0].strip()
            city = re.search(r'\w+', city).group()
            if not city:
                city = "не указан"
            vacancy = {
                'link': link,
                'position': position,
                'company': company,
                'salary': salary,
                'city': city
            }
            vacancies.append(vacancy)
        except Exception as e:
            print(f'{e}')
        time.sleep(1)
    return vacancies


def write_json(vacancies):
    with open('vacancies.json', 'w') as f:
        json.dumps(vacancies, ensure_ascii=False)
        return


if __name__ == "__main__":
    links = get_links('python')
    print(get_vacancies(links))
