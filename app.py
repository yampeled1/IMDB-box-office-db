from selenium import webdriver
from elasticsearch import Elasticsearch
import time
import datetime

driver = webdriver.Chrome()
driver.set_page_load_timeout(10)

def get_movies_url():
    driver.get("https://www.imdb.com/")
    for element in driver.find_elements_by_class_name('aux-content-widget-2'):
        if 'Now Playing' in element.text:
            movies_url_list = list()
            for box_office_element in element.find_elements_by_class_name('title'):
                movie_name_with_gross = box_office_element.text
                index = movie_name_with_gross.find('$')
                movie_title = movie_name_with_gross[0:(index - 1)]
                movies_url_list.append(box_office_element.find_element_by_link_text(movie_title).get_attribute('href'))

    for movie in movies_url_list:
        get_movie_info(movie)
    time.sleep(10)
    driver.quit()

def get_movie_info(movie):
    # Moving to the movie-url
    driver.get(movie)
    movie_info = str(driver.find_element_by_class_name('title_block').text)
    # Splits the string to list divided by newline
    movie_info = movie_info.split('\n')
    # Removing Rate this from the info
    movie_info.remove('Rate This')
    # Removing the 'x | y | z ' criteria from the list
    more_info = str(movie_info.pop())
    # Splits the string to list divided '|'
    more_info = more_info.split('|')
    # Unify all the info about the movie
    movie_info.extend(more_info)
    create_json_format(movie_info)

def create_json_format(movie_info):
    movie_doc = {
              "movie_name": movie_info[2],
              "genre": movie_info[5],
              "score": movie_info[0],
              "length": movie_info[4],
              "release_date": movie_info[6],
              "parental_guide": movie_info[3],
              "users_voted": movie_info[1]
        }
    insert_to_es(movie_doc)

def insert_to_es(json_doc):
    now = datetime.datetime.now()
    now.strftime("%Y-%m-%d")
    index_name = now.strftime("%Y-%m-%d-") + 'box-office-hits'
    es = Elasticsearch([{'host': '100.26.188.28', 'port': 9200}])
    res = es.index(index=index_name, doc_type='movie', body=json_doc)
    print(res)


if __name__ == '__main__':
    get_movies_url()
