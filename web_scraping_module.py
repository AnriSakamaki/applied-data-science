from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException, TimeoutException
import time
from bs4 import BeautifulSoup
import re
import json

import database_module as dm

# SELENIUM SETUP
url = "https://www.imdb.com/list/ls053501318/"
options = Options()
options.headless = True
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(5)

def wait_until_clickable(parent, selector):
    button_element = parent.find_element(selector[0], selector[1])
    wait = True
    while wait:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button_element)
        time.sleep(1)
        try:
            button_element.click()
            time.sleep(1)
            wait = False
        except ElementClickInterceptedException as e:
            continue
        except ElementNotInteractableException as e:
            continue
            
def scrape_actors(url):
    driver.get(url)

    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5) 

    accept_button = driver.find_element(By.CSS_SELECTOR, '[data-testid="accept-button"]')
    accept_button.click()

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    actor_anchors = soup.find_all('a', class_='ipc-title-link-wrapper')

    actor_names = []
    actor_links = []
    for anchor in actor_anchors:
        name_anchor = anchor.find('h3', class_='ipc-title__text')
        name = name_anchor.get_text(strip=True) if name_anchor else "Unknown Actor"
        name = ' '.join(name.split(' ')[1:])
        if 'href' in anchor.attrs:
            actor_link = f"https://www.imdb.com{anchor['href']}"
            actor_links.append(actor_link)
            actor_names.append(name)
        else:
            print(f"Skipping actor '{name}' because link is not found.")

    return list(zip(actor_names, actor_links))

def scrape_actor_bio(actor_link, actor_name):
    '''
        For a given actor link return the bio
        Returns:
            str: actor_bio
    '''

    driver.get(actor_link)
    actor_html = driver.page_source
    actor_soup = BeautifulSoup(actor_html, 'html.parser')

    bio_div = actor_soup.find('div', class_='ipc-html-content-inner-div')
    actor_bio = bio_div.get_text(strip=True) if bio_div else "Biography not available."

    return actor_bio

def scrape_actor_movies(actor_link, actor_name):
    '''
        For a given actor returns all the movies he acted in.
        Returns:
            list[tuple]: [(movie_title, movie_sub_url), ...]
    '''
    driver.get(actor_link)

    actor_previous_projects = driver.find_elements(By.CSS_SELECTOR, '[id=actor-previous-projects]')
    if len(actor_previous_projects) == 0:
        actor_previous_projects = driver.find_elements(By.CSS_SELECTOR, '[id=actress-previous-projects]')
    actor_previous_projects = actor_previous_projects[0]
    actor_previous_projects_classes = actor_previous_projects.get_attribute('class')
    if 'collapsed' in str(actor_previous_projects_classes):
        wait_until_clickable(driver, (By.CSS_SELECTOR, f'[id={actor_previous_projects.get_attribute('id')}]'))
    else:
        while len(actor_previous_projects.find_elements(By.CSS_SELECTOR, '[class*="ipc-see-more__button"]')) > 0:
            wait_until_clickable(actor_previous_projects, (By.CSS_SELECTOR, '[class*="ipc-see-more__button"]'))

    actor_html = driver.page_source
    actor_soup = BeautifulSoup(actor_html, 'html.parser')

    movie_lis = actor_soup.find_all('li', class_='ipc-metadata-list-summary-item')
    movie_lis = [li for li in movie_lis if 'data-testid=\"cred_actor' in str(li) or 'data-testid=\"cred_actress' in str(li)]
    movies = []
    for movie_li in movie_lis:
        film_title_anchor = movie_li.find('a', class_="ipc-metadata-list-summary-item__t")
        film_title = film_title_anchor.decode_contents()
        film_title_href = film_title_anchor['href']
        film_title_url = f"https://www.imdb.com{film_title_href}"
        movies.append((film_title, film_title_url))
    return movies

def scrape_movie_metadata(movie_link, movie_title):
    '''
        For a given movie link we return the movie_year, movie_rating and movie_genres.
        Returns:
            tuple: (movie_year, movie_rating, [movie_genre, ...])
    '''
    driver.get(movie_link)

    movie_html = driver.page_source
    movie_soup = BeautifulSoup(movie_html, 'html.parser')

    genres_div = movie_soup.find('div', {'data-testid': "interests"})
    movie_genres = [anchor.find('span').decode_contents() for anchor in genres_div.find_all('a')]

    hero_page_title_h1 = movie_soup.find('h1', {'data-testid': "hero__pageTitle"})
    hero_page_title_h1_parent_div = hero_page_title_h1.parent
    pattern = re.compile(r"^/title/.*/releaseinfo/.*")
    year_anchor = hero_page_title_h1_parent_div.find('a', href=pattern)
    if year_anchor is not None:
        movie_year = year_anchor.decode_contents()[:4]
    else:
        movie_year = None

    rating_div = movie_soup.find('div', {'data-testid': "hero-rating-bar__aggregate-rating__score"})
    movie_rating = rating_div.find_all('span')[0].decode_contents() if rating_div is not None else 0

    return movie_year, movie_rating, movie_genres

