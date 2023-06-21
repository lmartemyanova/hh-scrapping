import re
import time

import requests
from bs4 import BeautifulSoup
import fake_useragent
from tqdm import tqdm


def get_vacancies(text):
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
        vacancies = []
        for page in tqdm(range(pages_count)):
            response = requests.get(
                url=f'https://hh.ru/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text={text}&customDomain=1&page={page}',
                headers=headers
            )
            if response.status_code != 200:
                continue
            try:
                soup = BeautifulSoup(response.content, 'lxml')
                for i in soup.find_all('div', class_='serp-item'):
                    link = f'{i.find("a", class_="serp-item__title")["href"]}'
                    check_desc = check_description(link)
                    if check_desc is None:
                        continue
                    position = i.find('h3', class_="bloko-header-section-3").text
                    salary = i.find('span', class_="bloko-header-section-3")
                    try:
                        salary = salary.text
                    except AttributeError:
                        salary = 'не указано'
                    company = i.find('div', class_="vacancy-serp-item__meta-info-company").text
                    city = i.find('div', attrs={'data-qa': "vacancy-serp__vacancy-address"}).text
                    vacancy = {
                        'position': position,
                        'link': link,
                        'company': company,
                        'city': city,
                        'salary': salary
                    }
                    vacancies.append(vacancy)
            except Exception as e:
                print(f'{e}')
            time.sleep(1)
    return vacancies


def check_description(link):
    fake_user = fake_useragent.UserAgent()
    headers = fake_user.random
    response = requests.get(
        url=link,
        headers={'user-agent': headers}
    )
    if response.status_code != 200:
        print(f"Ошибка {response.status_code}")
        return
    try:
        soup = BeautifulSoup(response.content, 'lxml')
        description = soup.find('div', class_='g-user-content').text
        if 'django' not in description.lower() \
                and 'flask' not in description.lower():
            return
    except Exception:
        return
    time.sleep(1)
    return link


def clean_string(string):
    cleaned_string = re.sub(r'\u00A0|\u202F', ' ', string)
    return cleaned_string.strip()


def clean_vacancy(vacancy):
    position = clean_string(vacancy['position'])
    link = vacancy['link']
    company = clean_string(vacancy['company'])
    city = clean_string(vacancy['city'])
    salary = clean_string(vacancy['salary'])
    vacancy = {
        'position': position,
        'link': link,
        'company': company,
        'city': city,
        'salary': salary
    }
    return vacancy
