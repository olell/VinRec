# VinRec

VinRec ist erleichtert das Digitalisieren von Schallplatten. Aktuell noch in Entwicklung, aber als Proof-Of-Concept schon ganz brauchbar.

**Achtung: VinRec hat sehr wahrscheinlich noch viele Fehler, und ist bisher nicht in einer funktionierenden Version released worden.**

## Funktionen:
* Zerschneiden einer langen Aufnahme in einzelne Tracks
* Zuweisen von Metadaten auf Basis der Discogs-Datenbank
* Umwandlung in sämtliche Formate

## HowTo:
Einfach die Flask App starten, und im Browser öffnen:
```
env FLASK_APP=web.py flask run
```
Im Browser [`http://localhost:5000/`](http://localhost:5000/) öffnen

## Requirements
Benötigt werden folgende tools

* ffmpeg
* metaflac

Zudem folgende python Pakete:

* flask
* pydub
* requests
* python-magic

(TODO, README auf Englisch dürfte nicht schaden)

## Authors
* olel
