import time
import requests
import connector
from bs4 import BeautifulSoup
from song import Song

# TODO: Sometimes (probably on long song names) the Genius API returns wrong results even though the song
# is in the Genius system. Probalby the next step should be to just search by the song title.

# TODO: Fix the reprs

# TODO: When song lyrics weren't found, it just kept printing the "no lyrics found" message. This happened with classical music. Address this.


def read_token():
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


"""
    Main class:
        Start of program
        Verifies connectivity with Spotify API (else errors out)
        Verifies connectivity with Genius API (else errors out)

        Runs main loop (ESC exits it) on a 5 second sleep interval:
            Call "connector" Spotify, get the currently playing song
            If there is such a song and it has not been displayed, send it to GeniusConnector, get the genius API path of the song
            If there is such an API path, send it to the LyricsParser class to get the lyrics
            If the LyricsParser class returns the lyrics, then print them

    I will do this when at home.
"""

# this should probably be its own class
if __name__ == '__main__':
    base_url = "http://api.genius.com"

    token = read_token()
    headers = {'Authorization': 'Bearer ' + token}

    scope = "user-read-currently-playing"
    song_fetcher = connector.SongFetcher(scope)
    most_recent_song = Song('', '')

    while True:
        current_song = song_fetcher.get_song()

        if (current_song is not None and current_song.title != most_recent_song.title):
            # call genius API
            most_recent_song = current_song

            response = get_genius_results(current_song, base_url, headers)
            song_info = verify_song(current_song, response)

            # is the song is found
            if song_info:
                print_artist_and_title(current_song)
                song_api_path = song_info['result']['api_path']
                lyrics = get_lyrics(song_api_path, base_url, headers)
                print(lyrics)

            else:
                print("Song lyrics not found :-(")
        else:
            time.sleep(5)
