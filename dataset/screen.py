#!/usr/bin/env python3


"""
Prérequis : 
    ffmpeg -> https://www.ffmpeg.org/download.html
    magick -> https://imagemagick.org/script/download.php
Avant utilisation :
    Il faut absolument faire 'chmod +x screen.py' pour rendre le 
    script executable.
Utilisation :
    Dans le terminal faire './screen.py input.txt data_dir' avec
    data_dir le directory ou les screens seront enregistres et
    input.txt un fichier de la forme :
        nb screen par fichier, categorie, fichier/directory de la/des video a screen
    Il est possible de mettre une entree par ligne.
Sortie :
    Les screens sont enregistres dans le directory data_dir nommes avec la
    convention 'categorie_XXXX.jpg' avec XXXX l'identifiant du screen en 
    fonction de sa categorie. Les images sont deja redimensionnees en 512p.
"""
        






import asyncio
import logging
import random
import sys
from collections import defaultdict
from pathlib import Path

dico = defaultdict(int)

async def main():
    with open(sys.argv[1]) as fp:
        for ligne in fp.readlines():
            n, cat, element = ligne.strip().split(', ')
            n = int(n)
            await traite(element, n, cat)
    print(dico)

async def traite(element, n, cat):
    element = Path(element)
    if element.is_dir():
        await traite_dir(element, n, cat)
    else:
        await traite_file(element, n, cat)


async def traite_dir(directory: Path, n, cat):
    for element in directory.iterdir():
        await traite(element, n, cat)


async def traite_file(file: Path, n, cat):
    if file.suffix not in ('.mkv', '.mp4'):
        return

    cmd = (f"ffprobe -v error -show_entries format=duration "
           f"-of default=noprint_wrappers=1:nokey=1 \"{file}\"")
    stdout = await run(cmd)
    duration = int(float(stdout))

    for _ in range(0, n):
        t = random.randrange(duration)
        output = f"{sys.argv[2]}/{cat}_{dico[cat]:06}.jpg"
        cmd = f"ffmpeg -y -ss {t} -i \"{file}\" -frames:v 1 -q:v 2 \"{output}\""
        await run(cmd)
        cmd = f"magick convert -resize x512 \"{output}\" \"{output}\""
        await run(cmd)
        dico[cat] += 1


async def run(cmd):
    proc = await asyncio.create_subprocess_shell(cmd,
                                                 stdout=asyncio.subprocess.PIPE,
                                                 stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    if stderr:
        logging.error(stderr.decode())
    stdout = stdout.decode()
    logging.info(stdout)
    return stdout


asyncio.run(main())
