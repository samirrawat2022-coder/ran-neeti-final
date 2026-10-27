# RAN-NEETI — Multi-Sport + Anime Search-Grounded AI

This build expands the original Streamlit project into an automatic-first research interface for a broad set of real sports, esports, and anime/fictional matchups. The user enters a matchup in ordinary language; the app asks Gemini to use Google Search grounding and return a source-linked analysis including outcome estimates, strengths/weaknesses, major moves, counters, turning points, win conditions, uncertainties, and links.

## Important reliability statement
This is a **search-grounded AI analyst**, not a separately trained and validated ML model for every sport. Probabilities produced by the AI are labelled estimates and must not be presented as validated statistical-model probabilities. The prior football baseline should be evaluated and maintained as a separate research component if you want measured sports-model metrics. Fictional matchup probabilities are subjective and depend on versions/rules.

## Deploy online (no local Python installation needed)
1. Sign in to GitHub and create a new repository named `ran-neeti`.
2. Upload `app.py`, `requirements.txt`, and this `README.md` from this folder.
3. Open Streamlit Community Cloud: https://share.streamlit.io/ and connect GitHub.
4. Create an app using your repository and set the main file to `app.py`.
5. Before using live AI, create a Gemini API key in Google AI Studio if the API is available to your account: https://aistudio.google.com/app/apikey
6. In Streamlit Cloud, open App settings → Secrets and add:

```toml
GEMINI_API_KEY = "paste-your-private-key-here"
```

7. Save/reboot the app. The key must stay in Secrets; never put it in GitHub or public screenshots.
8. Test one real sports matchup and one fictional matchup; inspect the source links and logs before sharing the site.

## What works automatically
- Sport/domain inference from the matchup text.
- Google Search-grounded research via Gemini API.
- Automatic report generation with probabilities/estimates, explanations, major moves, counters, turning points and win conditions.
- Source links where returned by grounding metadata.
- Markdown report download.
- Optional advanced controls; no anime-specific configuration required by default.
- Broad catalog of 60+ sport types for prompts and coverage expectations.

## Limits / setup dependencies
- A Gemini API key is required for live grounded AI. Free tier, quota, regional availability and model access can change; not guaranteed to be unlimited.
- This app does not copy Google AI Overview's UI or scrape its private response. It uses the documented Gemini API with Google Search grounding.
- It does not claim a trained model for every sport. A real, defensible ML evaluation requires separate datasets and validation for each sport.
- Search grounding can miss sources or return outdated/ambiguous data; check sources and event dates.

## Local test (optional)
Python 3.10+ then `pip install -r requirements.txt`, set `GEMINI_API_KEY`, and run `streamlit run app.py`. End users of the deployed website do not need Python installed.
