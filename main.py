#!/usr/bin/env python2.7

import json
import requests
import os
import argparse
from slack import Slack, SlackMessage
from radarr import RadarrApi
from tmdb import TmdbApi

def _argparse():
    parser = argparse.ArgumentParser(
        description='Radarr Custom Script : perform Slack rich notification'
    )
    parser.add_argument(
        '--webhook-url', '-wu',
        help='Slack webhook url'
    )
    parser.add_argument(
        '--radarr-url', '-re',
        help='Radarr API endpoint : https://xxxx/api'
    )
    parser.add_argument(
        '--radarr-key', '-rk',
        help='Radarr API key, find it on Radarr > Settings > General'
    )
    parser.add_argument(
        '--tmdb-key', '-tk',
        help='TMDB API Key, register app on tmdb to obtain API Key'
    )
    args = parser.parse_args()
    return args


args = _argparse()

radarr = RadarrApi(args.radarr_url, args.radarr_key)
radarr.unmonitorMovieIfNeeded(os.environ.get("radarr_movie_id"), os.environ.get("radarr_eventtype"))
radarr.loadData(os.environ.get("radarr_download_id"))
link = "https://www.themoviedb.org/movie/"+os.environ.get("radarr_movie_tmdbid", "")

tmdb = TmdbApi(args.tmdb_key)
tmdb.loadMovieData(radarr.tmdbId)
tmdb.downloadMovieProductionImage()

message = SlackMessage(args.webhook_url)
message.package("*"+ os.environ.get("radarr_movie_title", "") +"* ("+ radarr.year +") ["+ os.environ.get("radarr_moviefile_quality", "") +"]")
message.constructor("`" +radarr.indexer+"` _"+os.environ.get("radarr_moviefile_releasegroup", "")+"_)")
message.link(link)
message.save()

message.notify()