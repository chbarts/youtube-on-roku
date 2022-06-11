#!/usr/bin/env python3

import sys
sys.path.insert(0, 'yt-dlp')
import json
import yt_dlp
import requests
import urllib.parse

URL = 'https://www.youtube.com/watch?v=BaW_jenozKc'
IP = '192.168.1.182'

def pick_format(data):
    res = {}
    for format in data['formats']:
        if format['ext'] == 'mp4':
            res = format
    return res

def make_roku_url(url):
    params = urllib.parse.urlencode({'t':'v', 'u':url, 'videoName':'(null)', 'k': '(null)', 'videoFormat': 'mp4'})
    return 'http://' + IP + ':8060/input/15985?' + params

ydl_opts = {'format':'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(URL, download=False)
    res = pick_format(ydl.sanitize_info(info))
    requests.post(make_roku_url(res['url']))
