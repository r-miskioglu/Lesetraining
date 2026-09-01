#!/usr/bin/env python3
"""
Lese-Lern-Blatt-Generator
==========================

Macht aus einem beliebigen deutschen Text ein druckbares A4-Lese-Blatt:
  * Silben werden abwechselnd in zwei Farben eingefaerbt (Silbenmethode),
  * der erste Wort-Anfang jedes Satzes wird fett hervorgehoben,
  * grosse Schrift, weite Zeilenabstaende, kurze Zeilen, linksbuendig.

Gedacht als Lesehilfe (z. B. fuer Grundschueler, auch bei ADHS): eine klare
Methode + ruhiges Layout statt maximaler Buntheit.

Benutzung:
    python3 lesetblatt.py input/text.txt
    # -> erzeugt output/text.html  (im Browser oeffnen, Strg+P -> Als PDF)

    python3 lesetblatt.py input/text.txt -o output/kind1.html --titel "Meine Lesegeschichte"

Zum Ausprobieren einfach die Werte im KONFIG-Block unten anpassen.
"""

# ----------------------------------------------------------------------------
# KONFIG  --  hier gefahrlos herumprobieren, was dem Kind am besten hilft
# ----------------------------------------------------------------------------
FONT_SIZE_PT   = 20        # Schriftgroesse in pt (groesser = leichter)
LINE_HEIGHT    = 1.9       # Zeilenabstand (mehr Luft = leichter zu verfolgen)
COLOR_A        = "#1e5fbf"  # Farbe fuer die 1., 3., 5. ... Silbe (Blau)
COLOR_B        = "#c0392b"  # Farbe fuer die 2., 4., 6. ... Silbe (Rot)
COLUMN_CH      = 34        # Zeilenlaenge in Zeichen (kleiner = kuerzere Zeilen)
FONT_FAMILY    = ('"Andika", "Atkinson Hyperlegible", "Verdana", '
                  '"Segoe UI", sans-serif')  # klare, gut lesbare Schrift
SILBEN         = True      # True = Silben zweifarbig; False = nur Satzanfaenge fett
FETTE_SATZANFAENGE = True  # erstes Wort jedes Satzes fett
ZEBRA          = False     # dezenter Zeilen-Wechsel-Hintergrund (an/aus)
SPRACHE        = "de_DE"   # Silbentrennungs-Woerterbuch

# ----------------------------------------------------------------------------
import argparse
import html
import re
import sys
from pathlib import Path

import pyphen

# Ein "Token" ist entweder ein Wort (Buchstaben/Ziffern) oder Nicht-Wort
# (Leerzeichen, Satzzeichen). \w deckt auch Umlaute/ss ab (re.UNICODE ist Default).
_TOKEN_RE = re.compile(r"\w+|\W+", re.UNICODE)
_WORT_RE = re.compile(r"\w", re.UNICODE)
_SATZ_ENDE = set(".!?")


def ist_wort(token: str) -> bool:
    """True, wenn das Token echte Wortzeichen enthaelt (nicht nur Satzzeichen)."""
    return bool(_WORT_RE.search(token))


def silben(wort: str, dic: pyphen.Pyphen) -> list[str]:
    """Zerlegt ein Wort anhand der pyphen-Trennstellen in Silben."""
    positionen = dic.positions(wort)  # Indizes moeglicher Trennstellen
    if not positionen:
        return [wort]
    teile = []
    vorher = 0
    for pos in positionen:
        teile.append(wort[vorher:pos])
        vorher = pos
    teile.append(wort[vorher:])
    return teile


def render_wort(wort: str, farb_index: int, dic: pyphen.Pyphen) -> tuple[str, int]:
    """
    Gibt das HTML fuer ein Wort zurueck und den fortgeschriebenen Farb-Index.
    Der Farb-Index laeuft ueber Wortgrenzen hinweg weiter (klassische Optik).
    """
    if not SILBEN:
        return html.escape(wort), farb_index
    stuecke = []
    for teil in silben(wort, dic):
        klasse = "a" if farb_index % 2 == 0 else "b"
        stuecke.append(f'<span class="{klasse}">{html.escape(teil)}</span>')
        farb_index += 1
    return "".join(stuecke), farb_index


