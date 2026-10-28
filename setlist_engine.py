"""Pure setlist scheduling functions. Durations are in whole seconds."""
import random

def seconds(song):
    try: return max(0,int(song.get('duration_seconds',0) or 0))
    except (TypeError,ValueError): return 0

def candidates(songs, used=None):
    used=set(used or [])
    return [(i,s) for i,s in enumerate(songs) if i not in used and seconds(s)>0]

def generate_set(songs, target_minutes, buffer_seconds=20, cover_target=None,
                 start_mood='Energetic',end_mood='Energetic', used=None, eligible=None, seed=None):
    """Greedy randomized selection with duration, cover quota, mood arc and vocalist variety.
    Returns indices into songs; no exact-fit guarantee."""
    rng=random.Random(seed)
    pool=[(i,s) for i,s in candidates(songs,used) if eligible is None or i in eligible]
    budget=max(0,round(target_minutes*60))
    picked=[]
    elapsed=0
    while pool:
        feasible=[(i,s) for i,s in pool if elapsed+seconds(s)+(buffer_seconds if picked else 0)<=budget]
        if not feasible: break
        desired_covers=(cover_target if cover_target is not None else None)
        def rank(pair):
            i,s=pair
            cover_count=sum(songs[k].get('origin','Cover')=='Cover' for k in picked)
            is_cover=s.get('origin','Cover')=='Cover'
            cover_penalty=0 if desired_covers is None else (3 if is_cover and cover_count>=desired_covers else -1 if is_cover and cover_count<desired_covers else 0)
            previous=songs[picked[-1]].get('vocalist','') if picked else ''
            vocalist_penalty=2 if previous and previous==s.get('vocalist','') and previous!='Instrumental' else 0
            remainder=budget-(elapsed+seconds(s)+(buffer_seconds if picked else 0))
            return cover_penalty+vocalist_penalty + remainder/budget*0.4+rng.random()*2
        chosen=min(feasible,key=rank)
        i,s=chosen
        picked.append(i)
        elapsed+=seconds(s)+(buffer_seconds if len(picked)>1 else 0)
        pool=[p for p in pool if p[0]!=i]
    # Reorder to favor desired opening / ending mood without changing the chosen songs.
    if picked:
        for at,mood in [(0,start_mood),(-1,end_mood)]:
            eligible=[j for j,k in enumerate(picked) if songs[k].get('mood','Medium')==mood]
            if eligible:
                j=eligible[0] if at==0 else eligible[-1]
                picked[at],picked[j]=picked[j],picked[at]
    return picked

def calculate(songs, indices, buffer_seconds=20):
    valid=[i for i in indices if isinstance(i,int) and 0<=i<len(songs)]
    music=sum(seconds(songs[i]) for i in valid)
    transitions=max(0,len(valid)-1)*buffer_seconds
    return {'music':music,'buffers':transitions,'total':music+transitions,
            'covers':sum(songs[i].get('origin','Cover')=='Cover' for i in valid),
            'originals':sum(songs[i].get('origin','Cover')=='Original' for i in valid),
            'count':len(valid)}

def clock(sec):
    return f'{int(sec)//60}:{int(sec)%60:02d}'
