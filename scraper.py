import time
import requests
import connector
from bs4 import BeautifulSoup
from song import Song

# TODO: Sometimes (probably on long song names) the Genius API returns wrong results even though the song
# is in the Genius system. Probalby the next step should be to just search by the song title.


def get_token():
    f = open('token.txt', 'r')
    token = f.read()
    return token


def get_lyrics(song_api_path, base_url, headers):
    song_url = base_url + song_api_path
    response = requests.get(song_url, headers=headers)
    json = response.json()
    path = json['response']['song']['path']

    page_url = 'http://genius.com' + path
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, 'html.parser')

    # remove script tags
    [h.extract() for h in html('script')]

    lyrics = html.find('div', class_='lyrics').get_text()
    return lyrics


def print_artist_and_title(song):
    print("\t\t" + song.artist.upper() + ' - ' + song.title.upper())


def get_genius_results(song, base_url, headers):
    token = get_token()

    print("token = " + token)

    base_url = "http://api.genius.com"
    headers = {'Authorization': 'Bearer ' + token}

    search_url = base_url + "/search"
    params = {'q': song.title + ' ' + song.artist}
    response = requests.get(search_url, params=params, headers=headers)
    json = response.json()
    return json


def verify_song(song, response):
    for hit in response["response"]["hits"]:
        if hit["result"]["primary_artist"]["name"] == song.artist:
            return hit
    return None


# this should probably be its own class
if __name__ == '__main__':

    # former connector logic
    scope = "user-read-currently-playing"

    song_fetcher = connector.SongFetcher(scope)
    most_recent_song = Song('', '')

    while True:
        current_song = song_fetcher.get_song()

        if (current_song is not None and current_song.title != most_recent_song.title):
            # call genius API
            most_recent_song = current_song

            response = get_genius_results(current_song)
            song_info = verify_song(current_song, response)

            # is the song is found
            if song_info:

                # print  'artist - title'
                print_artist_and_title(current_song)
                song_api_path = song_info['result']['api_path']

                print(get_lyrics(song_api_path))

            else:
                print("Song lyrics not found :-(")
        else:
            time.sleep(5)
