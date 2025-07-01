#!/usr/bin/env python3
"""
Génère un flux RSS par tag Bandcamp et l’enregistre dans docs/<tag>.xml
"""
import pathlib, requests, time, random
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator

TAGS = ['dubstep', 'bass', 'uk-bass', 'global-club',
        'club', 'tribal', 'ballroom', '140', 'footwork']

OUT = pathlib.Path("docs"); OUT.mkdir(exist_ok=True)
API = "https://bandcamp.com/api/hub/1/dig_deeper"
HEAD = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0"),
    "Origin": "https://bandcamp.com",
    "Content-Type": "application/json"
}

def latest(tag, n=30):
    payload = {"genre": tag, "sort_field": "date",
               "sort_value": "desc", "count": n}
    r = requests.post(API, json=payload, headers=HEAD, timeout=30)
    if r.status_code in (403, 429):
        time.sleep(random.uniform(1, 3))
        r = requests.post(API, json=payload, headers=HEAD, timeout=30)
    r.raise_for_status()
    return r.json().get("items", [])

for tag in TAGS:
    fg = FeedGenerator()
    fg.id(f'https://bandcamp.com/tag/{tag}')
    fg.title(f'Bandcamp – {tag} (latest)')
    fg.link(href=f'https://bandcamp.com/tag/{tag}', rel='alternate')
    fg.description(f'Newest Bandcamp releases for "{tag}"')
    items = latest(tag)
    for it in items:
        fe = fg.add_entry()
        fe.id(it['tralbum_url'])
        fe.title(f"{it['band_name']} – {it['title']}")
        fe.link(href=it['tralbum_url'])
        fe.author({'name': it['band_name']})
        fe.published(datetime.fromtimestamp(it['publish_date'],
                                            tz=timezone.utc))
        if it.get('art_url'):
            fe.enclosure(it['art_url'], 0, 'image/jpeg')
    (OUT / f'{tag}.xml').write_bytes(fg.rss_str(pretty=True))
    time.sleep(1)  # évite un blocage 429
