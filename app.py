import os, re, json, requests
from datetime import datetime, timezone
import streamlit as st

st.set_page_config(page_title='RAN-NEETI | Multiverse Prediction AI', page_icon='⚔️', layout='wide')

SPORTS = {
 'Team sports': ['Football / Soccer','Cricket (Test)','Cricket (ODI)','Cricket (T20)','Basketball','Baseball','American Football','Rugby Union','Rugby League','Rugby Sevens','Ice Hockey','Field Hockey','Volleyball','Beach Volleyball','Handball','Kabaddi','Water Polo','Lacrosse','Futsal','Netball','Australian Rules Football'],
 'Racket & individual': ['Tennis','Badminton','Table Tennis','Squash','Pickleball','Golf','Boxing','MMA','Wrestling','Judo','Taekwondo','Karate','Fencing','Chess','Go','Esports'],
 'Racing & athletics': ['Formula 1 / Motorsport','MotoGP','Cycling','Athletics / Track & Field','Marathon','Swimming','Diving','Gymnastics','Weightlifting','Rowing','Canoe / Kayak','Skiing','Snowboarding','Skating','Surfing','Archery','Shooting','Triathlon'],
 'Other': ['Darts','Snooker / Pool','Billiards','Equestrian','Sailing','Sport Climbing','Figure Skating']
}
ALL_SPORTS = [x for group in SPORTS.values() for x in group]

CSS = '''<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
.stApp{background:radial-gradient(ellipse at 12% 0%,#182747 0%,#080b14 50%,#090a12 100%);color:#edf3ff}
.block-container{max-width:1400px;padding-top:1.2rem}
[data-testid="stSidebar"]{background:#0c1120;border-right:1px solid #293650}
h1,h2,h3{font-family:Orbitron,sans-serif!important}
.hero{padding:26px 30px;border:1px solid #293b5b;border-radius:20px;background:linear-gradient(115deg,rgba(22,35,63,.96),rgba(15,18,35,.92));margin-bottom:20px}
.brand{font:800 clamp(30px,4vw,52px) Orbitron,sans-serif;background:linear-gradient(90deg,#fff,#54e8ff 55%,#b69aff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.2}
.kicker{font:600 11px Orbitron,sans-serif;letter-spacing:3px;color:#54e8ff;text-transform:uppercase}
.panel{background:rgba(16,22,38,.82);border:1px solid #25314a;border-radius:16px;padding:18px 22px;margin-bottom:14px}
.stButton>button{border:1px solid #54e8ff;background:linear-gradient(90deg,#173a50,#24234a);color:#f6fbff;border-radius:10px;font-family:Orbitron,sans-serif;font-weight:600;min-height:44px}
.small{color:#9ba8c2;font-size:12px}
</style>'''
st.markdown(CSS, unsafe_allow_html=True)

