# IMDb Actors CLI Tool

A simple Python project that **scrapes actor data from IMDb**, stores it in a **SQLite database**, and provides a **command-line interface (CLI)** to explore that data (e.g., retrieve actor biographies, movies, awards, etc.).

---

## Project Structure

1. **Web Scraping Module** (`webscraping_module.py`)  
   - Uses **Selenium** & **BeautifulSoup** to scrape data (actors, their bios, movies, etc.) from IMDb.  
   - Inserts scraped data into the database via the **Database Module**.
   
2. **Database Module** (`database_module.py`)  
   - Creates and manages a **SQLite** database (`movies.db`).  
   - Functions for inserting and retrieving actors, awards, movies, and their relationships (through `played_in`).  
   - Can **reset** the database, creating fresh tables (`actors`, `awards`, `movies`, `played_in`, `actor_movie_staging`, etc.).

3. **User Interface Module** (`userinterface_module.py`)  
   - A **CLI interface** that processes user input and runs queries against the database.  
   - Supports commands like `--bio`, `--movies`, `--awards`, `--genres`, `--ratings`, `--topfive`, and `--actors`.  
   - Uses the **argparse** library to parse commands, and calls **Database Module** functions to fetch results.

---

## Requirements

- **Python 3.7+**
- **Selenium** (e.g., `pip install selenium`)
- **BeautifulSoup4** (e.g., `pip install beautifulsoup4`)
- **ChromeDriver** (matching your local Chrome version) or another WebDriver

Make sure your environment can run a headless Chrome (or any Selenium-supported browser).

---

## Quick Start

1. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   # Ensure you have ChromeDriver set up (or use another driver).

2. **Initialize the Database**  
   - Run `database_module.py` to create/reset the `movies.db` database and tables:
     ```bash
     python database_module.py
     ```
   - This sets up the `actors`, `awards`, `movies`, `played_in`, and `actor_movie_staging` tables.

3. **Run the Scraper**  
   - Execute `webscraping_module.py` to scrape IMDb data and populate your database:
     ```bash
     python webscraping_module.py
     ```
   - This will insert actor data, awards, movies, and relationships into the database.
   - Note this takes a long time so please use the already provided database in this repository. 

4. **Use the CLI**  
   - Run `userinterface_module.py` to explore data interactively:
     ```bash
     python userinterface_module.py
     ```
   - You’ll be prompted for input.  
   - For example, **list all actors**:
     ```
     Please provide a actors name or use --help...:
       None None --actors
     ```
   - **Get a specific actor’s biography**:
     ```
     Please provide a actors name...:
       Robert De Niro --bio
     ```
   - **Quit** the CLI by typing `Q`.

---

## Example Commands in the CLI

- **All Actors**  
  `None None --actors`

- **Actor Bio**  
  `[first_name] [last_name] --bio`

- **Actor Movies**  
  `[first_name] [last_name] --movies --limit 3` (show only 3 items)

- **Actor Awards**  
  `[first_name] [last_name] --awards`

- **Actor Genres**  
  `[first_name] [last_name] --genres`

- **Ratings & Yearly Averages**  
  `[first_name] [last_name] --ratings`

- **Top Five Movies**  
  `[first_name] [last_name] --topfive`
