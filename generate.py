#!/usr/bin/env python3
"""
generate.py – Bandcamp feeds with full EmbeddedPlayer iframe
• Pour chaque tag, télécharge le flux Atom RSS-Bridge
• Pour chaque item, scrape la jaquette + iframe EmbeddedPlayer
• Écrit docs/<tag>.xml avec feedgen (content:encoded HTML)
"""
import pathlib, time, random, re, requests, feedparser
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator

# 👉 Modifie la liste si besoin
TAGS = ['dubstep', 'bass', 'uk-bass', 'global-club',
        'club', 'tribal', 'ballroom', '140', 'footwork']
BRIDGE = "https://rss-bridge.bb8.fun"          # change si instance lente
HEAD   = {"User-Agent": "Mozilla/5.0"}         # user-agent « navigateur »
OUT    = pathlib.Path("docs"); OUT.mkdir(exist_ok=True)

def scrape_album(url):
    """Retourne (art_url, iframe_html) depuis la page Bandcamp"""
    html = requests.get(url, headers=HEAD, timeout=20).text
    art_match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    art_url   = art_match.group(1) if art_match else ''
    iframe_match = re.search(
        r'(<iframe[^>]+bandcamp\.com/EmbeddedPlayer[^>]*></iframe>)',
        html, re.DOTALL)
    iframe_html = iframe_match.group(1) if iframe_match else ''
    return art_url, iframe_html

for tag in TAGS:
    atom_url = f"{BRIDGE}/?action=display&bridge=Bandcamp&tag={tag}&format=Atom"
    feed = feedparser.parse(requests.get(atom_url, headers=HEAD, timeout=30).content)

    fg = FeedGenerator()
    fg.id(f'https://bandcamp.com/tag/{tag}')
    fg.title(f'Bandcamp – {tag} (latest)')
    fg.link(href=f'https://bandcamp.com/tag/{tag}', rel='alternate')
    fg.description(f'Newest Bandcamp releases for “{tag}”')
    fg.generator('GitHub Actions + feedgen')

    for entry in feed.entries[:30]:          # limite à 30 items
        link   = entry.link
        title  = entry.title
        author = getattr(entry, 'author', '')
        pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

        art_url, iframe_html = scrape_album(link)
        # Description : jaquette cliquable + iframe lecteur
        description = f'<a href="{link}"><img src="{art_url}" ' \
                      f'style="max-width:400px;height:auto;border:0;"></a><br/>{iframe_html}'

        fe = fg.add_entry()
        fe.id(link)
        fe.title(title)
        fe.link(href=link)
        fe.author({'name': author})
        fe.published(pub_dt)
        fe.content(description, type='CDATA')
        time.sleep(0.5)      # politesse pour éviter les 429

    (OUT / f'{tag}.xml').write_bytes(fg.atom_str(pretty=True))
    time.sleep(1)            # petite pause entre tags

print("✅ Feeds regenerated with embedded players.")
