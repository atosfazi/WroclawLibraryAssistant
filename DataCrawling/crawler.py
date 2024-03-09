import os.path
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import json
import re
import time
import random


def extract_book_details(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    title = soup.find('h1', class_='book__title').text
    author = soup.find('a', class_='link-name d-inline-block').text
    tags = soup.find_all('a', class_='btn btn-outline-primary tag mt-2 mb-0')
    tags = [tag.text.strip() for tag in tags]
    tags = '|'.join(tags)
    description = soup.find('div', class_='collapse-content').text
    rating = soup.find('span', class_='big-number').text
    section = soup.find('section', class_='rating rating--legacy')
    text_inside_section = section.get_text()
    # Use regular expression to find the desired text within the extracted text
    ratings_nb = re.findall(r'\d+ ocen', text_inside_section)
    ratings_nb = ratings_nb[0].split(' ')[0]
    return title, author, tags, description, rating, ratings_nb


def get_books_category_urls(links_to_process, page_content, base_url, year):
    soup = BeautifulSoup(page_content, 'html.parser')
    links = [result for result in soup.find_all('a', class_='nav-link getDataToRewardList nav-years-categories')]
    links += [result for result in
              soup.find_all('a', class_='nav-link getDataToRewardList nav-years-categories active')]
    links = [link for link in links if link.get('data-category') != ""]
    category_names = [str(link.text) for link in links]
    links = [str(link.get('href')) for link in links]
    links = [f'{base_url}{link}' for link in links]
    for category, link in zip(category_names, links):
        record = {"Genre": category, "GenreResultsUrl": link}
        links_to_process[year].append(record)
    return links_to_process


def get_books_from_category(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    links = [result for result in soup.find_all('a', class_="book-url")]
    links = [str(link.get('href')) for link in links]
    links = list(set(links))
    return links


def save_ds_to_file(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        for dictionary in data:
            file.write(json.dumps(dictionary, ensure_ascii=False) + '\n')


def save_urls_to_file(links_to_process, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(links_to_process, file, ensure_ascii=False, indent=4)


def main():
    data = []
    years_to_process = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]
    base_url = 'https://lubimyczytac.pl'
    if os.path.exists('books_urls.json'):
        with open('books_urls.json', 'r', encoding='utf-8') as file:
            crawling_results = json.load(file)
    else:
        crawling_results = defaultdict(list)
        # get categories urls
        for year in years_to_process:
            url = f'{base_url}/plebiscyt{year}'
            response = requests.get(url)
            html_content = response.text
            crawling_results = get_books_category_urls(crawling_results, html_content, base_url, year)

        # get books urls
        for year, year_results in crawling_results.items():
            print(f'Processing data from year {year}')
            for genre_result in year_results:
                url = genre_result["GenreResultsUrl"]
                response = requests.get(url)
                html_content = response.text
                genre_books_urls = get_books_from_category(html_content)
                crawling_results[year][crawling_results[year].index(genre_result)]["BooksUrls"] = genre_books_urls

        # save urls to file
        save_urls_to_file(crawling_results, 'books_urls.json')

    # get books details
    keys = ['Year', 'Genre', 'BookUrl', 'Title', 'Author', 'Tags', 'Description', 'Rating', 'RatingsNb']
    for year, year_results in crawling_results.items():
        for genre_result in year_results:
            for book_url in genre_result["BooksUrls"]:
                url = f'{base_url}{book_url}'
                print(f'Processing {url}')
                try:
                    response = requests.get(url)
                    html_content = response.text
                    book_details = extract_book_details(html_content)
                    book_details = [year, genre_result["Genre"], url] + list(book_details)
                    book_details = dict(zip(keys, book_details))
                    data.append(book_details)
                    save_ds_to_file(data, 'awarded_books.json')
                    time.sleep(1)
                except Exception as e:
                    print('---------------------------------------------')
                    print(f'Error {e} occured while processing {url}')
                    print('---------------------------------------------')

    save_ds_to_file(data, 'awarded_books.json')


if __name__ == '__main__':
    main()
