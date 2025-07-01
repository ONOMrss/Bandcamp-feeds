#!/usr/bin/env python3
"""
Récupère le flux RSS-Bridge pour chaque tag Bandcamp
et le copie tel quel dans docs/<tag>.xml
"""
import pathlib, requests, time, random, shutil

# EDIT ici si tu veux ajouter/retirer des tags
TAGS = ['dubstep','bass','uk-bass','global-club',
        'club','tribal','ballroom','140','footwork']

# Choisis une instance RSS-Bridge publique stable
BRIDGE = "https://rss-bridge.bb8.fun"

OUT = pathlib.Path("docs"); OUT.mkdir(exist_ok=True)
HEAD = {"User-Agent": "Mozilla/5.0"}

for tag in TAGS:
    url = f"{BRIDGE}/?action=display&bridge=Bandcamp&tag={tag}&format=Atom"
    r = requests.get(url, headers=HEAD, timeout=30)
    if r.status_code != 200:
        # petite pause et 2ᵉ tentative (réseau saturé)
        time.sleep(random.uniform(1, 3))
        r = requests.get(url, headers=HEAD, timeout=30)
    r.raise_for_status()
    (OUT / f"{tag}.xml").write_bytes(r.content)
    time.sleep(1)   # politesse

print("✅  Flux copiés : ", ", ".join(TAGS))
