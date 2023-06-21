from parser import get_vacancies, clean_vacancy
from hh_json import write_json


if __name__ == "__main__":
    vacancies = get_vacancies('python')
    clean_vacancies = [clean_vacancy(vacancy) for vacancy in vacancies]
    write_json(clean_vacancies)
