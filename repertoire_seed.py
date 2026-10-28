"""User-provided initial repertoire; unknown timings are deliberately zero."""
ORIGINALS = '''Apfelbaum|
Gift|3:10
Gleitflug|
Glück|3:00
Herzensmensch|3:30
Meteorit|
Mehr!|3:30
Shitstorm|4:00
Sommer|4:50
Stilles Gedicht|4:00
Swipe|
Tanzgefühl|4:00
Licht|
Ok, Ciao|
Nonchalant|'''
COVERS = '''Blackberry Blossom|
Black Horse And The Cherry Tree|
Fever|
Footloose|4:00
Havana|
I Wanna Be Like You|
I Will Wait|5:00
Joseph Joseph|
Magic To Do / Spooky|
No Roots|
Old Man|
Schrei Nach Liebe|4:10
Seven Bridges Road|
Steel Rails|
Stubborn Love|4:10
Sunny|
Talkin About A Revolution|
English Man|
Mr Sandman/Santa|'''
CHRISTMAS = '''Let It Snow|
Nur Kurz Vorbei|
Stille Nacht - Silent Night|
Mr Santa|'''

def apply(songs):
    by_title={s.get('title','').strip().casefold():s for s in songs}
    for chunk,origin,special in [(ORIGINALS,'Original',False),(COVERS,'Cover',False),(CHRISTMAS,'Unspecified',True)]:
        for line in chunk.splitlines():
            title, _,time = line.partition('|')
            key=title.casefold()
            s=by_title.get(key)
            if s is None:
                s={'title':title,'artist':'','key':'','kind':'Instrumental' if title=='Blackberry Blossom' else 'Song','capo':'None','bpm':'','notes':'','structure':'','lyrics':'','sections':[]}
                songs.append(s);by_title[key]=s
            if special:
                tags=set(s.get('occasions',[]));tags.add('Christmas');s['occasions']=sorted(tags)
            else:s['origin']=origin
            if time:
                mm,ss=map(int,time.split(':'));s['duration_seconds']=mm*60+ss
            s.setdefault('duration_seconds',0)
            s.setdefault('origin','Unspecified')
            s.setdefault('vocalist','Instrumental' if s.get('kind')=='Instrumental' else '')
            s.setdefault('mood','Medium')
            s.setdefault('occasions',[])
    return songs
