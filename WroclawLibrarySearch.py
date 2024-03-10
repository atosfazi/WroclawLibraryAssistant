import json
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep


def initialize_browser():
    options = Options()
    options.headless = True

    driver = webdriver.Chrome(options=options)
    return driver


def get_page_with_browser(url, driver):
    try:
        driver.get(url)
        sleep(3)
        page_content = driver.page_source
        return page_content

    finally:
        pass


def encode_polish_characters(text):
    text = text.strip()
    return quote(text, safe='')


def load_file(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        data = file.readlines()
    return data


def check_is_no_results_found(response_text):
    soup = BeautifulSoup(response_text, 'html.parser')
    header = soup.find('h2', class_='md-headline', string=re.compile('Nie znaleziono żadnych rekordów'))
    return header is not None


def get_direct_links(driver):
    attempts = 0
    while True:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        found_links = []
        links = soup.find_all('a', href=lambda href: href and href.startswith(
            "https://omnis-mbpwr.primo.exlibrisgroup.com/discovery/fulldisplay?docid"))

        for link in links:
            if link['href'] not in found_links:
                found_links.append(link['href'])
        if len(links) > 0 or attempts > 3:
            break
    return found_links


def check_title(driver, title):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    title_span = soup.find('span', attrs={'ng-bind-html': '$ctrl.highlightedText'})
    if title_span:
        found_title = ' / '.join(title_span.text.split('/')[:-1]).strip()
        found_title = ''.join(char for char in found_title if char.isalnum())
        title = ''.join(char for char in title if char.isalnum())
        if found_title.lower() != title.lower():
            return False
    return True


def get_books_accessibility(links, driver, title):
    due_date_text = ""
    availability_status = 0
    for url in links:
        get_page_with_browser(url, driver)
        if not check_title(driver, title):
            continue

        try:
            filia_27 = driver.find_element("xpath", '//div[h3[contains(text(), "27")]]')
            filia_27.click()
        except:
            show_more_button = driver.find_element("xpath", '//button[@aria-label="Pokaż więcej lokalizacji"]')
            show_more_button.click()
            filia_27 = driver.find_element("xpath", '//div[h3[contains(text(), "27")]]')
            filia_27.click()

        page_source_after_click = driver.page_source
        soup = BeautifulSoup(page_source_after_click, 'html.parser')
        element_filia_27 = soup.find('h3', string='27 - Łokietka')
        if element_filia_27:
            availability_span = element_filia_27.find_next_sibling('p').find('span', class_='availability-status')
            if availability_span:
                availability_status = availability_span.text.strip()
                print("Status dostępności w filii 27:", availability_status)
                availability_status = 1 if availability_status == "Dostępny" else 0

                if not availability_status:
                    try:
                        due_date = driver.find_element("xpath", '//span[@class="item-status"]')
                        due_date_text = due_date.text
                        print("Termin oddania:", due_date_text)
                    except:
                        print("Nie można znaleźć informacji o terminie oddania")
            else:
                print("Nie można znaleźć informacji o dostępności w filii 27")
        else:
            print("Nie znaleziono filii 27 na stronie")

    return availability_status, due_date_text


def main():
    file = 'dataset/awarded_books.json'
    search_link = "https://omnis-mbpwr.primo.exlibrisgroup.com/discovery/search?query=any,contains,{book_title}&tab=LibraryCatalog&search_scope=filia27&vid=48OMNIS_MBP:MBP&lang=pl&offset=0"
    driver = initialize_browser()
    data = load_file(file)

    for row in data:
        line = json.loads(row)
        original_title = line['Title']
        title = encode_polish_characters(line['Title'])

        url = search_link.format(book_title=title)
        response = get_page_with_browser(url, driver)

        if check_is_no_results_found(response):
            print(f"No results found for book: {original_title}")
        else:
            print(f"Results found for book: {original_title}")
            links = get_direct_links(driver)
            available, due_date = get_books_accessibility(links, driver, original_title)
            print(f'Book: {original_title}, available: {available}, due date: {due_date}')


main()
