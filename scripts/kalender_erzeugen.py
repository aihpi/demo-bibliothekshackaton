"""Erzeugt die Kalender für Flow 05: daten/schulungsplanung/kalender_<jahr>.csv mit jedem Tag und seinem Wochentag.

Sprachmodelle verrechnen sich bei Wochentagen. Mit dem Kalender schlägt die KI den Wochentag nach, statt ihn zu raten.

    uv run scripts/kalender_erzeugen.py 2026 2027
"""

import datetime
import sys
from pathlib import Path

ZIEL = Path(__file__).resolve().parent.parent / "daten" / "schulungsplanung"
WOCHENTAGE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def kalender(jahr: int) -> str:
    tag = datetime.date(jahr, 1, 1)
    zeilen = ["datum,wochentag"]
    while tag.year == jahr:
        zeilen.append(f"{tag:%d.%m.%Y},{WOCHENTAGE[tag.weekday()]}")
        tag += datetime.timedelta(days=1)
    return "\n".join(zeilen) + "\n"


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Bitte die Jahre angeben, z. B.: uv run scripts/kalender_erzeugen.py 2026 2027")
    for jahr in map(int, sys.argv[1:]):
        datei = ZIEL / f"kalender_{jahr}.csv"
        datei.write_text(kalender(jahr), encoding="utf-8")
        print(f"geschrieben: {datei}")


if __name__ == "__main__":
    main()
