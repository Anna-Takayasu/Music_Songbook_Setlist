"""Chromatic chord transposition, including seventh and slash chords."""
import re
NOTES_SHARP = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
NOTES_FLAT = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']
PITCH = {name:i for i,name in enumerate(NOTES_SHARP)} | {name:i for i,name in enumerate(NOTES_FLAT)}
KEYS = ['C','Db','D','Eb','E','F','F#','G','Ab','A','Bb','B']
CHORD = re.compile(r'(?<![A-Za-z0-9])([A-G](?:#|b)?)([^\s|/]*)(?:/([A-G](?:#|b)?))?(?![A-Za-z0-9])')
KEY_RE = re.compile(r'^\s*([A-G](?:#|b)?)(m?)(?:\s*\(.*\))?\s*$')

def parse_key(key):
    m=KEY_RE.fullmatch(str(key or ''))
    return (m.group(1),m.group(2)) if m else None

def shift_note(note, semitones, prefer_flats=False):
    if note not in PITCH: return note
    return (NOTES_FLAT if prefer_flats else NOTES_SHARP)[(PITCH[note]+semitones)%12]

def transpose_chord(token, semitones, prefer_flats=False):
    """Transpose all recognized chords; do not touch annotations/holds."""
    if token in {'-','[2/4]','|','%'}: return token
    # Complex cell like G/C or G C or C/D7: slash bass is transposed.
    def convert(m):
        root, suffix, bass=m.groups()
        return shift_note(root,semitones,prefer_flats)+suffix+('/'+shift_note(bass,semitones,prefer_flats) if bass else '')
    return CHORD.sub(convert,token)

def transpose_boxes(text, semitones, prefer_flats=False):
    # Preserve whitespace, formatting and explicit measure markers.
    return re.sub(r'[^\s|]+',lambda m:transpose_chord(m.group(),semitones,prefer_flats),text)

def transpose_song(song, target_key, source_key=None):
    """Return a transposed copy, never mutate the original song.
    Target is the sounding key. If a capo is active, update shapes too and
    retain its original position, unless the user explicitly opts otherwise.
    """
    import copy
    result=copy.deepcopy(song)
    parsed_source=parse_key(source_key or song.get('key',''))
    parsed_target=parse_key(target_key)
    if not parsed_source or not parsed_target:
        raise ValueError('Choose a source and target musical key, such as D or E (or Am). For descriptive key labels, set Source key manually.')
    a,minor_a=parsed_source; b,minor_b=parsed_target
    if minor_a!=minor_b:raise ValueError('Major and minor keys cannot be mixed here. Choose e.g. D→E or Am→Bm.')
    shift=(PITCH[b]-PITCH[a])%12
    use_flats=b in {'Db','Eb','F','Ab','Bb'}
    for section in result.get('sections',[]):
        section['chords']=transpose_boxes(section.get('chords',''),shift,use_flats)
    result['key']=target_key
    # A capo preserves the interval between chord shapes and sounding key.
    result['notes']=(result.get('notes','')+'\n' if result.get('notes') else '')+f'Transposed from {source_key or song.get("key","")} to {target_key}; capo position unchanged.'
    return result
