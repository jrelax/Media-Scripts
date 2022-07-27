import tmdbsimple as tmdb
import requests
from dotenv import load_dotenv
from alive_progress import alive_bar
from plexapi.server import PlexServer
import os
import sys
import textwrap
from tmdbapis import TMDbAPIs
import requests
import pathlib
from pathlib import Path
import platform
from timeit import default_timer as timer
import time

start = timer()

load_dotenv()

TMDB_KEY = os.getenv('TMDB_KEY')
POSTER_DIR = os.getenv('POSTER_DIR')
PERSON_DEPTH = 0
try:
    PERSON_DEPTH = int(os.getenv('PERSON_DEPTH'))
except:
    PERSON_DEPTH = 0


TMDb = TMDbAPIs(TMDB_KEY, language="en")

image_path = POSTER_DIR
people_name_file = 'people_names.txt'

items = []

people_file = Path(people_name_file)

if people_file.is_file():
    with open(f"{people_name_file}") as fp:
        for line in fp:
            items.append(line.strip())

idx = 1

def save_image(person, idx):

    file_root = f"{person.name}-{person.id}"

    if person.profile_url is not None:
        r = requests.get(person.profile_url)

        filepath = Path(f"{image_path}/{file_root}.jpg")
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with filepath.open("wb") as f:
            f.write(r.content)

item_total = len(items)
print(f"{item_total} item(s) retrieved...")
item_count = 1
with alive_bar(item_total, dual_line=True, title='TMDB people') as bar:
    for item in items:
        bar.text = f'->   starting: {item}'
        item_count = item_count + 1

        try:
            person = TMDb.person(int(item))
            bar.text = f"-> retrieving: {item}"
            save_image(person, 0)

        except ValueError:
            try:
                results = TMDb.people_search(str(item))
                if not results:
                    bar.text = f'->  NOT FOUND: {item}'
                    continue

                idx = 0
                UPPER = PERSON_DEPTH

                if len(results) < PERSON_DEPTH:
                    UPPER = len(results)

                for i in range(0,UPPER):
                    try:
                        person = results[i]
                        idx = idx + 1
                        bar.text = f"-> retrieving: {idx}-{item}"
                        save_image(person, idx)

                    except Exception as ex:
                        print(f'->  exception: {item} - {ex.args[0]}')
            except Exception as ex:
                print(f'->  exception: {item} - {ex.args[0]}')

            bar()


