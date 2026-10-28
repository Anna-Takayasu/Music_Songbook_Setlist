import io, json, csv
import streamlit as st
from setlist_engine import generate_set,calculate,clock,seconds
from songbook import export_docx

MOODS=['Calm','Gentle','Medium','Energetic','High energy']

def render():
    st.title('🎤 Setlist planner')
    st.caption('Create a timed show, control covers and the mood arc, then move songs manually. Save the plan as JSON for later use.')
    songs=st.session_state.songs
    if 'sets' not in st.session_state: st.session_state.sets=[]
    if 'occasion_presets' not in st.session_state: st.session_state.occasion_presets={}
    if 'active_occasion' not in st.session_state: st.session_state.active_occasion='Custom'
    with st.expander('1 · Song metadata — durations, vocalist, origin and mood',expanded=True):
        st.caption('Only songs with a duration greater than zero can be selected automatically. Edit and save metadata before generating.')
        import pandas as pd
        data=[{'ID':i,'Song':s['title'],'Duration (sec)':seconds(s),'Original / Cover':s.get('origin','Unspecified'),
               'Occasions':', '.join(s.get('occasions',[])), 'Styles':', '.join(s.get('styles',[])),
               'Main vocalist':s.get('vocalist','Instrumental' if s.get('kind')=='Instrumental' else ''),
               'Mood':s.get('mood','Medium')} for i,s in enumerate(songs)]
        edit=st.data_editor(pd.DataFrame(data),hide_index=True,use_container_width=True,num_rows='fixed',disabled=['ID','Song'],
              column_config={'Original / Cover':st.column_config.SelectboxColumn(options=['Original','Cover','Unspecified'],required=True),
                             'Mood':st.column_config.SelectboxColumn(options=MOODS,required=True),
                             'Duration (sec)':st.column_config.NumberColumn(min_value=0,max_value=3600,step=10,required=True)},key='metadata_grid')
        if st.button('Save song metadata'):
            for row in edit.to_dict('records'):
                s=songs[int(row['ID'])]
                s['duration_seconds']=int(row['Duration (sec)'] or 0)
                s['origin']=row['Original / Cover']
                s['vocalist']=str(row['Main vocalist'] or '')
                s['mood']=row['Mood']
                s['occasions']=[v.strip() for v in str(row.get('Occasions') or '').split(',') if v.strip()]
                s['styles']=[v.strip() for v in str(row.get('Styles') or '').split(',') if v.strip()]
            st.success('Song metadata saved in this session. Download JSON to keep it.')
            st.rerun()
    st.subheader('2 · Occasion and style restrictions')
    st.caption('Give each repertoire entry tags in Song metadata above. A song can be both a Cover and Christmas, and have multiple styles (for example Bluegrass, Folk).')
    all_styles=sorted({tag for song in songs for tag in song.get('styles',[]) if tag},key=str.casefold)
    all_occasions=sorted({tag for song in songs for tag in song.get('occasions',[]) if tag},key=str.casefold)
    presets=st.session_state.occasion_presets
    names=['Custom']+sorted(presets,key=str.casefold)
    active=st.selectbox('Choose an occasion preset', names, index=names.index(st.session_state.active_occasion) if st.session_state.active_occasion in names else 0)
    if active != st.session_state.active_occasion:
        st.session_state.active_occasion=active
        for k in ['occasion_tags','xmas_rule','style_rule','style_tags','bg_share']:
            st.session_state.pop('rule_'+k,None)
    preset=presets.get(active,{})
    a,b=st.columns(2)
    with a:
        selected_tags=st.multiselect('Occasion tags to include',all_occasions,default=[v for v in preset.get('occasion_tags',[]) if v in all_occasions],key='rule_occasion_tags',help='Leave empty for all occasions. Multiple selected tags mean OR.')
        christmas=st.selectbox('Christmas songs', ['Include','Exclude','Only Christmas'], index=['Include','Exclude','Only Christmas'].index(preset.get('xmas_rule','Include')),key='rule_xmas_rule')
    with b:
        style_rule=st.selectbox('Musical style restriction',['Any style','Include selected styles','Exclude selected styles'],index=['Any style','Include selected styles','Exclude selected styles'].index(preset.get('style_rule','Any style')),key='rule_style_rule')
        style_tags=st.multiselect('Styles',all_styles,default=[v for v in preset.get('style_tags',[]) if v in all_styles],key='rule_style_tags')
    min_bluegrass=st.slider('Minimum Bluegrass share (target % of songs)',0,100,value=int(preset.get('bg_share',0)),step=10,key='rule_bg_share',help='Targets the proportion of selected songs tagged Bluegrass. If insufficient eligible songs fit, the planner reports a shortfall.')
    new_name=st.text_input('Save these restrictions as a named occasion (e.g. Christmas concert, Bluegrass night)',key='new_preset_name')
    if st.button('Save / update occasion preset'):
        if not new_name.strip(): st.warning('Enter a name to save your occasion settings.')
        else:
            presets[new_name.strip()]={'occasion_tags':selected_tags,'xmas_rule':christmas,'style_rule':style_rule,'style_tags':style_tags,'bg_share':min_bluegrass}
            st.session_state.active_occasion=new_name.strip()
            st.success('Occasion preset saved in this session. Download the project JSON to keep it.')
    if active!='Custom' and st.button('Delete this occasion preset'):
        presets.pop(active,None); st.session_state.active_occasion='Custom';st.rerun()

    def eligible_song(song):
        occasions={v.casefold() for v in song.get('occasions',[])}
        styles={v.casefold() for v in song.get('styles',[])}
        if selected_tags and not occasions.intersection({v.casefold() for v in selected_tags}):return False
        if christmas=='Exclude' and 'christmas' in occasions:return False
        if christmas=='Only Christmas' and 'christmas' not in occasions:return False
        selected_style_set={v.casefold() for v in style_tags}
        if style_rule=='Include selected styles' and selected_style_set and not styles.intersection(selected_style_set):return False
        if style_rule=='Exclude selected styles' and styles.intersection(selected_style_set):return False
        return True
    eligible=[j for j,entry in enumerate(songs) if eligible_song(entry)]
    st.caption(f'{len(eligible)} of {len(songs)} repertoire entries match these restrictions; only entries with known durations are automatically scheduled.')
    st.subheader('3 · Build your sets')
    n=st.number_input('Number of sets',1,8,max(1,len(st.session_state.sets) or 2),step=1)
    while len(st.session_state.sets)<n: st.session_state.sets.append({'name':f'Set {len(st.session_state.sets)+1}','songs':[],'duration':40,'buffer':20,'covers':2,'start':'Energetic','end':'Energetic'})
    st.session_state.sets=st.session_state.sets[:n]
    for si,plan in enumerate(st.session_state.sets):
        with st.container(border=True):
            st.markdown(f'### Set {si+1}')
            plan['name']=st.text_input('Set name',plan['name'],key=f'setname{si}')
            a,b,c=st.columns(3)
            plan['duration']=a.number_input('Target set length (minutes)',min_value=5,max_value=240,value=int(plan['duration']),key=f'duration{si}')
            plan['buffer']=b.number_input('Buffer between songs (seconds)',min_value=0,max_value=300,value=int(plan['buffer']),step=5,key=f'buffer{si}')
            plan['covers']=c.number_input('Desired number of covers',min_value=0,max_value=100,value=int(plan['covers']),key=f'covers{si}')
            a,b=st.columns(2)
            plan['start']=a.selectbox('Opening mood',MOODS,index=MOODS.index(plan['start']),key=f'start{si}')
            plan['end']=b.selectbox('Ending mood',MOODS,index=MOODS.index(plan['end']),key=f'end{si}')
            if st.button('🎲 Generate / reshuffle draft',key=f'generate{si}'):
                used=[k for other in st.session_state.sets[:si] for k in other['songs']]
                plan['songs']=generate_set(songs,plan['duration'],plan['buffer'],plan['covers'],plan['start'],plan['end'],used=used,eligible=eligible,min_bluegrass_fraction=min_bluegrass/100)
                st.rerun()
            if not any(seconds(s) for s in songs):st.info('Enter song durations in section 1 to enable automatic planning.')
            if plan['songs']:
                stats=calculate(songs,plan['songs'],plan['buffer'])
                st.write(f"**Total {clock(stats['total'])} / {plan['duration']}:00** · Music {clock(stats['music'])} · Buffers {clock(stats['buffers'])} · Covers {stats['covers']} · Originals {stats['originals']}")
                bluegrass_count=sum('bluegrass' in {t.casefold() for t in songs[j].get('styles',[])} for j in plan['songs'])
                if min_bluegrass and bluegrass_count/len(plan['songs']) < min_bluegrass/100:
                    st.warning(f'Bluegrass target not met: {bluegrass_count}/{len(plan["songs"])} songs ({100*bluegrass_count/len(plan["songs"]):.0f}%) vs {min_bluegrass}%. Add more eligible Bluegrass titles or relax the restrictions.')
                diff=plan['duration']*60-stats['total']
                st.caption(f"{'Remaining' if diff>=0 else 'Over target'}: {clock(abs(diff))}. Cover target is a preference, not an absolute constraint.")
                for pos,idx in enumerate(list(plan['songs'])):
                    song=songs[idx]
                    col=st.columns([0.5,4,1,0.7,0.7,0.7])
                    col[0].write(f'{pos+1}.')
                    col[1].write(f"**{song['title']}** · {song.get('vocalist','')} · {song.get('mood','')} · {song.get('origin','Cover')}")
                    col[2].write(clock(seconds(song)))
                    if col[3].button('↑',key=f'up{si}_{pos}',disabled=pos==0):
                        plan['songs'][pos-1],plan['songs'][pos]=plan['songs'][pos],plan['songs'][pos-1];st.rerun()
                    if col[4].button('↓',key=f'dn{si}_{pos}',disabled=pos==len(plan['songs'])-1):
                        plan['songs'][pos+1],plan['songs'][pos]=plan['songs'][pos],plan['songs'][pos+1];st.rerun()
                    if col[5].button('✕',key=f'rm{si}_{pos}'):
                        plan['songs'].pop(pos);st.rerun()
            chosen=set(plan['songs'])
            choices=[i for i,s in enumerate(songs) if i not in chosen and i in eligible]
            if choices:
                selected=st.selectbox('Add a song manually',options=choices,format_func=lambda i:f"{songs[i]['title']} — {clock(seconds(songs[i]))}",key=f'addchoice{si}')
                if st.button('Add to this set',key=f'add{si}'):
                    plan['songs'].append(selected);st.rerun()
    st.subheader('4 · Export setlist / order the Songbook')
    all_indices=[i for plan in st.session_state.sets for i in plan['songs']]
    st.caption('Word Songbook export follows the exact set order above. A song played twice is included twice. Songs not on the setlist are omitted.')
    if all_indices:
        out=io.BytesIO();export_docx([songs[i] for i in all_indices],heading='SETLIST SONGBOOK') .save(out)
        st.download_button('📄 Export Songbook in setlist order',out.getvalue(),file_name='Setlist_ordered_songbook.docx')
        rows=[]
        for p in st.session_state.sets:
            for j,i in enumerate(p['songs'],1):
                s=songs[i];rows.append({'Set':p['name'],'Order':j,'Title':s['title'],'Duration':clock(seconds(s)),'Origin':s.get('origin','Cover'),'Vocalist':s.get('vocalist',''),'Mood':s.get('mood',''),'Occasions':', '.join(s.get('occasions',[]))})
        output=io.StringIO();w=csv.DictWriter(output,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        st.download_button('📋 Export setlist CSV',output.getvalue().encode('utf-8-sig'),file_name='setlist.csv',mime='text/csv')
    state={'songs':songs,'sets':st.session_state.sets,'occasion_presets':st.session_state.occasion_presets}
    st.download_button('💾 Save songs + setlists as JSON',json.dumps(state,ensure_ascii=False,indent=2),file_name='bluegrass_project.json',mime='application/json')
