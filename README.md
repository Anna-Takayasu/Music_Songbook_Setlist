# Songbook & Setlist — public demo

GitHub/Streamlit-ready **example-only** application. All bundled songs and lyric snippets are fictional. **No personal repertoire, original uploaded songbook or real setlist is bundled.**

## Deploy
Upload only the files in this folder to the root of your GitHub repository (`app.py`, `demo_repertoire.json`, `songbook.py`, etc.). At https://share.streamlit.io/ select repository, branch `main`, entrypoint `app.py`. The live site requires Streamlit Community Cloud hosting; GitHub alone cannot run it.

## Use your own files later
In **Songbook**, use **Import existing Word sheet (.docx)** or **Restore saved library (.json)**. Imported data appears in the current browser session, not in the GitHub repository. Export Word/JSON from the app, then save the JSON file on your computer to restore it another day. Use **Setlist** to edit durations, mood, vocalist, type, occasion tags, and generate, reorder, and export sets. Songbook export can follow setlist order.

## Privacy
When using a **public Streamlit Cloud app**, your upload is processed on the remote app server even though it is not committed to GitHub. This starter implementation does **not** persist uploaded data to a database, does **not** synchronize between users, and does **not** ask for email. Avoid uploading confidential data to a public hosted app if you require strict local-only handling. To keep documents entirely on your own PC, run the app locally (`python -m pip install -r requirements.txt` then `python -m streamlit run app.py`).

Only upload the example project files to GitHub; never commit your personal `.docx` or private `.json` collection.
