#!/usr/bin/env python3

import sys

try:
    import yt_dlp
except ImportError:
    sys.path.insert(0, 'yt-dlp')
    import yt_dlp

import json
import requests
import urllib.parse
from ssdpy import SSDPClient
import xml.etree.ElementTree as ET

URL = 'https://www.youtube.com/watch?v=BaW_jenozKc'
IP = '192.168.1.182'

def pick_format(data):
    res = {}
    for format in data['formats']:
        if (format['ext'] == 'mp4') and (format['acodec'] != 'none') and (format['vcodec'] != 'none'):
            res = format
    return res

def get_roku_info(roku):
    data = requests.get(roku + 'query/device-info')
    root = ET.fromstring(data)
    if root.find('user-device-name'):
        return root.find('user-device-name').text + ' at ' + roku
    if root.find('default-device-name'):
        return root.find('default-device-name').text + ' at ' + roku
    return 'Unknown Roku at ' + roku

def make_roku_url(roku, url):
    params = urllib.parse.urlencode({'t':'v', 'u':url, 'videoName':'(null)', 'k': '(null)', 'videoFormat': 'mp4'})
    return roku + 'input/15985?' + params

def get_roku():
    client = SSDPClient()
    devices = client.m_search('ssdp:all')
    res = []
    for device in devices:
        if "roku" in device.get("usn"):
            res = res + [device]
    return res

#        print(device.get("usn") + '\t' + device.get("location"))

if len(sys.argv) != 2:
    print('Usage: ' + sys.argv[0] + ' YOUTUBE_URL_OR_VIDEO_ID')
    sys.exit(0)

URL = sys.argv[1]

roku = ""
rokus = get_roku()
if len(rokus) > 1:
    n = 1
    for roku in rokus:
        print("{0} - {1}".format(n, get_roku_info(roku.get("location"))))
        n = n + 1
    num = input("Enter number")
    roku = rokus[num - 1].get("location")
else:
    roku = rokus[0].get("location")

ydl_opts = {'format':'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(URL, download=False)
    res = pick_format(ydl.sanitize_info(info))
    requests.post(make_roku_url(roku, res['url']))
