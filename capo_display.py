"""Display written guitar shapes alongside concert-pitch chords for capo charts."""
import re
from transpose import transpose_chord

CAPO_RE = re.compile(r'^\s*(?:capo\s*)?(\d{1,2})\s*(?:st|nd|rd|th)?\s*(?:fret)?\s*$', re.I)

def capo_fret(song):
    value = str(song.get('capo','None') or 'None').strip()
    match=CAPO_RE.fullmatch(value)
    if not match:return 0
    fret=int(match.group(1))
    return fret if 0<=fret<=11 else 0

def concert_chord(shape, song):
    fret=capo_fret(song)
    if not fret or shape in {'-', '%', '[2/4]', '|'}:return None
    # Favour flat spelling for common concert keys (like Bb and Eb).
    key=str(song.get('key',''))
    use_flats=bool(re.match(r'^(?:Bb|Eb|Ab|Db|Gb|F)(?:\b|\s|$)',key))
    result=transpose_chord(shape,fret,use_flats)
    return result if result!=shape else None


def chord_pair(shape, song):
    """Return (guitar shape, sounding chord or None)."""
    return shape, concert_chord(shape,song)
