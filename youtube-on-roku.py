#!/usr/bin/env python3

import sys

try:
    import yt_dlp
except ImportError:
    sys.path.insert(0, 'yt-dlp')
    import yt_dlp

import json
import requests
import argparse
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
    root = ET.fromstring(data.text)
    loc = None
    name = None
    if root.find('user-device-location') != None:
        loc = root.find('user-device-location').text
    if root.find('user-device-name') != None:
        name = root.find('user-device-name').text
    elif root.find('default-device-name') != None:
        name = root.find('default-device-name').text
    else:
        name = 'Unknown Roku'
    if loc != None:
        return "{0} ({1}) at {2}".format(name, loc, roku)
    else:
        return "{0} at {1}".format(name, roku)

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

parser = argparse.ArgumentParser(description='Play YouTube videos on a Roku on the LAN.')

parser.add_argument('-n', '--number', metavar='NUMBER', nargs=1, type=int, default=0, help='Use the Roku device number NUMBER')
parser.add_argument('-u', '--url', metavar='ROKU_URL', nargs=1, default='', help='Use the Roku URL ROKU_URL')
parser.add_argument('-l', '--list', action='store_true', help='Just list the Roku devices this program can discover')
parser.add_argument('video', nargs='?', help='The YouTube URL or video ID')

args = parser.parse_args()

if args.list:
    rokus = get_roku()
    n = 1
    for roku in rokus:
        print("{0} - {1}".format(n, get_roku_info(roku.get("location"))))
        n = n + 1
    sys.exit(0)

roku = ""
if len(args.url) > 0:
    roku = args.url
else:
    rokus = get_roku()
    if (len(rokus) > 1) and (args.number == 0):
        n = 1
        for roku in rokus:
            print("{0} - {1}".format(n, get_roku_info(roku.get("location"))))
            n = n + 1
        num = input("Enter number")
        roku = rokus[num - 1].get("location")
    elif (len(rokus) > 1) and (args.number != 0):
        roku = rokus[args.number - 1].get("location")
    else:
        roku = rokus[0].get("location")

URL = args.video

ydl_opts = {'format':'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'}
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(URL, download=False)
    res = pick_format(ydl.sanitize_info(info))
    requests.post(make_roku_url(roku, res['url']))
