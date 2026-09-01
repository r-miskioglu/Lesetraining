# Lese-Lern-Blätter erstellen

Macht aus beliebigem deutschem Text ein **druckbares A4-Lese-Blatt** mit
**zweifarbigen Silben** (Silbenmethode) und **fetten Satzanfängen** — eine ruhige,
lesefreundliche Lesehilfe (auch bei ADHS).

## Einmal einrichten

```bash
cd ~/Lesetraining
python3 -m venv .venv
./.venv/bin/pip install pyphen
```

## Ordnerstruktur

| Ordner / Datei  | Inhalt                                                        |
|-----------------|---------------------------------------------------------------|
| `input/`        | die Text-Dateien (`.md` / `.txt`), aus denen Blätter entstehen |
| `output/`       | die erzeugten `.html`-Blätter (zum Öffnen/Drucken)            |
| `lesetblatt.py` | das Programm                                                  |

## Ein Blatt erstellen

1. Text in eine Datei im Ordner `input/` schreiben (Absätze durch eine
   **Leerzeile** trennen). Die Endung ist egal — es funktioniert jede reine
   Text-Datei, z. B. `.md` oder `.txt`. Beispiele liegen schon bereit
   (`input/Buchstabe_B.md`, `input/text.txt`).
2. Blatt erzeugen:
   ```bash
   ./.venv/bin/python lesetblatt.py input/Buchstabe_B.md -t "Der Buchstabe B"
   ```
   → erzeugt `output/Buchstabe_B.html` (gleicher Name wie die Eingabe, mit `.html`).
   Eigener Ausgabename: `... -o output/meinblatt.html`.
3. Die erzeugte Datei in `output/` **im Browser öffnen** → **Strg+P** → **„Als PDF speichern"** (oder drucken).
   Wichtig: im Druckdialog **„Hintergrundgrafiken"** aktivieren, damit die Farben mitkommen.

## Aussehen anpassen

Oben in `lesetblatt.py` im **KONFIG-Block** (gefahrlos herumprobieren):

| Einstellung          | Wirkung                                             |
|----------------------|-----------------------------------------------------|
| `FONT_SIZE_PT`       | Schriftgröße (größer = leichter)                    |
| `LINE_HEIGHT`        | Zeilenabstand                                       |
| `COLOR_A` / `COLOR_B`| die zwei Silben-Farben (Standard Blau/Rot)          |
| `COLUMN_CH`          | Zeilenlänge (kleiner = kürzere Zeilen)              |
| `SILBEN`             | `False` = keine Farben, nur fette Satzanfänge       |
| `FETTE_SATZANFAENGE` | fette Wort-Anfänge am Satzanfang an/aus             |
| `ZEBRA`              | `True` = dezenter Zeilen-Wechsel-Hintergrund        |

## Hinweis

Die Silbentrennung kommt aus dem Wörterbuch `de_DE` (Bibliothek `pyphen`) und ist bei
Alltagswörtern sehr zuverlässig. Bei seltenen Wörtern lohnt ein kurzer Blick — das
Ergebnis lässt sich notfalls im erzeugten `.html` von Hand nachbessern.
