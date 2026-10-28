# Bluegrass Songbook & Setlist Planner

A free, local-first Streamlit app for a shared band repertoire. It has two pages accessible from the sidebar: **Songbook** and **Setlist**.

## Run on your own computer

Install Python 3.10 or newer. Download this project and, in its directory, run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the address printed by Streamlit (normally `http://localhost:8501`). No email address or account is required to use the app locally. This project has no database or automatic server-side sync. **Download the JSON project file before closing** to preserve changes, and upload it next time.

## Publish on GitHub and share a link

1. Create a new repository in GitHub and upload the source files from this ZIP (not the ZIP alone). Do not upload private lyrics or personal project JSON if you want the repository to be public.
2. To share a *working web app*, deploy the repository on [Streamlit Community Cloud](https://share.streamlit.io/) using `app.py` as the entrypoint. GitHub alone hosts code; it does not automatically run the Python/Streamlit server.
3. Share the resulting Streamlit web URL. Visitors can open it in their browser from a PC without installing Python. Shared app sessions are not a collaborative database; use downloaded JSON files to exchange changes.
4. Alternatively, share the GitHub repo URL so others can download and run it locally with Python.

## Songbook

- Starter library: the earlier 24 charts plus the supplied band repertoire, with four edited arrangements already included: Everyday I Write the Book (G), Rebecca, Shenandoah, There's Your Trouble.
- Create chords in 2-beat boxes, edit structures and lyrics, preview, synthesize WAV, change keys, show sounding chords alongside capo shapes.
- Use `**bold**` and `[color=blue]text[/color]` for lyric emphasis; export Word with one- or two-column lyrics.
- Unknown chord arrangements and lyrics are deliberately left blank. Some earlier chord progressions are simplified and should be checked before performance.

## Setlist

- Repertoire metadata: original / cover / unspecified, duration, vocalist, mood, and independent comma-separated **occasion tags** such as `Christmas`, `Wedding`, or `Festival`.
- Provided repertoire and known durations have been preloaded. Missing durations are `0` (unknown), not estimates. Edit metadata to enable those songs for automatic selection.
- Choose number of sets, minutes per set, song-to-song buffer, desired number of covers, opening and closing mood; use the occasion filter. Randomized drafting considers these preferences but does not guarantee an exact fit or cover quota.
- Move songs up/down, remove songs, add songs manually; see song and buffer minutes immediately.
- Download CSV, a Word songbook in the current set order, or the complete project JSON. Existing chord sheets are included when available; otherwise the Word pages contain titles and metadata with empty chord sections.

**Copyright:** The application does not automatically retrieve copyrighted lyrics. Only upload lyrics you have permission to use, especially when publishing a public repository.
