import pytest
import scraper


BOOK_URL = (
    'http://books.toscrape.com/catalogue/'
    'a-light-in-the-attic_1000/index.html'
)

EXPECTED_KEYS = {
    'title',
    'price',
    'rating',
    'availability',
    'description',
    'product_information',
}

@pytest.fixture(scope='module')

# Один раз загружаем данные реальной книги.
def book() -> dict:
    return scraper.get_book_data(BOOK_URL)

# Данные о книге возвращаются словарём с нужными ключами.
def test_get_book_data_returns_dict_with_expected_keys(book):
    assert isinstance(book, dict)
    assert EXPECTED_KEYS.issubset(book.keys())

# Поле title содержит корректное название книги.
def test_get_book_data_title_is_correct(book):
    assert book['title'] == 'A Light in the Attic'

#При недоступной странице возвращается строка с текстом ошибки.
def test_get_book_data_returns_error_string_on_bad_url():
    
    bad_url = (
        'http://books.toscrape.com/catalogue/'
        'this-book-does-not-exist_9999/index.html'
    )
    result = scraper.get_book_data(bad_url)
    assert isinstance(result, str)
    assert 'Ошибка' in result
    assert '404' in result