def render_absatz(text: str, dic: pyphen.Pyphen) -> str:
    """Wandelt einen Absatz (ohne Leerzeilen) in HTML um."""
    tokens = _TOKEN_RE.findall(text)
    farb_index = 0
    satzanfang = True   # naechstes Wort ist ein Satzanfang
    letzte_ziffer = False  # endete das letzte Wort auf einer Ziffer? (Ordnungszahl)
    out = []
    for token in tokens:
        if ist_wort(token):
            wort_html, farb_index = render_wort(token, farb_index, dic)
            if FETTE_SATZANFAENGE and satzanfang:
                wort_html = f"<strong>{wort_html}</strong>"
            out.append(wort_html)
            satzanfang = False
            letzte_ziffer = token[-1].isdigit()
        else:
            out.append(html.escape(token))
            # Satzende? '!'/'?' immer; '.' nur, wenn keine Ordnungszahl davor
            # steht (z. B. "14. August" oder "1. Mai" beginnt keinen neuen Satz).
            if "!" in token or "?" in token:
                satzanfang = True
            elif "." in token and not letzte_ziffer:
                satzanfang = True
    return "".join(out)


def text_zu_html_body(roher_text: str, dic: pyphen.Pyphen) -> str:
    """Zerlegt den Text in Absaetze (Leerzeile = Trenner) und rendert sie."""
    absaetze = re.split(r"\n\s*\n", roher_text.strip())
    return "\n".join(
        f"    <p>{render_absatz(a.strip(), dic)}</p>"
        for a in absaetze if a.strip()
    )


def baue_html(body: str, titel: str) -> str:
    zebra_css = (
        "    p { background: repeating-linear-gradient(\n"
        "        transparent, transparent calc(var(--lh) * 1em),\n"
        "        rgba(0,0,0,.035) calc(var(--lh) * 1em),\n"
        "        rgba(0,0,0,.035) calc(var(--lh) * 2em)); }\n"
        if ZEBRA else ""
    )
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<title>{html.escape(titel)}</title>
<style>
    :root {{ --lh: {LINE_HEIGHT}; }}
    @page {{ size: A4; margin: 2cm; }}
    * {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    body {{
        font-family: {FONT_FAMILY};
        font-size: {FONT_SIZE_PT}pt;
        line-height: var(--lh);
        color: #111;
        max-width: {COLUMN_CH}ch;
        margin: 0 auto;
        text-align: left;      /* kein Blocksatz */
        hyphens: none;
        background: #fff;
    }}
    header {{
        font-size: 12pt;
        color: #444;
        border-bottom: 1px solid #ccc;
        padding-bottom: .4em;
        margin-bottom: 1.2em;
        display: flex;
        justify-content: space-between;
    }}
    h1 {{ font-size: {FONT_SIZE_PT + 4}pt; margin: 0 0 .8em; }}
    p {{ margin: 0 0 1.1em; }}
    .a {{ color: {COLOR_A}; }}
    .b {{ color: {COLOR_B}; }}
    strong {{ font-weight: 800; }}
{zebra_css}    @media print {{ header {{ }} }}
</style>
</head>
<body>
    <header>
        <span>Name: ______________________</span>
        <span>Datum: ____________</span>
    </header>
    <h1>{html.escape(titel)}</h1>
{body}
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Erzeugt ein druckbares Lese-Lern-Blatt.")
    parser.add_argument("eingabe", help="Text-Datei (.md/.txt) mit deutschem Text, z. B. input/text.txt")
    parser.add_argument("-o", "--ausgabe", help="Ausgabe-HTML (Default: output/<eingabe>.html)")
    parser.add_argument("-t", "--titel", default="Lese-Blatt", help="Ueberschrift des Blatts")
    args = parser.parse_args()

    eingabe = Path(args.eingabe)
    if not eingabe.is_file():
        print(f"Fehler: Datei nicht gefunden: {eingabe}", file=sys.stderr)
        return 1

    if args.ausgabe:
        ausgabe = Path(args.ausgabe)
    else:
        # Standard: gleicher Name wie die Eingabe, aber als .html im Ordner output/
        ausgabe_ordner = Path("output")
        ausgabe_ordner.mkdir(exist_ok=True)
        ausgabe = ausgabe_ordner / (eingabe.stem + ".html")
    dic = pyphen.Pyphen(lang=SPRACHE)

    roher_text = eingabe.read_text(encoding="utf-8")
    body = text_zu_html_body(roher_text, dic)
    ausgabe.write_text(baue_html(body, args.titel), encoding="utf-8")

    print(f"Fertig: {ausgabe}")
    print("Zum Drucken im Browser oeffnen und Strg+P -> 'Als PDF speichern'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