st.markdown('''<div class="hero"><div class="kicker">MULTI-SPORT • SEARCH-GROUNDED AI • EXPLAINABLE PREDICTIONS</div><div class="brand">RAN-NEETI</div><p style="color:#b8c6df;font-size:16px">One matchup in. Research, probability estimate, major moves, counters, turning points and win conditions out.</p><p class="small">Real sports × esports × anime / fictional battles • Automatic-first • Advanced controls optional</p></div>''', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('## ⚙️ Control room')
    st.markdown('**Automatic mode** is the default. Enter a matchup in ordinary language; the AI tries to identify the sport/domain and research it.')
    advanced = st.toggle('Advanced controls', value=False)
    if advanced:
        domain_hint = st.selectbox('Domain hint', ['Auto-detect','Real sport / esports','Anime / fictional battle'])
        detail_level = st.select_slider('Analysis detail', options=['Concise','Detailed','Deep research'], value='Detailed')
        context = st.text_area('Optional context', placeholder='e.g., T20, today’s match, neutral venue, specific anime arc, no prep time…')
        sources_limit = st.slider('Requested source count', 3, 10, 6)
    else:
        domain_hint, detail_level, context, sources_limit = 'Auto-detect', 'Detailed', '', 6
    st.divider()
    st.markdown('### Sports coverage')
    st.caption(f'{len(ALL_SPORTS)} sport / competition types listed for automatic research.')
    with st.expander('See supported sports list'):
        for group, items in SPORTS.items():
            st.markdown(f'**{group}**')
            st.write(' • '.join(items))

st.markdown('### 🔎 What do you want to analyse?')
query = st.text_input('Matchup', placeholder='e.g. India vs Australia T20, Lakers vs Celtics, Alcaraz vs Sinner, Naruto vs Sasuke')
col1, col2 = st.columns([1, 3])
with col1:
    predict = st.button('⚡ RESEARCH & PREDICT', use_container_width=True)
with col2:
    st.caption('You do not need to choose an anime setting or manually enter statistics. The AI researches the matchup from the query; optional controls only refine it.')


def get_api_key():
    key = os.getenv('GEMINI_API_KEY', '').strip()
    try:
        if not key:
            key = str(st.secrets.get('GEMINI_API_KEY', '')).strip()
    except Exception:
        pass
    return key


def call_grounded_gemini(user_query, api_key, domain, detail, extra, source_count):
    model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    instruction = f'''You are the research and analysis engine for RAN-NEETI, a multi-sport and fictional-matchup analysis website. Use Google Search grounding to research the exact query. Do not assume the sport; identify it from the matchup. Domain hint: {domain}. Detail: {detail}. User context: {extra or 'None'}. Try to use at least {source_count} useful sources if available, prioritizing official leagues/federations, reliable statistics providers, reputable reporting, and primary/canon references for fiction.

Produce a clear report with these headings:
1. MATCHUP IDENTIFICATION — identify domain, sport/format, teams/players/characters, event/date if verified, and any ambiguity. If ambiguous, state the assumption you used.
2. CURRENT EVIDENCE — recent form / results / relevant stats for real sports; for fictional matchups, compare character version/arc and documented feats. Include source-grounded facts and citations/links from search grounding.
3. OUTCOME ESTIMATE — give outcome probabilities that sum to 100% (for football/soccer include home/side A win, draw, side B win; for sports with no draw use valid outcomes only; for races/competitions give winner/podium or stated outcome format). Clearly label these as an AI research estimate, NOT a validated statistical model probability, unless actual validated model output is available. Do not invent unavailable statistics or pretend to have a live feed. If evidence is thin or contradictory, widen uncertainty and say so.
4. WHY — strongest factors for each side, strengths, weaknesses, matchup advantages, and what evidence supports each.
5. MAJOR MOVES / GAME-CHANGERS — for each side: likely decisive actions or strategies, trigger/when to use, expected impact, risk, and opponent’s best counter. For fiction, only discuss abilities/feats supported by sources and state the selected version/rules.
6. TURNING POINTS — events that could swing the result (line-up/injury/news, early goal, powerplay, weather, fatigue, red card, tactical adjustment, etc. only when relevant).
7. WIN CONDITIONS — concrete conditions each side needs to meet; explain plausible path to victory and how the opponent might stop it.
8. HOW A W/L/D OR RESULT HAPPENS — explain what would have to happen for each outcome, not just who is favoured.
9. WHAT COULD CHANGE THE PREDICTION — missing information, uncertainty, late changes, alternate versions/rules, or source disagreements.
10. SOURCES & FRESHNESS — list cited sources and dates where available; distinguish facts from inference.

Rules: no fabricated citations, feats, scores, injury news, statistics, odds, or certainty. Do not say you scraped Google AI Overview. Use retrieved web evidence and link it. Do not use odds as if they were model probabilities without saying so. If the query is a fictional/anime matchup, percentages are subjective scenario estimates, not empirically calibrated. If there is not enough evidence, say that rather than making confident claims. Plain English, detailed but skimmable.'''
    payload = {
      'contents': [{'role':'user','parts':[{'text': instruction + '\n\nMATCHUP REQUEST: ' + user_query}]}],
      'tools': [{'google_search': {}}],
      'generationConfig': {'temperature': 0.25, 'maxOutputTokens': 8192}
    }
    response = requests.post(url, params={'key': api_key}, json=payload, timeout=120)
    if response.status_code >= 400:
        try: detail_msg = response.json().get('error', {}).get('message', response.text)
        except Exception: detail_msg = response.text
        raise RuntimeError(f'Gemini API returned {response.status_code}: {detail_msg}')
    data = response.json()
    candidates = data.get('candidates', [])
    if not candidates:
        raise RuntimeError('The AI returned no report. Try again or simplify the matchup.')
    parts = candidates[0].get('content', {}).get('parts', [])
    answer = '\n\n'.join(p.get('text','') for p in parts if p.get('text'))
    grounding = candidates[0].get('groundingMetadata', {})
    sources = []
    for item in grounding.get('groundingChunks', []):
        web = item.get('web', {})
        uri, title = web.get('uri'), web.get('title')
        if uri and all(s['url'] != uri for s in sources): sources.append({'title': title or uri, 'url': uri})
    return answer, sources, model

if predict:
    if not query.strip():
        st.warning('Pehle matchup likh — jaise “India vs Australia T20” ya “Naruto vs Sasuke”.')
    else:
        key = get_api_key()
        if not key:
            st.error('AI Search key is not configured yet. The website code is ready, but live Google Search-grounded analysis needs a Gemini API key.')
            st.markdown('**One-time setup for the deployed website:** open Google AI Studio, create an API key if the free tier is available to your account, then add `GEMINI_API_KEY` in Streamlit Community Cloud → App settings → Secrets. Never paste the key into public code or chat.')
            st.link_button('Open Google AI Studio', 'https://aistudio.google.com/app/apikey')
        else:
            with st.spinner('AI is identifying the matchup, searching sources and preparing the analysis…'):
                try:
                    report, sources, model_name = call_grounded_gemini(query.strip(), key, domain_hint, detail_level, context, sources_limit)
                    st.session_state['ran_neeti_last_report'] = {'query': query.strip(), 'report': report, 'sources': sources, 'model': model_name, 'time': datetime.now(timezone.utc).isoformat()}
                except Exception as e:
                    st.error(f'Prediction could not be completed: {e}')
                    st.caption('Check API-key validity, quota, model availability and network access. No prediction is shown when the search/AI call fails.')

if 'ran_neeti_last_report' in st.session_state:
    result = st.session_state['ran_neeti_last_report']
    st.divider()
    st.markdown('## 📡 Prediction intelligence report')
    st.caption(f"Query: {result['query']}  •  Model: {result['model']}  •  Generated: {result['time']}")
    st.markdown(result['report'])
    if result['sources']:
        st.markdown('### 🔗 Retrieved source links')
        for i, src in enumerate(result['sources'], 1):
            st.markdown(f"{i}. [{src['title']}]({src['url']})")
    else:
        st.warning('The response did not return source links in its grounding metadata. Treat factual claims cautiously and retry if needed.')
    st.download_button('⬇️ Download report (.md)', data=f"# RAN-NEETI Report\n\nQuery: {result['query']}\n\nGenerated: {result['time']}\n\n{result['report']}\n\n## Sources\n" + '\n'.join(f"- [{s['title']}]({s['url']})" for s in result['sources']), file_name='ran_neeti_report.md', mime='text/markdown')

st.divider()
st.markdown('## 🧠 How this version works')
cols = st.columns(4)
for col, title, body in zip(cols, ['1 · Identify','2 · Search','3 · Analyse','4 · Explain'], [
    'Reads the matchup and infers sport, format or fictional universe.',
    'Uses Google Search grounding through the Gemini API to find current or source-backed information.',
    'Compares form, stats, abilities, counters and uncertainties relevant to that domain.',
    'Returns outcome estimates, major moves, counters, turning points, win conditions and links.'
]):
    with col:
        st.markdown(f'<div class="panel"><h3 style="font-size:16px">{title}</h3><p>{body}</p></div>', unsafe_allow_html=True)

with st.expander('Important: prediction reliability and academic honesty'):
    st.markdown('''- **Broad sport coverage means broad research coverage, not that every sport has a separately trained ML model.** This version uses search-grounded AI analysis for arbitrary matchups; the generated probabilities are estimates, not validated/calibrated sports-model outputs.
- For a genuine MSc Data Science evaluation, each sport needs suitable historical data, a sport-specific target/features, a time-based holdout test, baseline comparison, and recorded metrics such as accuracy/F1 and probability calibration. Do not claim measured accuracy until the experiment has actually run.
- Fictional/anime matchup percentages are scenario-dependent opinions because universes do not share a common objective measurement scale. Version, feats, setting and rules can change the answer.
- Search results can be incomplete or disagree. Always inspect source links. The app should not be used for betting or as a guarantee of outcomes.
- Google Search grounding and Gemini usage depend on account eligibility, quota, model availability and Google terms. Search is not the same thing as unrestricted scraping of Google AI Overviews.''')

st.markdown('<p class="small">RAN-NEETI • VIT Online MSc Data Science Capstone • Automatic-first, evidence-aware analysis</p>', unsafe_allow_html=True)
