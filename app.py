import io,json,re
import streamlit as st
from songbook import export_docx,import_docx,synth_preview,preview_html
from transpose import KEYS, parse_key, transpose_song
st.set_page_config(page_title='Bluegrass Songbook & Setlist',layout='wide')
from pathlib import Path
if 'songs' not in st.session_state:
 
 try:
  st.session_state.songs=json.loads((Path(__file__).parent/'demo_repertoire.json').read_text(encoding='utf-8'))
 except (FileNotFoundError,ValueError):
  st.session_state.songs=[]
mode=st.sidebar.radio('Start here', ['Songbook', 'Setlist'], index=0)
if mode=='Setlist':
 from setlist_ui import render
 render()
 st.stop()
st.title('🎻 Bluegrass Songbook Builder')
st.caption('Edit, transpose and preview chord sheets; one chord token = one 2-beat box. Public demo entries only. Imports and edits stay in your current app session unless you explicitly download them. Do not upload confidential material to public cloud services.')
with st.sidebar:
 st.header('Library')
 if st.button('Reset to fictional demo songs'):
  st.session_state.songs=json.loads((Path(__file__).parent/'demo_repertoire.json').read_text(encoding='utf-8'))
  st.session_state.sets=[]
  st.session_state.edit=-1
  st.rerun()
 incoming=st.file_uploader('Import existing Word sheet (.docx)',type=['docx'])
 if incoming and st.button('Import DOCX'):
  imported=import_docx(io.BytesIO(incoming.read()))
  existing={s['title'].casefold() for s in st.session_state.songs}
  st.session_state.songs += [s for s in imported if s['title'].casefold() not in existing]
  st.success(f'Imported {len(imported)} entries (duplicates skipped). Review chords and timing.');st.rerun()
 json_file=st.file_uploader('Restore saved library (.json)',type=['json'])
 if json_file and st.button('Restore JSON'):
  data=json.load(json_file)
  if isinstance(data,list):st.session_state.songs=data;st.rerun()
  if isinstance(data,dict) and isinstance(data.get('songs'),list):
   st.session_state.songs=data['songs'];st.session_state.sets=data.get('sets',[]);st.rerun()
 st.download_button('Download library JSON',data=json.dumps(st.session_state.songs,ensure_ascii=False,indent=2),file_name='bluegrass_songs.json',mime='application/json')
 if st.session_state.songs:
  output=io.BytesIO();export_docx(st.session_state.songs).save(output)
  st.download_button('📄 Export Word songbook',data=output.getvalue(),file_name='Bluegrass_Songbook.docx',mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
 st.divider()
 st.write('**Format**: Type chord boxes separated by spaces; press Enter for a new row. Example: `G G C D`. A `-` holds the previous chord for two more beats. Type `[2/4]` at the end of a shortened row.')

if 'edit' not in st.session_state:st.session_state.edit=-1
sort=st.selectbox('View order',['Songs A–Z, then instrumentals A–Z','All titles A–Z','Instrumentals first','Original / entry order'])
if st.button('＋ Add new song'):
 st.session_state.songs.append({'title':'New song','artist':'','key':'G','kind':'Song','capo':'None','bpm':'','notes':'','structure':'','lyrics':'','duration_seconds':0,'origin':'Cover','vocalist':'','mood':'Medium','sections':[{'name':'Verse','chords':'G G C D'}]})
 st.session_state.edit=len(st.session_state.songs)-1;st.rerun()
indices=list(range(len(st.session_state.songs)))
if sort=='Songs A–Z, then instrumentals A–Z':indices.sort(key=lambda i:(st.session_state.songs[i].get('kind')=='Instrumental',st.session_state.songs[i]['title'].casefold()))
elif sort=='All titles A–Z':indices.sort(key=lambda i:st.session_state.songs[i]['title'].casefold())
elif sort=='Instrumentals first':indices.sort(key=lambda i:(st.session_state.songs[i].get('kind')!='Instrumental',st.session_state.songs[i]['title'].casefold()))
left,right=st.columns([1,2])
with left:
 if not indices:st.info('Add a new song, import your own Word document, or load the fictional examples.')
 for i in indices:
  s=st.session_state.songs[i]
  if st.button(f"{'🎻' if s.get('kind')=='Instrumental' else '🎤'} {s['title']} ({s.get('key','')})",key=f'open{i}',use_container_width=True):st.session_state.edit=i;st.rerun()
with right:
 i=st.session_state.edit
 if 0<=i<len(st.session_state.songs):
  s=st.session_state.songs[i]
  st.subheader('Edit arrangement')
  with st.expander('🎼 Transpose all chords to another key', expanded=True):
   st.caption('Change the sounding key for the whole chart. Every chord box updates, including Bm7, F#7 and slash basses like D/F#. Lyrics and section order stay unchanged. Your current chart remains untouched until you apply the change.')
   detected=parse_key(s.get('key',''))
   source_default=(detected[0]+detected[1]) if detected else ''
   a,b=st.columns(2)
   source=a.text_input('Current key (sounding)',value=source_default, key=f'sourcekey{i}',help='For entries such as B (G shapes), enter B. For a chart in G shapes with capo 4, sounding key is B.')
   target=b.selectbox('New key',KEYS,index=KEYS.index(source_default) if source_default in KEYS else 0,key=f'targetkey{i}')
   if st.button('Transpose this song',key=f'transpose{i}'):
    try:
     updated=transpose_song(s,target,source_key=source)
     # A capo is carried over: chord shapes transpose alongside the sounding key.
     st.session_state.songs[i]=updated
     # Clear old chord editor widget state so Streamlit reflects the new chords.
     for j in range(len(s.get('sections',[]))):
      st.session_state.pop(f'c{i}_{j}',None)
     st.success(f'Converted from {source} to {target}. You can export, or transpose again.')
     st.rerun()
    except ValueError as err:st.error(str(err))
   st.caption('Tip: D → E changes D–G–A–Bm into E–A–B–C#m. With capo 4, G-shape chords transpose to A shapes, still sounding four semitones higher. To keep the same shapes instead, simply change the capo position.')
  with st.form(f'editform{i}'):
   s['title']=st.text_input('Title',value=s['title'])
   s['artist']=st.text_input('Artist / version',value=s.get('artist',''))
   a,b,c,d=st.columns(4)
   s['key']=a.text_input('Key / shapes',value=s.get('key',''))
   s['kind']=b.selectbox('Category',['Song','Instrumental'],index=1 if s.get('kind')=='Instrumental' else 0)
   s['capo']=c.text_input('Capo',value=s.get('capo',''))
   s['bpm']=d.text_input('BPM',value=str(s.get('bpm','')))
   s['structure']=st.text_area('Playing order / structure',value=s.get('structure',''),height=72)
   s['notes']=st.text_area('Notes',value=s.get('notes',''),height=65)
   st.markdown('**Sections** — one chord per two-beat box; one row per line')
   sections=[]
   for j,part in enumerate(s.get('sections',[])):
    st.markdown(f'**Section {j+1}**')
    a,b=st.columns([1,3])
    name=a.text_input('Name',value=part['name'],key=f'n{i}_{j}')
    chords=b.text_area('Chord boxes',value=part['chords'],key=f'c{i}_{j}',height=110)
    sections.append({'name':name,'chords':chords})
   s['lyrics']=st.text_area('Lyrics (paste your own copy, optional)',value=s.get('lyrics',''),height=160,help='Make words **bold** or color them with [color=blue]text[/color] or [color=#C62828]text[/color].')
   st.caption('Lyric styling: `**bold words**` · `[color=red]red words[/color]` · `[color=#1565C0]custom blue[/color]`. Styling appears in the preview and exported Word document.')
   layouts=['Auto','Two columns','One column']
   s['lyrics_layout']=st.selectbox('Word lyrics layout',layouts,index=layouts.index(s.get('lyrics_layout','Auto')) if s.get('lyrics_layout','Auto') in layouts else 0,help='Auto puts longer lyrics in two columns to save page space. Short lyrics stay in one column. The layout can still exceed one page for very long songs.')
   save=st.form_submit_button('Save changes')
   if save:
    s['sections']=sections
    st.success('Saved. The preview below now shows your updated chart.')
    st.rerun()
  with st.expander('👁 Preview chord sheet and formatted lyrics',expanded=True):
   st.caption('Updates after you click Save changes. It closely matches the Word content; exact page breaks depend on Word.')
   st.html(preview_html(s))
  st.download_button('▶ Download chord audio preview (WAV)', data=synth_preview(s), file_name=re.sub(r'[^a-zA-Z0-9_-]','_',s['title'])+'_preview.wav', mime='audio/wav')
  c1,c2,c3=st.columns(3)
  if c1.button('Add section'):
   s['sections'].append({'name':'New section','chords':'G G C D'});st.rerun()
  if c2.button('Duplicate song'):
   clone=json.loads(json.dumps(s));clone['title']+=' (copy)';st.session_state.songs.append(clone);st.session_state.edit=len(st.session_state.songs)-1;st.rerun()
  if c3.button('Delete song',type='secondary'):
   st.session_state.songs.pop(i);st.session_state.edit=-1;st.rerun()
 else:st.write('Select a song on the left to edit its chords, lyrics, and section order.')
