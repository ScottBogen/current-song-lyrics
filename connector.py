import requests
import json

import spotipy
from song import Song
from spotipy.oauth2 import SpotifyOAuth

# This class will represent the part of the program that fetches Spotify's API and returns a song object


class SongFetcher():
    def __init__(self, scope):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    # returns as JSON
    def get_currently_playing_song_as_JSON(self):
        response = self.sp.currently_playing(
            market=None, additional_types=None)
        return response

    def get_artist_from_JSON(self, json):
        artist = json['item']['artists'][0]['name']
        return artist

    def get_track_from_JSON(self, json):
        track = json['item']['name']
        return track

    def get_song(self):
        response = self.get_currently_playing_song_as_JSON()
        song = None
        if response is not None:
            track = self.get_track_from_JSON(response)
            artist = self.get_artist_from_JSON(response)
            song = Song(track, artist)
        return song