def scrape_actor_awards(actor_link, actor_name):
    '''
        For a given actor returns the awards he got in respective years.
        Returns:
            list[tuple]: [(award_name, award_tag, award_category, award_year), ...]
    '''
    driver.get(actor_link)

    actor_html = driver.page_source
    actor_soup = BeautifulSoup(actor_html, 'html.parser')
    pattern = re.compile(r"^/name/.*/awards/.*")
    award_href = actor_soup.find('a', href=pattern)['href']
    award_url = f"https://www.imdb.com{award_href}"

    driver.get(award_url)

    award_html = driver.page_source
    award_soup = BeautifulSoup(award_html, 'html.parser')

    award_lis = award_soup.find_all('li', {'data-testid': "list-item"})
    actor_awards = []
    for award_li in award_lis:
        award_div = award_li.find('div', class_='ipc-metadata-list-summary-item__tc')
        award_anchor = award_div.find('a', class_='ipc-metadata-list-summary-item__t')
        award_year, award_tag = tuple(award_anchor.decode_contents().split('<span')[0].split(' '))
        award_name = award_anchor.find('span').decode_contents()
        award_category = award_div.find('span', class_='ipc-metadata-list-summary-item__li awardCategoryName')
        actor_awards.append((award_name, award_tag, award_category.decode_contents() if award_category is not None else "No Category", award_year))

    return actor_awards

if __name__ == '__main__':
    
    print('Scrape Actor Data:')
    result = dm.get_actor_links()
    actors_in_database = [(actor_name, actor_link) for _, actor_name, actor_link in result]
    for actor_index, (actor_name, actor_link) in enumerate(scrape_actors(url)):
        if (actor_name, actor_link) in actors_in_database:
            print(f'Skipping {actor_name}...')
            continue
        print(f'Scraping {actor_name}...')
        actor_bio = scrape_actor_bio(actor_link, actor_name)
        actor_id = dm.insert_actor_into_actors_table(actor_name, actor_bio, actor_link)

    print('Scrape Actor Award Data:')
    actors_in_actors = dm.get_actor_links()
    actors_in_awards = [actor_name for actor_name, in dm.get_actors_in_awards()]
    for actor_id, actor_name, actor_link in actors_in_actors:
        if actor_name in actors_in_awards:
            print(f'Skipping Awards for {actor_name}...')
            continue
        print(f'Scraping Awards for {actor_name}...')
        actor_awards = scrape_actor_awards(actor_link, actor_name)
        actor_awards = [ actor_award for actor_award in actor_awards if actor_award[1] == 'Winner']
        for award_name, award_tag, award_category, award_year in actor_awards:
            dm.insert_award_into_awards_table(actor_id, award_name, award_category, award_year)
    
    print('Scrape Actor Movie Data:')
    actors_in_actor_movie_staging = [actor_name for actor_name, in dm.get_actors_in_actor_movie_staging()]
    for actor_id, actor_name, actor_link in actors_in_actors:
        if actor_name in actors_in_actor_movie_staging:
            print(f'Skipping Movies for {actor_name}...')
            continue
        print(f'Scraping Movies for {actor_name}...')
        wait = True
        while wait:
            try:
                actor_movies = scrape_actor_movies(actor_link, actor_name)
                wait = False
            except StaleElementReferenceException as e:
                continue           
        for movie_name, movie_url in actor_movies:
            dm.insert_into_actor_movie_staging_table(actor_id, movie_name, movie_url)
        dm.conn.commit()

    print('Scrape Movie Data:')
    movies_in_movies = dm.get_all_movies()
    movie_urls_in_movies = [movie_url for _, _, movie_url in movies_in_movies]
    stg_in_actor_movie_staging = dm.get_all_actor_movie_staging_table()
    unique_movies_in_actor_movie_staging = list(set([(movie_name, movie_url) for _, movie_name, movie_url in stg_in_actor_movie_staging]))
    movies_to_scrape = [(movie_name, movie_url) for _, movie_name, movie_url in stg_in_actor_movie_staging if movie_url not in movie_urls_in_movies]
    for movie_index, (movie_name, movie_url) in enumerate(movies_to_scrape):
        print(f'Scraping Movie {movie_name}...')
        wait = True
        while wait:
            try:
                movie_year, movie_rating, movie_genres = scrape_movie_metadata(movie_url, movie_name)
                wait = False
            except TimeoutException as e:
                continue
        movie_id = dm.insert_movie_into_movies_table(movie_name, movie_rating, movie_year, ", ".join(movie_genres), movie_url)

    print('Insert played_in relations:')
    for movie_index, (actor_id, movie_name, movie_url) in enumerate(stg_in_actor_movie_staging):
        if movie_index % 25 == 0:
            print(f'{movie_index}/{len(stg_in_actor_movie_staging)}')
        movie_id = dm.get_movie_id(movie_url)[0]
        dm.insert_entry_in_played_in_table(actor_id, movie_id)

    dm.conn.commit()
    dm.conn.close()
    driver.quit()
