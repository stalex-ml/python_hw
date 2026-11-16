import time
import json
import requests
import schedule
from bs4 import BeautifulSoup

def get_book_data(book_url: str) -> dict:
    """
    Получает данные о книге по указанному URL.

    Функция выполняет GET-запрос по указанному URL, парсит HTML-страницу
    и извлекает основную информацию о книге: название, цену, рейтинг,
    количество в наличии, описание и таблицу Product Information.

    Args:
        book_url (str): Полный URL страницы книги.

    Returns:
        dict: Словарь с данными о книге. Содержит ключи:
            - 'title' (str): название книги;
            - 'price' (str): цена в фунтах (например, '£51.77');
            - 'rating' (str): рейтинг в виде слова ('One'..'Five');
            - 'availability' (str): количество в наличии
              (например, 'In stock (22 available)');
            - 'description' (str): описание книги (пустая строка, если нет);
            - 'product_information' (dict): характеристики из таблицы
              Product Information (ключ — название строки, значение — текст).
    """

    # НАЧАЛО ВАШЕГО РЕШЕНИЯ
    response = requests.get(book_url)
    response.encoding = "utf-8"

    # Проверка доступности страницы
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        # Название книги
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else None

        # Цена       
        price_tag = soup.find("p", class_="price_color")
        price = price_tag.get_text(strip=True) if price_tag else None

        # Рейтинг: класс вида "star-rating Three"
        rating = None
        rating_tag = soup.find("p", class_="star-rating")
        if rating_tag:
            classes = rating_tag.get("class", [])
            for c in classes:
                if c != "star-rating":
                    rating = c
                    break

        # Наличие
        availability_tag = soup.find("p", class_="instock availability")
        availability = availability_tag.get_text(strip=True) if availability_tag else None

        # Описание: параграфы сразу после заголовка "Product Description"
        description = ''
        desc_header = soup.find("div", id="product_description")
        if desc_header:
            desc_paragraph = desc_header.find_next_sibling("p")
            if desc_paragraph:
                description = desc_paragraph.get_text(strip=True)
        
        # Таблица Product Information
        product_information = {}
        table = soup.find("table", class_="table table-striped")
        if table:
            rows = table.find_all("tr")
            for row in rows:
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    key = th.get_text(strip=True)
                    value = td.get_text(strip=True)
                    product_information[key] = value                   

        # Возврат результата
        return {
            "title": title,
            "price": price,
            "rating": rating,
            "availability": availability,
            "description": description,
            "product_information": product_information,
        }

    else:
        # Возврат результата, если страница не доступна
        return f'Ошибка {response.status_code} при загрузке страницы: {book_url}'

def scrape_books(is_save: bool = False) -> list:
    """
    Собирает ссылки на страницы всех книг из каталога.

    Проходит по страницам каталога вида
    'http://books.toscrape.com/catalogue/page-{N}.html',
    до ошибки 404 (страница не найдена).
    
    Args:
        is_save (bool): аргумент-флаг, если он будет равен `True`, то информация сохранится
                в ту же папку в файл `books_data.txt`; иначе шаг сохранения будет пропущен.
    
    Returns:
        list[str]: список книг со всеми их данными.
    """

    # НАЧАЛО ВАШЕГО РЕШЕНИЯ
    books_data = []
    page_number = 1

    # Бесконечный список до ошибки 404
    while True:
        page_url = f'http://books.toscrape.com/catalogue/page-{page_number}.html'
        response = requests.get(page_url)
        response.encoding = "utf-8"

        if response.status_code == 404:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        
        # На странице каталога каждая книга представлена ссылкой в <h3><a>
        book_links = soup.select("h3 a")
        if book_links:
            for link in book_links:
                href = link["href"]
                if not href:
                    continue
           
                book_url = f'http://books.toscrape.com/catalogue/{href}'
                book_info = get_book_data(book_url)
                books_data.append(book_info)
        
        page_number += 1

    # Сохранение списка с информацией о книгах в файл
    if is_save:
        with open("artifacts/books_data.txt", "w", encoding="utf-8") as file:
            for book in books_data:
                file.write(json.dumps(book, ensure_ascii=False) + "\n")

    return books_data

schedule.every().day.at("19:00").do(scrape_books, is_save=True)
print("Планировщик запущен. Задача будет выполняться ежедневно в 19:00.")

while True:
    schedule.run_pending()
    time.sleep(30)