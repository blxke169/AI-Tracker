

import streamlit as st
import pandas as pd
import sqlite3, os, json, math, requests, html
from datetime import datetime, date
from pathlib import Path

st.set_page_config(page_title="EdgeLab | Betting Intelligence", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

st.markdown(r"""
<style>
:root{--bg:#061018;--panel:#0b1724;--line:#173149;--text:#f5f8fb;--muted:#8da2b7;--teal:#18e3b1;--green:#35e985;--red:#ff5e6c;--amber:#ffcc4d;--blue:#4bb8ff;}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;}
[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 24% -10%,rgba(13,87,111,.22),transparent 33%),radial-gradient(circle at 90% 0%,rgba(0,185,145,.10),transparent 28%),linear-gradient(180deg,#061018 0%,#050b12 100%);color:var(--text);}
[data-testid="stHeader"]{background:rgba(6,16,24,.84);backdrop-filter:blur(14px);border-bottom:1px solid rgba(32,65,93,.38);}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#06111a 0%,#050c13 100%);border-right:1px solid #10273a;}
.block-container{max-width:1600px;padding-top:1rem;padding-bottom:3rem;} h1,h2,h3{letter-spacing:-.035em;color:#f8fbff;} h1{font-size:2rem!important;} h2{font-size:1.45rem!important;} p,li{color:#c8d4df;}
[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(14,29,44,.96),rgba(8,19,30,.96));border:1px solid #17344d;border-radius:14px;padding:14px 16px;box-shadow:0 10px 32px rgba(0,0,0,.18);}
[data-testid="stMetricLabel"]{color:#9db0c2;} [data-testid="stMetricValue"]{font-weight:850;letter-spacing:-.035em;} [data-testid="stMetricDelta"]{color:var(--teal)!important;}
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{min-height:43px;border-radius:9px;border:1px solid #22435f;background:linear-gradient(180deg,#102235,#0b1928);color:#eef7fb;font-weight:750;box-shadow:none;}
[data-testid="stFormSubmitButton"]>button{background:linear-gradient(90deg,#08d9a4,#33efa9);color:#022c23;border:0;font-weight:900;}
[data-testid="stForm"]{background:linear-gradient(145deg,rgba(11,23,36,.98),rgba(8,18,29,.96));border:1px solid #17344d;border-radius:14px;padding:1rem;}
[data-baseweb="input"]>div,[data-baseweb="select"]>div,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input{background:#0a1623!important;border-color:#1b3952!important;border-radius:8px!important;}
[data-testid="stDataFrame"]{border:1px solid #17344d;border-radius:12px;overflow:hidden;background:#08131f;}
.top-shell{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:10px 14px;margin:0 0 12px;border:1px solid #163249;border-radius:13px;background:linear-gradient(180deg,rgba(10,24,36,.96),rgba(7,18,28,.94));}
.brand{display:flex;align-items:center;gap:10px;min-width:220px}.brand-mark{width:29px;height:29px;border-radius:8px;display:grid;place-items:center;background:linear-gradient(135deg,#21f0b7,#0ea97f);color:#003b2e;font-weight:950}.brand-name{font-size:1.22rem;font-weight:900}.brand-sub{font-size:.62rem;color:#7890a6;letter-spacing:.16em;text-transform:uppercase}
.search-shell{flex:1;max-width:560px;padding:9px 13px;border-radius:9px;border:1px solid #18364f;color:#8fa6ba;background:#081521}.status-strip{display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end}.status-chip{padding:7px 10px;border:1px solid #17354d;border-radius:9px;background:#081521;min-width:110px}.status-chip b{display:block;color:#21e7b2;font-size:.94rem}.status-chip span{font-size:.65rem;color:#8199ad;text-transform:uppercase;letter-spacing:.08em}
.page-kicker{color:#20e2ae;font-size:.7rem;font-weight:850;letter-spacing:.15em;text-transform:uppercase;margin-bottom:3px}.page-title{font-size:1.62rem;font-weight:900;letter-spacing:-.04em;color:#f7fbff}.page-copy{color:#8fa5ba;margin-top:3px;margin-bottom:12px}
.panel-title{font-size:.95rem;font-weight:850;color:#f3f8fb;margin-bottom:7px}.panel-sub{font-size:.76rem;color:#8399ae}.kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:8px 0 14px}.kpi-card{background:linear-gradient(145deg,#0c1b29,#08131f);border:1px solid #17364f;border-radius:12px;padding:13px 14px;min-height:93px}.kpi-label{font-size:.72rem;color:#90a6ba;margin-bottom:8px}.kpi-value{font-size:1.55rem;font-weight:900;color:#f4fbff}.kpi-delta{font-size:.72rem;color:#20e2ae;margin-top:6px}
.alert-card,.signal{border:1px solid #183a53;border-radius:11px;padding:10px 11px;margin:7px 0;background:#081621}.alert-row{display:flex;gap:10px;align-items:flex-start}.alert-dot{width:8px;height:8px;border-radius:50%;margin-top:6px;flex:0 0 8px}.alert-title{font-weight:800;font-size:.82rem;color:#f4f7fa}.alert-copy,.signal-meta{font-size:.72rem;color:#89a0b4;margin-top:2px;line-height:1.35}.signal-head{display:flex;align-items:center;justify-content:space-between;gap:8px}.badge{display:inline-block;padding:3px 8px;border-radius:6px;font-size:.68rem;font-weight:900}.badge-bet{background:#20e2ae;color:#023b2e}.badge-lean{background:#ffcf4d;color:#423000}.badge-nobet{background:#263748;color:#dbe5ed}.green{color:#22e6b0}.muted{color:#8da2b7}
.sidebar-logo{padding:8px 5px 10px}.sidebar-logo .x{font-weight:950;font-size:1.25rem;color:#f7fbff}.sidebar-logo .y{font-size:.65rem;color:#6f8aa1;letter-spacing:.14em}.ai-off{padding:8px 10px;border-radius:9px;border:1px solid #493e18;background:#1e1b0d;color:#ffd66a;font-size:.76rem}.ai-on{padding:8px 10px;border-radius:9px;border:1px solid #164836;background:#0b211a;color:#63efbf;font-size:.76rem}
@media(max-width:1100px){.kpi-grid{grid-template-columns:repeat(2,1fr)}.status-strip,.search-shell{display:none}}

/* --- Mockup polish pass --- */
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child{display:none!important;}
[data-testid="stSidebar"] [role="radiogroup"] label{
  width:100%!important; padding:9px 11px!important; margin:2px 0!important;
  border-radius:9px!important; border:1px solid transparent!important;
  background:transparent!important; transition:.16s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{
  background:#0a1c2a!important; border-color:#153d55!important; transform:translateX(2px);
}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){
  background:linear-gradient(90deg,rgba(20,226,176,.14),rgba(20,226,176,.04))!important;
  border-color:#1cae8c!important; box-shadow:inset 3px 0 0 #20e2ae;
}
[data-testid="stSidebar"] [role="radiogroup"] label p{font-size:.87rem!important;font-weight:800!important;color:#dfeaf2!important;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p{color:#4df0c2!important;}
[data-testid="stSidebar"] hr{margin:14px 0!important;}
.block-container{padding-left:1.2rem!important;padding-right:1.2rem!important;max-width:1540px!important;}
[data-testid="stHorizontalBlock"]{gap:.8rem!important;}
[data-testid="stMetric"]{min-height:108px;display:flex;justify-content:center;}
[data-testid="stMetricValue"]{font-size:1.7rem!important;}
[data-testid="stMetricLabel"]{font-size:.73rem!important;text-transform:uppercase;letter-spacing:.06em;}
[data-testid="stDataFrame"]{box-shadow:0 8px 28px rgba(0,0,0,.16);}
.mock-table{width:100%;border-collapse:separate;border-spacing:0;background:#08141f;border:1px solid #17344d;border-radius:12px;overflow:hidden;font-size:.77rem;}
.mock-table th{background:#0d1b29;color:#91a8ba;text-align:left;padding:10px;border-bottom:1px solid #1a354c;font-weight:800;text-transform:uppercase;font-size:.66rem;letter-spacing:.05em;}
.mock-table td{padding:10px;border-bottom:1px solid #10283a;color:#d7e3ec;}
.mock-table tr:last-child td{border-bottom:0}.mock-table tr:hover td{background:#0a1a28;}
.status-pill{display:inline-block;padding:3px 8px;border-radius:999px;font-weight:850;font-size:.67rem;border:1px solid transparent;}
.status-won{background:#0b3a2d;color:#53efbd;border-color:#176a52}.status-lost{background:#3a141a;color:#ff7b86;border-color:#722a34}.status-pending{background:#3d3210;color:#ffd769;border-color:#6c5717}.status-push{background:#1d2a38;color:#bdcede;border-color:#30465b}
.section-shell{background:linear-gradient(145deg,rgba(10,24,36,.96),rgba(7,16,26,.96));border:1px solid #17344d;border-radius:14px;padding:14px 15px;margin-bottom:12px;box-shadow:0 12px 32px rgba(0,0,0,.14)}
.alert-card{box-shadow:inset 0 1px 0 rgba(255,255,255,.02)}
.alert-card:hover,.signal:hover{border-color:#24516f;transform:translateY(-1px);}


.sample-warning{padding:8px 10px;border:1px solid #5b4b18;background:#1d190d;border-radius:8px;color:#ffd76a;font-size:.72rem;margin-top:7px;}
.quick-actions{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:8px 0 14px;}
.quick-card{padding:12px 14px;border:1px solid #193a52;border-radius:11px;background:linear-gradient(145deg,#0d1c2a,#08131f);}
.quick-card b{display:block;color:#f4f9fc;font-size:.86rem;margin-bottom:3px}.quick-card span{font-size:.72rem;color:#89a1b5}
.score-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:8px 0 10px;}
.score-card{padding:12px;border:1px solid #193950;border-radius:11px;background:#081621;}
.score-label{font-size:.68rem;color:#8299ad;margin-bottom:5px}.score-value{font-size:1.18rem;font-weight:900;color:#f6fbff}.score-note{font-size:.68rem;color:#20dfad;margin-top:4px;}
@media(max-width:900px){.quick-actions,.score-grid{grid-template-columns:1fr 1fr}}

</style>
""", unsafe_allow_html=True)

DB = Path("betting.db")
SPORTS = ["NBA","NFL","NHL","MLB","NCAAB","NCAAF","AFL","Soccer","Tennis","Horses","Greyhounds"]
BET_TYPES = {
    "NBA":["3PT","Points","Rebounds","Assists","PRA","Steals","Blocks","Threes+","Moneyline","Spread","Total","Other"],
    "NFL":["Passing Yards","Rushing Yards","Receiving Yards","Receptions","TD","Pass Attempts","Moneyline","Spread","Total","Other"],
    "NHL":["Goals","Assists","Points","Shots","SOG","Saves","Moneyline","Puck Line","Total","Other"],
    "MLB":["Hits","Runs","RBI","HR","Strikeouts","Pitcher Outs","Moneyline","Run Line","Total","Other"],
    "NCAAB":["3PT","Points","Rebounds","Assists","PRA","Moneyline","Spread","Total","Other"],
    "NCAAF":["Passing Yards","Rushing Yards","Receiving Yards","TD","Moneyline","Spread","Total","Other"],
    "AFL":["Disposals","Kicks","Handballs","Marks","Tackles","Goals","CBA","Fantasy Score","Team Total","Line","Total","Other"],
    "Soccer":["Goals","Shots","Shots on Target","Assists","Cards","Corners","Moneyline","Draw No Bet","Total","Other"],
    "Tennis":["Match Winner","Games","Sets","Aces","Double Faults","Total Games","Handicap","Other"],
    "Horses":["Win","Place","Top 3","Top 4","Each Way","Exacta","Quinella","Trifecta","First 4","Other"],
    "Greyhounds":["Win","Place","Top 2","Top 3","Top 4","Exacta","Quinella","Trifecta","Other"]
}
FACTOR_HINTS = {
    "NBA":"minutes, usage, matchup, pace, injuries, role, recent hit rate, rest, line movement",
    "NFL":"snap share, route share, target share, carries, matchup, injuries, weather, game script",
    "NHL":"TOI, line assignment, PP role, shots, opponent, goalie, injuries, pace",
    "MLB":"plate appearances, splits, pitcher matchup, park, handedness, bullpen, weather",
    "NCAAB":"minutes, usage, pace, matchup, injuries, rebounding, recent role",
    "NCAAF":"snap share, target share, rushing role, matchup, injuries, weather, game script",
    "AFL":"time on ground, CBA, role, disposals, matchup, venue, weather, injuries",
    "Soccer":"minutes, xG/xA, shots, role, opponent, home/away, lineup, cards, corners",
    "Tennis":"surface, hold/break rates, serve points, return points, fatigue, head-to-head, injury",
    "Horses":"barrier, speed/sectionals, distance, class, weight, track/going, jockey, trainer, pace, market",
    "Greyhounds":"box, early speed, split times, distance, grade, track, interference, recent times, market"
}

def conn():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS bets(
      id INTEGER PRIMARY KEY AUTOINCREMENT, placed_at TEXT, event_date TEXT, sport TEXT, league TEXT,
      event TEXT, book TEXT, bet_type TEXT, market TEXT, selection TEXT, line TEXT,
      odds REAL, closing_odds REAL, stake REAL, result TEXT, pnl REAL,
      reasoning TEXT, post_game_reason TEXT, clv REAL, ai_review TEXT, process_grade TEXT,
      factors_json TEXT, source_note TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS odds_snapshots(
      id INTEGER PRIMARY KEY AUTOINCREMENT, captured_at TEXT, sport TEXT, event TEXT,
      market TEXT, selection TEXT, line TEXT, bookmaker TEXT, odds REAL, source TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS event_data(
      id INTEGER PRIMARY KEY AUTOINCREMENT, captured_at TEXT, sport TEXT, event TEXT,
      subject TEXT, data_json TEXT, source TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reviews(
      id INTEGER PRIMARY KEY AUTOINCREMENT, bet_id INTEGER, created_at TEXT,
      review TEXT, grade TEXT, tags TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bankroll_settings(
      id INTEGER PRIMARY KEY CHECK(id=1), starting_bankroll REAL DEFAULT 1000,
      unit_percent REAL DEFAULT 1.0, staking_mode TEXT DEFAULT 'Flat units',
      kelly_fraction REAL DEFAULT 0.25)""")
    c.execute("""CREATE TABLE IF NOT EXISTS bankroll_transactions(
      id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, txn_date TEXT,
      txn_type TEXT, amount REAL, note TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS multi_legs(
      id INTEGER PRIMARY KEY AUTOINCREMENT, bet_id INTEGER, leg_no INTEGER, sport TEXT, event TEXT,
      bet_type TEXT, market TEXT, selection TEXT, line TEXT, odds REAL, closing_odds REAL, result TEXT DEFAULT 'Pending',
      clv REAL, notes TEXT, FOREIGN KEY(bet_id) REFERENCES bets(id))""")
    # Lightweight migration for existing V4 databases created before multi-leg bet types were added.
    multi_cols={row[1] for row in c.execute("PRAGMA table_info(multi_legs)").fetchall()}
    if "bet_type" not in multi_cols:
        c.execute("ALTER TABLE multi_legs ADD COLUMN bet_type TEXT")
    c.execute("""CREATE TABLE IF NOT EXISTS analysis_log(
      id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT, sport TEXT, selection TEXT, market TEXT,
      odds REAL, user_probability REAL, implied_probability REAL, edge REAL, gate TEXT,
      evidence_quality TEXT, evidence TEXT, reason TEXT)""")
    c.execute("INSERT OR IGNORE INTO bankroll_settings(id,starting_bankroll,unit_percent,staking_mode,kelly_fraction) VALUES(1,1000,1.0,'Flat units',0.25)")
    c.commit()
    return c

def clv(bet, close):
    try:
        b=float(bet); c=float(close)
        # Decimal-odds CLV in implied-probability percentage points.
        # Positive means the closing market implied a higher probability than your entry price.
        return ((1/c)-(1/b))*100
    except: return None

def q(sql,args=()):
    c=conn(); rows=c.execute(sql,args).fetchall(); c.close()
    return pd.DataFrame([dict(r) for r in rows])

def execsql(sql,args=()):
    c=conn(); cur=c.execute(sql,args); c.commit(); out=cur.lastrowid; c.close(); return out

def money(x):
    try:return f"${x:,.2f}" if x>=0 else f"-${abs(x):,.2f}"
    except:return "$0.00"

def pct(x):
    try:return f"{x:.2f}%"
    except:return "—"

def save_event_snapshot(sport,event,subject,payload,source):
    execsql("INSERT INTO event_data(captured_at,sport,event,subject,data_json,source) VALUES(?,?,?,?,?,?)",
            (datetime.now().isoformat(),sport,event,subject,json.dumps(payload),source))

def latest_context(sport, search_text="", limit=8):
    df=q("SELECT * FROM event_data WHERE sport=? ORDER BY captured_at DESC LIMIT 80",(sport,))
    if df.empty: return []
    if search_text.strip():
        term=search_text.strip().lower()
        mask=df.apply(lambda r: term in (str(r.get("event",""))+" "+str(r.get("subject",""))+" "+str(r.get("data_json",""))).lower(),axis=1)
        hit=df[mask]
        if not hit.empty: df=hit
    return df.head(limit).to_dict("records")

@st.cache_data(ttl=300, show_spinner=False)
def fetch_nba_scoreboard(day=None):
    day=(day or date.today()).strftime("%Y%m%d") if hasattr((day or date.today()),"strftime") else str(day).replace("-","")
    url=f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={day}"
    r=requests.get(url,timeout=15); r.raise_for_status(); raw=r.json()
    out=[]
    for e in raw.get("events",[]):
        comp=(e.get("competitions") or [{}])[0]
        teams=[]
        for c in comp.get("competitors",[]):
            teams.append({"team":c.get("team",{}).get("displayName"),"homeAway":c.get("homeAway"),"score":c.get("score")})
        out.append({"id":e.get("id"),"name":e.get("name"),"date":e.get("date"),"status":e.get("status",{}).get("type",{}).get("description"),"teams":teams})
    return out

@st.cache_data(ttl=900, show_spinner=False)
def fetch_afl_games(year=None):
    year=int(year or date.today().year)
    url=f"https://api.squiggle.com.au/?q=games;year={year}"
    r=requests.get(url,headers={"User-Agent":"EdgeLab-Betting-Tracker/1.0"},timeout=15); r.raise_for_status()
    games=r.json().get("games",[])
    games=sorted(games,key=lambda x:str(x.get("date","")),reverse=True)
    return games[:120]

conn().close()

def _secret(name):
    v=os.getenv(name,"")
    if v:
        return v
    try:
        return st.secrets.get(name,"")
    except Exception:
        return ""

def ai_provider():
    """Prefer Groq when configured, otherwise fall back to OpenAI."""
    groq=_secret("GROQ_API_KEY")
    if groq:
        return "Groq",groq
    oa=_secret("OPENAI_API_KEY")
    if oa:
        return "OpenAI",oa
    return None,""

def run_ai_commentary(prompt):
    provider,key=ai_provider()
    if not provider:
        raise RuntimeError("NO_AI_KEY")
    from openai import OpenAI
    if provider=="Groq":
        client=OpenAI(api_key=key,base_url="https://api.groq.com/openai/v1")
        resp=client.responses.create(model="openai/gpt-oss-20b",input=prompt)
    else:
        client=OpenAI(api_key=key)
        resp=client.responses.create(model="gpt-5-mini",input=prompt)
    return provider,resp.output_text

def evidence_audit(sport,evidence,data_ctx):
    """Free deterministic evidence checks; never invents data."""
    e=(evidence or "").lower()
    checks={
        "volume / opportunity":["target","targets","attempt","attempts","minutes","routes","carries","usage","volume","touches"],
        "recent form / sample":["last 5","last 10","recent","season","average","avg","3/3","hit rate","form"],
        "matchup / opponent":["matchup","opponent","defense","defence","coverage","pace","allowed","vs "],
        "role / availability":["role","starter","starting","injury","injuries","questionable","probable","out","minutes"],
        "price / market":["odds","price","line","market","closing","movement","implied"],
    }
    if sport in ("Horses","Greyhounds"):
        checks.update({
            "barrier / box / map":["barrier","box","speed map","map","draw"],
            "track / going":["track","going","heavy","soft","good","distance","course"],
            "class / grade":["class","grade","weight"],
            "sectionals / speed":["sectional","split","early speed","speed figure","time"],
        })
    found=[name for name,keys in checks.items() if any(k in e for k in keys)]
    missing=[name for name in checks if name not in found]
    return found,missing,bool(data_ctx)


def _summary():
    bets=q("SELECT * FROM bets")
    settings=q("SELECT * FROM bankroll_settings WHERE id=1").iloc[0]
    tx=q("SELECT * FROM bankroll_transactions ORDER BY txn_date,id")
    settled=bets[bets.result.isin(["Won","Lost","Push"])].copy() if not bets.empty else pd.DataFrame()
    start=float(settings.starting_bankroll)
    dep=float(tx.loc[tx.txn_type=="Deposit","amount"].sum()) if not tx.empty else 0
    wd=float(tx.loc[tx.txn_type=="Withdrawal","amount"].sum()) if not tx.empty else 0
    pnl=float(settled.pnl.sum()) if not settled.empty else 0
    bank=start+dep-wd+pnl
    stake=float(settled.stake.sum()) if not settled.empty else 0
    roi=pnl/stake*100 if stake else 0
    clv_avg=float(settled.clv.mean()) if not settled.empty and settled.clv.notna().any() else 0
    wl=settled[settled.result.isin(["Won","Lost"])] if not settled.empty else pd.DataFrame()
    win=(wl.result.eq("Won").mean()*100) if not wl.empty else 0
    pending=bets[bets.result.eq("Pending")] if not bets.empty else pd.DataFrame()
    open_stake=float(pending.stake.sum()) if not pending.empty else 0
    return dict(bets=bets,settled=settled,settings=settings,tx=tx,bank=bank,pnl=pnl,roi=roi,clv=clv_avg,win=win,pending=pending,open_stake=open_stake)

summary=_summary()
st.sidebar.markdown("""<div class='sidebar-logo'><div class='x'>◆ EdgeLab</div><div class='y'>INSIGHTS • EDGES • RESULTS</div></div>""",unsafe_allow_html=True)
nav_items=["Dashboard","Today","Analyse Bet","Log Bet","Multis","Bankroll","Performance","AI Review","Data Hub","Bet History","Settings"]
page=st.sidebar.radio("Navigation",nav_items,label_visibility="collapsed",key="main_nav")
ai_commentary_enabled=st.sidebar.toggle("Enable AI commentary",value=False,help="Off = no OpenAI API calls or credits used.")
st.sidebar.markdown("<div class='ai-on'>● AI commentary enabled</div>" if ai_commentary_enabled else "<div class='ai-off'>AI commentary off · no API credits used</div>",unsafe_allow_html=True)
st.sidebar.markdown("---"); st.sidebar.caption("EdgeLab v5 · Mockup-style interface"); st.sidebar.caption("Educational analytics only. Betting involves financial risk.")
st.markdown(f"""<div class='top-shell'><div class='brand'><div class='brand-mark'>E</div><div><div class='brand-name'>EdgeLab</div><div class='brand-sub'>Insights • Edges • Results</div></div></div><div class='search-shell'>⌕ Search teams, players, races, or analyse a bet…</div><div class='status-strip'><div class='status-chip'><span>Bankroll</span><b>{money(summary['bank'])}</b></div><div class='status-chip'><span>Total P&L</span><b>{money(summary['pnl'])}</b></div><div class='status-chip'><span>AI Status</span><b>{'Online' if ai_commentary_enabled else 'Off'}</b></div><div class='status-chip'><span>Open Bets</span><b>{len(summary['pending'])}</b></div></div></div>""",unsafe_allow_html=True)


# TODAY
if page=="Today":
    st.markdown("<div class='page-kicker'>Daily workspace</div><div class='page-title'>Today</div><div class='page-copy'>Open bets, exposure, latest alerts and items that need attention today.</div>",unsafe_allow_html=True)
    s=summary
    today_str=str(date.today())

    t1,t2,t3,t4=st.columns(4)
    todays_bets=s["bets"][s["bets"]["event_date"].astype(str).eq(today_str)] if not s["bets"].empty else pd.DataFrame()
    todays_settled=todays_bets[todays_bets.result.isin(["Won","Lost","Push"])] if not todays_bets.empty else pd.DataFrame()
    todays_pnl=float(todays_settled.pnl.sum()) if not todays_settled.empty else 0.0
    t1.metric("Today's bets",len(todays_bets))
    t2.metric("Open bets",len(s["pending"]))
    t3.metric("Open stake",money(s["open_stake"]))
    t4.metric("Today's P&L",money(todays_pnl))

    st.markdown("<div class='panel-title'>Quick Actions</div>",unsafe_allow_html=True)
    qa1,qa2,qa3=st.columns(3)
    with qa1:
        if st.button("🔎 Analyse Bet",use_container_width=True,key="today_analyse"):
            st.session_state["main_nav"]="Analyse Bet"; st.rerun()
    with qa2:
        if st.button("＋ Log Bet",use_container_width=True,key="today_log"):
            st.session_state["main_nav"]="Log Bet"; st.rerun()
    with qa3:
        if st.button("🧩 Add Multi",use_container_width=True,key="today_multi"):
            st.session_state["main_nav"]="Multis"; st.rerun()

    left,right=st.columns([2.1,1],gap="large")
    with left:
        st.markdown("<div class='panel-title'>Open / Pending Bets</div>",unsafe_allow_html=True)
        if s["pending"].empty:
            st.info("No open bets right now.")
        else:
            cols=["event_date","sport","event","bet_type","selection","odds","stake","result"]
            st.dataframe(s["pending"][cols].sort_values(["event_date","id"],ascending=False),use_container_width=True,hide_index=True,height=260)

        st.markdown("<div class='panel-title'>Today's Bets</div>",unsafe_allow_html=True)
        if todays_bets.empty:
            st.info("No bets dated today yet.")
        else:
            show=todays_bets.copy()
            show["P&L"]=show["pnl"].map(money)
            st.dataframe(show[["sport","event","bet_type","selection","odds","stake","result","P&L"]],use_container_width=True,hide_index=True)

    with right:
        st.markdown("<div class='panel-title'>⚠ Attention</div>",unsafe_allow_html=True)
        msgs=[]
        if s["bank"]>0 and s["open_stake"]/s["bank"]>0.10:
            msgs.append(("Bankroll exposure",f"{s['open_stake']/s['bank']*100:.1f}% of bankroll is currently open."))
        if s["clv"] < -1 and len(s["settled"])>=3:
            msgs.append(("Negative CLV trend",f"Average implied-probability CLV is {s['clv']:.2f}%."))
        old_pending=s["pending"][pd.to_datetime(s["pending"]["event_date"],errors="coerce") < pd.Timestamp(date.today())] if not s["pending"].empty else pd.DataFrame()
        if not old_pending.empty:
            msgs.append(("Needs settlement",f"{len(old_pending)} past-dated pending bet(s) may need a result entered."))
        latest=q("SELECT MAX(captured_at) AS latest FROM event_data")
        if not latest.empty and pd.notna(latest.iloc[0]["latest"]):
            try:
                last=pd.to_datetime(latest.iloc[0]["latest"])
                hrs=(pd.Timestamp.now()-last).total_seconds()/3600
                if hrs>12:
                    msgs.append(("Data may be stale",f"Latest structured sports data is about {hrs:.0f} hours old."))
            except Exception:
                pass
        if not msgs:
            msgs=[("All clear","No urgent rule-based alerts right now.")]
        for title,copy in msgs:
            st.markdown(f"<div class='alert-card'><div class='alert-title'>{title}</div><div class='alert-copy'>{copy}</div></div>",unsafe_allow_html=True)

# DASHBOARD
if page=="Dashboard":
    st.markdown("<div class='page-kicker'>Overview & insights</div><div class='page-title'>Dashboard</div><div class='page-copy'>Your bankroll, process quality, open exposure and latest EdgeLab signals in one view.</div>",unsafe_allow_html=True)

    qa1,qa2,qa3=st.columns(3)
    with qa1:
        if st.button("🔎 Analyse Bet",use_container_width=True,key="dash_analyse"):
            st.session_state["main_nav"]="Analyse Bet"; st.rerun()
    with qa2:
        if st.button("＋ Log Bet",use_container_width=True,key="dash_log"):
            st.session_state["main_nav"]="Log Bet"; st.rerun()
    with qa3:
        if st.button("🧩 Add Multi",use_container_width=True,key="dash_multi"):
            st.session_state["main_nav"]="Multis"; st.rerun()
    s=summary; open_count=len(s["pending"])
    st.markdown(f"""<div class='kpi-grid'><div class='kpi-card'><div class='kpi-label'>Bankroll</div><div class='kpi-value'>{money(s['bank'])}</div><div class='kpi-delta'>{money(s['pnl'])} betting P&L</div></div><div class='kpi-card'><div class='kpi-label'>ROI</div><div class='kpi-value'>{pct(s['roi'])}</div><div class='kpi-delta'>{len(s['settled'])} settled bets</div></div><div class='kpi-card'><div class='kpi-label'>CLV</div><div class='kpi-value'>{pct(s['clv'])}</div><div class='kpi-delta'>Implied-probability CLV</div></div><div class='kpi-card'><div class='kpi-label'>Win Rate</div><div class='kpi-value'>{pct(s['win'])}</div><div class='kpi-delta'>Won / lost bets only</div></div><div class='kpi-card'><div class='kpi-label'>Open Bets</div><div class='kpi-value'>{open_count}</div><div class='kpi-delta'>{money(s['open_stake'])} currently staked</div></div></div>""",unsafe_allow_html=True)
    main,right=st.columns([3.15,1.05],gap="large")
    with main:
        c1,c2=st.columns([1.45,1],gap="large")
        with c1:
            st.markdown("<div class='panel-title'>Bankroll Growth</div><div class='panel-sub'>Settled P&L plus cash movements</div>",unsafe_allow_html=True)
            events=[]
            if not s["tx"].empty:
                for _,r in s["tx"].iterrows(): events.append({"date":pd.to_datetime(r.txn_date,errors="coerce"),"change":float(r.amount) if r.txn_type=="Deposit" else -float(r.amount)})
            if not s["settled"].empty:
                for _,r in s["settled"].iterrows(): events.append({"date":pd.to_datetime(r.event_date,errors="coerce"),"change":float(r.pnl or 0)})
            ev=pd.DataFrame(events); start=float(s["settings"].starting_bankroll)
            if not ev.empty:
                ev=ev.dropna(subset=["date"]).sort_values("date"); ev["Bankroll"]=start+ev["change"].cumsum(); st.area_chart(ev.set_index("date")[["Bankroll"]],use_container_width=True,height=290,color="#18e3b1")
            else: st.info("Settle a bet or add a bankroll transaction to start the growth chart.")
        with c2:
            st.markdown("<div class='panel-title'>Performance by Sport</div><div class='panel-sub'>ROI from settled bets</div>",unsafe_allow_html=True)
            if not s["settled"].empty:
                perf=s["settled"].groupby("sport").agg(Bets=("id","count"),Stake=("stake","sum"),PnL=("pnl","sum")); perf["ROI"]=perf.apply(lambda r:(r.PnL/r.Stake*100) if r.Stake else 0,axis=1); st.bar_chart(perf[["ROI"]],use_container_width=True,height=290,color="#18e3b1")
            else: st.info("No settled bets yet.")

        st.markdown("<div class='panel-title'>Model / Process Scorecard</div><div class='panel-sub'>Process metrics from your settled history</div>",unsafe_allow_html=True)
        settled=s["settled"].copy()
        if settled.empty:
            st.info("Settle more bets to build your process scorecard.")
        else:
            pos_clv=int((settled["clv"].fillna(0)>0).sum())
            neg_clv=int((settled["clv"].fillna(0)<0).sum())
            avg_stake_pct=(settled["stake"].mean()/s["bank"]*100) if s["bank"] else 0
            by_type=settled.groupby("bet_type").agg(Stake=("stake","sum"),PnL=("pnl","sum"),Bets=("id","count"))
            by_type["ROI"]=by_type.apply(lambda r:(r.PnL/r.Stake*100) if r.Stake else 0,axis=1)
            best_type=by_type["ROI"].idxmax() if not by_type.empty else "—"
            worst_type=by_type["ROI"].idxmin() if not by_type.empty else "—"
            score_html=f"""
            <div class="score-grid">
              <div class="score-card"><div class="score-label">Avg CLV</div><div class="score-value">{pct(s['clv'])}</div><div class="score-note">{pos_clv} positive / {neg_clv} negative</div></div>
              <div class="score-card"><div class="score-label">Avg Stake / Bankroll</div><div class="score-value">{avg_stake_pct:.1f}%</div><div class="score-note">Exposure discipline</div></div>
              <div class="score-card"><div class="score-label">Best Bet Type</div><div class="score-value">{best_type}</div><div class="score-note">By ROI</div></div>
              <div class="score-card"><div class="score-label">Worst Bet Type</div><div class="score-value">{worst_type}</div><div class="score-note">Review for leaks</div></div>
            </div>"""
            st.markdown(score_html,unsafe_allow_html=True)
            st.dataframe(by_type.reset_index()[["bet_type","Bets","ROI","PnL"]],use_container_width=True,hide_index=True,height=220)

        st.markdown("<div class='panel-title'>Recent Bets</div>",unsafe_allow_html=True)
        if not s["bets"].empty:
            recent=s["bets"].sort_values(["event_date","id"],ascending=False).head(10).copy(); recent["P&L"]=recent["pnl"].map(money); recent["CLV"]=recent["clv"].map(pct)
            rows=[]
            for _,r in recent.iterrows():
                result=str(r.get("result","Pending")); cls={"Won":"status-won","Lost":"status-lost","Pending":"status-pending","Push":"status-push"}.get(result,"status-push")
                rows.append(f"<tr><td>{html.escape(str(r.get('event_date','')))}</td><td>{html.escape(str(r.get('sport','')))}</td><td>{html.escape(str(r.get('event','')))}</td><td>{html.escape(str(r.get('bet_type','')))}</td><td>{html.escape(str(r.get('selection','')))}</td><td>{float(r.get('odds') or 0):.2f}</td><td>{money(float(r.get('stake') or 0))}</td><td><span class='status-pill {cls}'>{html.escape(result)}</span></td><td>{html.escape(str(r.get('P&L','')))}</td><td>{html.escape(str(r.get('CLV','')))}</td></tr>")
            table="<table class='mock-table'><thead><tr><th>Date</th><th>Sport</th><th>Event</th><th>Bet type</th><th>Selection</th><th>Odds</th><th>Stake</th><th>Result</th><th>P&L</th><th>CLV</th></tr></thead><tbody>"+"".join(rows)+"</tbody></table>"
            st.markdown(table,unsafe_allow_html=True)
        else: st.info("Log your first bet to populate this table.")
    with right:
        st.markdown("<div class='panel-title'>🔔 AI Alerts</div><div class='panel-sub'>Rule-based alerts from stored data and bankroll</div>",unsafe_allow_html=True)
        alerts=[]
        # Stronger rule-based alerts that work without paid AI.
        if s["bank"]>0 and s["open_stake"]/s["bank"]>0.10:
            alerts.append(("amber","Bankroll warning",f"Open stake is {s['open_stake']/s['bank']*100:.1f}% of bankroll. Consider concentration risk."))
        if not s["pending"].empty:
            exp=s["pending"].groupby("sport")["stake"].sum().sort_values(ascending=False)
            if len(exp) and s["bank"]>0 and float(exp.iloc[0])/s["bank"]>0.08:
                alerts.append(("amber","Sport concentration",f"{exp.index[0]} accounts for {float(exp.iloc[0])/s['bank']*100:.1f}% of bankroll in open stake."))
        if s["clv"] < -1 and len(s["settled"])>=3:
            alerts.append(("red","Price warning",f"Average CLV is {s['clv']:.2f}%. Your entries have been worse than the close on average."))
        elif s["clv"] > 1 and len(s["settled"])>=3:
            alerts.append(("green","Positive CLV trend",f"Average CLV is {s['clv']:.2f}% across settled bets."))
        if not s["settled"].empty:
            recent_results=s["settled"].sort_values(["event_date","id"],ascending=False).head(5)["result"].tolist()
            loss_streak=0
            for r in recent_results:
                if r=="Lost": loss_streak+=1
                else: break
            if loss_streak>=3:
                alerts.append(("red","Losing streak",f"{loss_streak} consecutive losses. Avoid stake escalation and review process quality."))
            bt=s["settled"].groupby("bet_type").agg(Stake=("stake","sum"),PnL=("pnl","sum"),Bets=("id","count"))
            bt["ROI"]=bt.apply(lambda r:(r.PnL/r.Stake*100) if r.Stake else 0,axis=1)
            bad=bt[(bt["Bets"]>=5)&(bt["ROI"]<-10)]
            if not bad.empty:
                name=bad["ROI"].idxmin()
                alerts.append(("red","Bet-type leak",f"{name} is running at {bad.loc[name,'ROI']:.1f}% ROI over {int(bad.loc[name,'Bets'])} bets."))
        data_latest=q("SELECT captured_at,sport,event,source FROM event_data ORDER BY captured_at DESC LIMIT 1")
        if not data_latest.empty:
            rr=data_latest.iloc[0]
            alerts.append(("blue","Data updated",f"{rr.sport}: {rr.event} · {rr.source}"))
            try:
                hrs=(pd.Timestamp.now()-pd.to_datetime(rr.captured_at)).total_seconds()/3600
                if hrs>12:
                    alerts.append(("amber","Data freshness warning",f"Latest structured sports data is about {hrs:.0f} hours old."))
            except Exception:
                pass
        if open_count:
            alerts.append(("green","Open positions",f"{open_count} pending bet{'s' if open_count!=1 else ''} with {money(s['open_stake'])} at risk."))
        if not alerts: alerts=[("#4bb8ff","No active alerts","Log bets and fetch data to generate alerts.")]
        for col,title,copy in alerts[:5]: st.markdown(f"<div class='alert-card'><div class='alert-row'><div class='alert-dot' style='background:{col}'></div><div><div class='alert-title'>{title}</div><div class='alert-copy'>{copy}</div></div></div></div>",unsafe_allow_html=True)
        st.markdown("<div class='panel-title' style='margin-top:14px'>🧠 AI Recommendations</div><div class='panel-sub'>Latest BET / LEAN / NO BET signals from your analysis engine</div>",unsafe_allow_html=True)
        signals=q("SELECT * FROM analysis_log ORDER BY id DESC LIMIT 5")
        if signals.empty: st.markdown("<div class='signal'><div class='signal-head'><span class='badge badge-nobet'>WAITING</span><span class='muted'>No analyses yet</span></div><div class='signal-meta'>Run Analyse Bet to populate this panel.</div></div>",unsafe_allow_html=True)
        else:
            for _,r in signals.iterrows():
                cls="badge-bet" if r.gate=="BET" else "badge-lean" if r.gate=="LEAN" else "badge-nobet"; edge=f"{float(r.edge):+.1f} pp" if pd.notna(r.edge) else "edge unknown"
                st.markdown(f"<div class='signal'><div class='signal-head'><span class='badge {cls}'>{r.gate}</span><span class='green'>{edge}</span></div><div class='alert-title' style='margin-top:7px'>{r.sport} · {r.selection or r.market}</div><div class='signal-meta'>{r.market} @ {float(r.odds):.2f}</div></div>",unsafe_allow_html=True)

# PERFORMANCE
if page=="Performance":
    if len(summary["settled"]) < 20:
        st.warning(f"Low sample: {len(summary['settled'])} settled bets. Treat ROI, win rate and sport splits as preliminary.")
    df=q("SELECT * FROM bets")
    settings=q("SELECT * FROM bankroll_settings WHERE id=1").iloc[0]
    tx=q("SELECT * FROM bankroll_transactions ORDER BY txn_date,id")
    start_bank=float(settings.starting_bankroll)
    deposits=float(tx.loc[tx.txn_type=="Deposit","amount"].sum()) if not tx.empty else 0
    withdrawals=float(tx.loc[tx.txn_type=="Withdrawal","amount"].sum()) if not tx.empty else 0
    settled_all=df[df.result.isin(["Won","Lost","Push"])].copy() if not df.empty else pd.DataFrame()
    total_pnl=float(settled_all.pnl.sum()) if not settled_all.empty else 0
    current_bank=start_bank+deposits-withdrawals+total_pnl
    unit_value=current_bank*float(settings.unit_percent)/100

    a,b,c,d,e=st.columns(5)
    a.metric("Current Bankroll",money(current_bank),money(current_bank-start_bank-deposits+withdrawals))
    b.metric("Total P&L",money(total_pnl))
    total_stake=float(settled_all.stake.sum()) if not settled_all.empty else 0
    b_roi=total_pnl/total_stake*100 if total_stake else 0
    c.metric("ROI",pct(b_roi))
    avg_clv=float(settled_all.clv.mean()) if not settled_all.empty and settled_all.clv.notna().any() else 0
    d.metric("Avg CLV",pct(avg_clv))
    e.metric("1 Unit",money(unit_value))

    if df.empty:
        st.info("Your dashboard is empty. Log your first bet to start building your performance history.")
    else:
        sport_filter=st.selectbox("Sport",["All"]+SPORTS,key="dashsport")
        dff=df if sport_filter=="All" else df[df.sport==sport_filter]
        settled=dff[dff.result.isin(["Won","Lost","Push"])].copy()
        if not settled.empty:
            st.markdown("### Performance overview")
            c1,c2=st.columns(2)
            with c1:
                daily=settled.copy(); daily["event_date"]=pd.to_datetime(daily.event_date,errors="coerce")
                daily=daily.dropna(subset=["event_date"]).sort_values(["event_date","id"])
                if not daily.empty:
                    daily["Cumulative P&L"]=daily.pnl.cumsum()
                    st.caption("Cumulative profit / loss")
                    st.line_chart(daily.set_index("event_date")[["Cumulative P&L"]],use_container_width=True)
            with c2:
                outcomes=settled[settled.result.isin(["Won","Lost","Push"])].groupby("result").size()
                st.caption("Bet outcomes")
                if not outcomes.empty: st.bar_chart(outcomes,use_container_width=True)

            c3,c4=st.columns(2)
            with c3:
                sport_perf=settled.groupby("sport").agg(PnL=("pnl","sum")).sort_values("PnL",ascending=False)
                st.caption("P&L by sport")
                if not sport_perf.empty: st.bar_chart(sport_perf,use_container_width=True)
            with c4:
                type_perf=settled.groupby("bet_type").agg(PnL=("pnl","sum")).sort_values("PnL",ascending=False).head(12)
                st.caption("P&L by bet type")
                if not type_perf.empty: st.bar_chart(type_perf,use_container_width=True)

            st.markdown("### Performance by bet type")
            g=settled.groupby("bet_type").agg(Bets=("id","count"),Stake=("stake","sum"),PnL=("pnl","sum"),CLV=("clv","mean")).reset_index()
            g["ROI"]=g.apply(lambda r:r.PnL/r.Stake*100 if r.Stake else 0,axis=1)
            g["P&L"]=g.PnL.map(money); g["ROI"]=g.ROI.map(pct); g["CLV"]=g.CLV.map(pct)
            st.dataframe(g[["bet_type","Bets","Stake","P&L","ROI","CLV"]],use_container_width=True,hide_index=True)
            st.markdown("### Recent bets")
            cols=["id","event_date","sport","event","bet_type","selection","line","odds","closing_odds","result","pnl","clv","process_grade"]
            show=settled.sort_values(["event_date","id"],ascending=False)[cols].copy()
            show["pnl"]=show.pnl.map(money); show["clv"]=show.clv.map(pct)
            st.dataframe(show,use_container_width=True,hide_index=True)
        else:
            st.info("No settled bets for this filter yet.")

# BANKROLL MANAGER
if page=="Bankroll":
    st.markdown("<div class='page-kicker'>Money management</div><div class='page-title'>Bankroll</div>",unsafe_allow_html=True)
    st.caption("Manage your bankroll, staking rules, cash movements and risk. Settled bet P&L is included automatically.")
    settings=q("SELECT * FROM bankroll_settings WHERE id=1").iloc[0]
    tx=q("SELECT * FROM bankroll_transactions ORDER BY txn_date,id")
    allbets=q("SELECT * FROM bets")
    settled=allbets[allbets.result.isin(["Won","Lost","Push"])].copy() if not allbets.empty else pd.DataFrame()
    start_bank=float(settings.starting_bankroll)
    dep=float(tx.loc[tx.txn_type=="Deposit","amount"].sum()) if not tx.empty else 0
    wd=float(tx.loc[tx.txn_type=="Withdrawal","amount"].sum()) if not tx.empty else 0
    bpnl=float(settled.pnl.sum()) if not settled.empty else 0
    current=start_bank+dep-wd+bpnl
    unit=current*float(settings.unit_percent)/100

    m1,m2,m3,m4,m5=st.columns(5)
    m1.metric("Starting Bankroll",money(start_bank)); m2.metric("Current Bankroll",money(current))
    m3.metric("Betting P&L",money(bpnl)); m4.metric("1 Unit",money(unit)); m5.metric("Net Cash Flow",money(dep-wd))

    left,right=st.columns([1,1])
    with left:
        st.markdown("### Bankroll settings")
        with st.form("bankroll_settings_form"):
            sb=st.number_input("Starting bankroll",min_value=0.0,value=float(settings.starting_bankroll),step=50.0)
            up=st.number_input("Unit size (% of current bankroll)",min_value=0.1,max_value=10.0,value=float(settings.unit_percent),step=0.1)
            mode=st.selectbox("Staking mode",["Flat units","% bankroll","Fractional Kelly"],index=["Flat units","% bankroll","Fractional Kelly"].index(settings.staking_mode) if settings.staking_mode in ["Flat units","% bankroll","Fractional Kelly"] else 0)
            kf=st.select_slider("Kelly fraction",options=[0.10,0.20,0.25,0.33,0.50,0.75,1.0],value=float(settings.kelly_fraction) if float(settings.kelly_fraction) in [0.10,0.20,0.25,0.33,0.50,0.75,1.0] else 0.25)
            if st.form_submit_button("Save bankroll settings",use_container_width=True):
                execsql("UPDATE bankroll_settings SET starting_bankroll=?,unit_percent=?,staking_mode=?,kelly_fraction=? WHERE id=1",(sb,up,mode,kf))
                st.success("Bankroll settings saved."); st.rerun()
    with right:
        st.markdown("### Deposit / withdrawal")
        with st.form("cash_form"):
            td=st.date_input("Date",date.today(),key="cashdate")
            typ=st.selectbox("Transaction",["Deposit","Withdrawal"])
            amt=st.number_input("Amount",min_value=0.01,value=50.0,step=10.0)
            note=st.text_input("Note",placeholder="Optional note")
            if st.form_submit_button("Add transaction",use_container_width=True):
                execsql("INSERT INTO bankroll_transactions(created_at,txn_date,txn_type,amount,note) VALUES(?,?,?,?,?)",(datetime.now().isoformat(),str(td),typ,amt,note))
                st.success(f"{typ} recorded."); st.rerun()

    st.markdown("### Bankroll growth")
    events=[]
    if not tx.empty:
        for _,r in tx.iterrows():
            events.append({"date":pd.to_datetime(r.txn_date,errors="coerce"),"change":float(r.amount) if r.txn_type=="Deposit" else -float(r.amount),"kind":r.txn_type})
    if not settled.empty:
        for _,r in settled.iterrows():
            events.append({"date":pd.to_datetime(r.event_date,errors="coerce"),"change":float(r.pnl or 0),"kind":"Bet P&L"})
    ev=pd.DataFrame(events)
    peak=start_bank; max_dd=0.0
    if not ev.empty:
        ev=ev.dropna(subset=["date"]).sort_values("date")
        ev["Bankroll"]=start_bank+ev.change.cumsum()
        ev["Peak"]=ev.Bankroll.cummax().clip(lower=start_bank)
        ev["Drawdown"]=ev.Bankroll-ev.Peak
        peak=max(start_bank,float(ev.Bankroll.max()))
        max_dd=float(ev.Drawdown.min()) if not ev.empty else 0
        st.line_chart(ev.set_index("date")[["Bankroll"]],use_container_width=True)
    else:
        st.info("Your bankroll chart will appear after you settle a bet or add a transaction.")
    x1,x2,x3,x4=st.columns(4)
    x1.metric("Peak Bankroll",money(peak)); x2.metric("Max Drawdown",money(max_dd))
    winrate=(settled.result.eq("Won").sum()/settled.result.isin(["Won","Lost"]).sum()*100) if not settled.empty and settled.result.isin(["Won","Lost"]).sum() else 0
    x3.metric("Win Rate",pct(winrate)); x4.metric("Settled Bets",len(settled))

    if not settled.empty:
        trend=settled.copy(); trend["event_date"]=pd.to_datetime(trend.event_date,errors="coerce"); trend=trend.dropna(subset=["event_date"]).set_index("event_date")
        if not trend.empty:
            st.markdown("### P&L by period")
            period=st.radio("View",["Daily","Weekly","Monthly"],horizontal=True,key="pnlperiod")
            rule={"Daily":"D","Weekly":"W","Monthly":"ME"}[period]
            try: period_pnl=trend["pnl"].resample(rule).sum().to_frame("P&L")
            except ValueError: period_pnl=trend["pnl"].resample("M").sum().to_frame("P&L")
            st.bar_chart(period_pnl,use_container_width=True)

    st.markdown("### Performance breakdown")
    p1,p2=st.columns(2)
    with p1:
        if not settled.empty:
            bysport=settled.groupby("sport").agg(PnL=("pnl","sum"),Stake=("stake","sum"),Bets=("id","count"))
            bysport["ROI"]=bysport.apply(lambda r:r.PnL/r.Stake*100 if r.Stake else 0,axis=1)
            st.caption("Profit / loss by sport")
            st.bar_chart(bysport[["PnL"]],use_container_width=True)
    with p2:
        if not settled.empty:
            allocation=settled.groupby("sport")["stake"].sum().sort_values(ascending=False)
            st.caption("Stake allocation by sport")
            # Streamlit has no native pie chart, so use Altair if available through Streamlit.
            try:
                import altair as alt
                pie=allocation.reset_index(); pie.columns=["Sport","Stake"]
                chart=alt.Chart(pie).mark_arc(innerRadius=55).encode(theta=alt.Theta("Stake:Q"),color=alt.Color("Sport:N"),tooltip=["Sport:N",alt.Tooltip("Stake:Q",format="$.2f")]).properties(height=330)
                st.altair_chart(chart,use_container_width=True)
            except Exception:
                st.bar_chart(allocation,use_container_width=True)

    st.markdown("### Stake calculator")
    sc1,sc2,sc3=st.columns(3)
    calc_odds=sc1.number_input("Bet odds",min_value=1.01,value=1.90,step=0.01,key="calcodds")
    est_prob=sc2.number_input("Your estimated win probability (%)",min_value=0.1,max_value=99.9,value=55.0,step=0.5)
    units=sc3.number_input("Flat units",min_value=0.1,value=1.0,step=0.25)
    flat_stake=unit*units
    pct_stake=current*float(settings.unit_percent)/100*units
    b=calc_odds-1; p=est_prob/100; qv=1-p
    full_kelly=max(0,(b*p-qv)/b) if b>0 else 0
    kelly_stake=current*full_kelly*float(settings.kelly_fraction)
    recommended=flat_stake if settings.staking_mode=="Flat units" else pct_stake if settings.staking_mode=="% bankroll" else kelly_stake
    st.metric(f"Suggested stake · {settings.staking_mode}",money(recommended))
    if current>0 and recommended/current>0.05:
        st.warning(f"This stake is {recommended/current*100:.1f}% of your bankroll. Large single-bet exposure can create severe drawdowns.")
    st.caption("Kelly staking depends on your probability estimate being well calibrated. It is a sizing tool, not a guarantee of profit.")

    if not tx.empty:
        st.markdown("### Cash transaction history")
        st.dataframe(tx[["txn_date","txn_type","amount","note"]].sort_values("txn_date",ascending=False),use_container_width=True,hide_index=True)

# LOG BET
if page in ("Log Bet","Multis"):
    st.markdown("<div class='page-kicker'>Track your wagers</div><div class='page-title'>Log Bet / Multi</div>",unsafe_allow_html=True)
    st.caption("Log a single or a multi. Multi legs are stored individually so you can later see which markets are helping or hurting your parlays.")
    wager_type=st.radio("Wager type",["Single","Multi / Parlay"],horizontal=True,index=1 if page=="Multis" else 0,key="wager_type")
    if wager_type=="Single":
        c1,c2,c3=st.columns(3)
        event_date=c1.date_input("Event date",date.today(),key="sdate")
        sport=c2.selectbox("Sport",SPORTS,key="ssport")
        league=c3.text_input("League",value="",key="sleague")

        c1,c2,c3=st.columns(3)
        bt=c1.selectbox("Bet type",BET_TYPES.get(sport,["Other"]),key="sbt")
        market=c2.text_input("Market",placeholder="Over/Under, handicap, win, place...",key="smarket")
        selection=c3.text_input("Selection / Player / Runner",key="ssel")

        event=st.text_input("Event / Race",key="sevent")
        book=st.text_input("Sportsbook",value="Sportsbet",key="sbook")

        c1,c2,c3=st.columns(3)
        line=c1.text_input("Line",key="sline")
        odds=c2.number_input("Odds taken (decimal)",min_value=1.01,value=1.91,step=0.01,key="sodds")
        close=c3.number_input("Closing odds (if known)",min_value=1.01,value=1.91,step=0.01,key="sclose")
        stake=st.number_input("Stake",min_value=0.0,value=20.0,step=5.0,key="sstake")
        reasoning=st.text_area("Your reasoning",placeholder="What was your thesis? Why did you think the price was wrong?",key="sreason")
        st.markdown("### Analysis context")
        raw=st.text_area(f"Key factors ({FACTOR_HINTS[sport]})",placeholder="Optional. Paste relevant stats, lineup/race notes, weather, sectionals, etc.",key="sfactors")
        source_note=st.text_input("Data source / note",value="Manual entry",key="ssource")

        if st.button("Save Single",use_container_width=True,key="save_single"):
            cv=clv(odds,close)
            execsql("""INSERT INTO bets(placed_at,event_date,sport,league,event,book,bet_type,market,selection,line,odds,closing_odds,stake,result,pnl,reasoning,post_game_reason,clv,ai_review,process_grade,factors_json,source_note)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (datetime.now().isoformat(),str(event_date),sport,league,event,book,bt,market,selection,line,odds,close,stake,"Pending",0,reasoning,"",cv,"","",json.dumps({"raw_factors":raw,"wager_type":"single"}),source_note))
            st.success("Single saved."); st.rerun()
    else:
        st.info("Choose the number of legs. Each leg's Bet type changes immediately when you change that leg's sport.")
        nlegs=st.number_input("Number of legs",min_value=2,max_value=12,value=3,step=1,key="nlegs")
        c1,c2,c3=st.columns(3)
        event_date=c1.date_input("Bet date / main event date",date.today(),key="mdate")
        book=c2.text_input("Sportsbook",value="Sportsbet",key="mbook")
        stake=c3.number_input("Stake",min_value=0.0,value=20.0,step=5.0,key="mstake")
        multi_name=st.text_input("Multi name",placeholder="e.g. Wednesday NBA 4-leg",key="mname")
        reasoning=st.text_area("Overall multi reasoning",placeholder="Why do these legs belong in the multi? Note any correlations or risks.",key="mreason")

        legs=[]
        for i in range(int(nlegs)):
            st.markdown(f"#### Leg {i+1}")
            a,b,c,d=st.columns(4)
            lsport=a.selectbox("Sport",SPORTS,key=f"lsport{i}")
            lbet_type=b.selectbox("Bet type",BET_TYPES.get(lsport,["Other"]),key=f"lbt{i}")
            levent=c.text_input("Event",key=f"levent{i}")
            lodds=d.number_input("Odds",min_value=1.01,value=1.50,step=0.01,key=f"lodds{i}")
            e,f,g,h=st.columns(4)
            lmarket=e.text_input("Market",placeholder="Over/Under, handicap, win, place...",key=f"lmarket{i}")
            lselection=f.text_input("Selection",key=f"lsel{i}")
            lline=g.text_input("Line",key=f"lline{i}")
            lnotes=h.text_input("Notes",key=f"lnotes{i}")
            legs.append((lsport,lbet_type,levent,lmarket,lselection,lline,lodds,lnotes))

        source_note=st.text_input("Data source / note",value="Manual entry",key="msource")
        combined=math.prod([x[6] for x in legs]) if legs else 1.0
        m1,m2,m3=st.columns(3)
        m1.metric("Combined odds",f"{combined:.2f}")
        m2.metric("Potential return",money(stake*combined))
        m3.metric("Potential profit",money(stake*(combined-1)))

        if st.button("Save Multi",use_container_width=True,key="save_multi"):
            label=multi_name.strip() or f"{len(legs)}-Leg Multi"
            bet_id=execsql("""INSERT INTO bets(placed_at,event_date,sport,league,event,book,bet_type,market,selection,line,odds,closing_odds,stake,result,pnl,reasoning,post_game_reason,clv,ai_review,process_grade,factors_json,source_note)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (datetime.now().isoformat(),str(event_date),"Multi","",label,book,"Multi / Parlay","Multi",label,f"{len(legs)} legs",combined,combined,stake,"Pending",0,reasoning,"",None,"","",json.dumps({"wager_type":"multi","legs":len(legs)}),source_note))
            for i,leg in enumerate(legs,1):
                execsql("INSERT INTO multi_legs(bet_id,leg_no,sport,bet_type,event,market,selection,line,odds,closing_odds,result,clv,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (bet_id,i,leg[0],leg[1],leg[2],leg[3],leg[4],leg[5],leg[6],leg[6],"Pending",None,leg[7]))
            st.success(f"Multi saved — combined odds {combined:.2f} · potential return {money(stake*combined)} · potential profit {money(stake*(combined-1))}")
            st.rerun()

# PRE-BET ANALYST
if page=="Analyse Bet":
    st.markdown("<div class='page-kicker'>Decision engine</div><div class='page-title'>Analyse Bet</div>",unsafe_allow_html=True)
    st.caption("A decision gate, not a pick generator. It can return BET, LEAN or NO BET and must not invent missing evidence.")
    with st.form("prebet"):
        c1,c2,c3=st.columns(3)
        asport=c1.selectbox("Sport",SPORTS,key="asport")
        aselection=c2.text_input("Selection",placeholder="Player / team / runner")
        amarket=c3.text_input("Market + line",placeholder="Over 2.5 threes")
        aodds=c1.number_input("Available decimal odds",min_value=1.01,value=1.90,step=0.01)
        aprob=c2.number_input("Your estimated win probability % (optional)",min_value=0.0,max_value=100.0,value=0.0,step=0.5)
        confidence=c3.selectbox("Evidence quality",["Low / incomplete","Medium","High / well sourced"])
        evidence=st.text_area("Evidence / reasoning",placeholder="Paste the stats and information you actually have. Missing data is okay — the analyst should say NO BET when evidence is insufficient.")
        submitted=st.form_submit_button("Analyse Bet",use_container_width=True)
    if submitted:
        implied=100/aodds
        edge=(aprob-implied) if aprob>0 else None
        # deterministic safety gate before AI
        if not evidence.strip() or confidence=="Low / incomplete" or aprob<=0:
            gate="NO BET"; reason="Insufficient reliable evidence or no probability estimate."
        elif edge < 2:
            gate="NO BET"; reason=f"Estimated edge is only {edge:.1f} percentage points."
        elif edge < 5:
            gate="LEAN"; reason=f"Estimated edge is {edge:.1f} percentage points, but not strong enough for a full BET signal."
        else:
            gate="BET"; reason=f"Estimated edge is {edge:.1f} percentage points, subject to the evidence being accurate."
        execsql("""INSERT INTO analysis_log(created_at,sport,selection,market,odds,user_probability,implied_probability,edge,gate,evidence_quality,evidence,reason) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",(datetime.now().isoformat(),asport,aselection,amarket,float(aodds),float(aprob),float(implied),float(edge) if edge is not None else None,gate,confidence,evidence,reason))
        st.markdown(f"<div class='page-kicker'>Recommendation</div><div class='page-title'>{gate}</div><div class='page-copy'>{reason}</div>",unsafe_allow_html=True)
        x1,x2,x3=st.columns(3)
        x1.metric("Market implied probability",f"{implied:.1f}%")
        x2.metric("Your probability",f"{aprob:.1f}%" if aprob else "Not supplied")
        x3.metric("Estimated edge",f"{edge:.1f} pp" if edge is not None else "Unknown")
        data_ctx=latest_context(asport, aselection or amarket, 8)
        if data_ctx:
            st.markdown("### Connected data context")
            st.caption("Recent structured snapshots stored by EdgeLab. These are context only unless they contain the exact player/market information needed.")
            st.dataframe(pd.DataFrame(data_ctx)[["captured_at","event","subject","source"]],use_container_width=True,hide_index=True)

        found,missing,has_ctx=evidence_audit(asport,evidence,data_ctx)
        st.markdown("### Evidence check")
        a1,a2=st.columns(2)
        with a1:
            st.markdown("**Covered in your reasoning**")
            if found:
                for item in found[:6]:
                    st.markdown(f"✓ {item}")
            else:
                st.caption("No structured evidence categories detected.")
        with a2:
            st.markdown("**Still worth verifying**")
            if missing:
                for item in missing[:6]:
                    st.markdown(f"• {item}")
            else:
                st.caption("Your write-up covers the main evidence categories.")
        if not has_ctx:
            st.caption("EdgeLab does not currently have exact connected player/market data for this selection, so it cannot independently verify those claims yet.")

        provider,key=ai_provider()
        if not ai_commentary_enabled:
            st.info("AI commentary is switched off. No AI API call was made. The rule-based decision and evidence checks above are still active.")
        elif provider:
            try:
                prompt=f"""Act as a conservative betting process analyst. Do not invent facts, statistics, injuries, odds movement, or live data.
SPORT: {asport}
SELECTION: {aselection}
MARKET: {amarket}
ODDS: {aodds}
MARKET IMPLIED PROBABILITY: {implied:.2f}%
USER PROBABILITY: {aprob if aprob else 'not supplied'}%
EVIDENCE QUALITY: {confidence}
SUPPLIED EVIDENCE: {evidence}
CONNECTED DATA AVAILABLE: {'yes' if data_ctx else 'no'}
SAFETY GATE: {gate} — {reason}

Critique the user's thesis rather than agreeing with it. Separate claims supported by supplied/connected evidence from assumptions. Use five short sections:
1. Verdict
2. Price / Edge
3. Evidence that supports the thesis
4. Risks / Missing Data
5. What would change the decision

Never upgrade a NO BET safety gate to BET. If exact player or market data is missing, say that clearly."""
                used_provider,assessment=run_ai_commentary(prompt)
                st.markdown(f"### AI assessment · {used_provider}")
                st.write(assessment)
            except Exception as ex:
                msg=str(ex).lower()
                if "rate" in msg or "429" in msg or "quota" in msg:
                    st.info("AI commentary hit the provider's free-tier/rate limit. The rule-based analysis and evidence checks still worked.")
                elif "invalid_api_key" in msg or "incorrect api key" in msg or "401" in msg:
                    st.info("The configured AI API key was rejected. The rule-based analysis and evidence checks still worked.")
                else:
                    st.info("AI commentary is temporarily unavailable. The rule-based analysis and evidence checks still worked.")
        else:
            st.caption("AI commentary is enabled, but no GROQ_API_KEY or OPENAI_API_KEY is configured. Add either key in Streamlit Secrets; the rule-based analysis still works without one.")

# POST GAME
if page=="AI Review":
    st.markdown("<div class='page-kicker'>Post-event process review</div><div class='page-title'>AI Review</div>",unsafe_allow_html=True)
    st.caption("Grade the decision separately from the outcome. A losing bet can still be a good bet, and vice versa.")
    df=q("SELECT * FROM bets ORDER BY event_date DESC,id DESC")
    if df.empty: st.info("Log a bet first.")
    else:
        options=df.id.tolist()
        chosen=st.selectbox("Bet",options,format_func=lambda x: f"#{x} — {df[df.id==x].iloc[0].event} — {df[df.id==x].iloc[0].selection}")
        r=df[df.id==chosen].iloc[0]
        st.write(f"**{r.sport} · {r.bet_type} · {r.selection} · {r.line} @ {r.odds}**")
        c1,c2,c3=st.columns(3)
        result=c1.selectbox("Result",["Pending","Won","Lost","Push"],index=["Pending","Won","Lost","Push"].index(r.result))
        pnl=c2.number_input("P&L",value=float(r.pnl or 0),step=1.0)
        closing=c3.number_input("Closing odds",min_value=1.01,value=float(r.closing_odds or r.odds),step=0.01)
        post=st.text_area("What actually happened?",value=r.post_game_reason or "",placeholder="Game/race result, role, minutes, race shape, interference, weather, injuries, etc.")
        review_button_label = "Save result + generate AI review" if ai_commentary_enabled else "Save result (AI commentary off)"
        if st.button(review_button_label,use_container_width=True):
            cv=clv(r.odds,closing)
            execsql("UPDATE bets SET result=?,pnl=?,closing_odds=?,clv=?,post_game_reason=? WHERE id=?",(result,pnl,closing,cv,post,int(chosen)))
            provider,key=ai_provider()
            post_ctx=latest_context(r.sport, f"{r.event} {r.selection}", 8)
            prompt=f"""You are an expert betting process analyst, not a tipster. Review this {r.sport} bet using ONLY supplied information and clearly label unknowns.
BET: {r.sport} | {r.bet_type} | {r.market} | {r.selection} | line {r.line} | odds {r.odds} | closing {closing} | stake {r.stake}
ORIGINAL REASONING: {r.reasoning}
SPORT FACTORS: {r.factors_json}
RESULT: {result} | P&L {pnl}
POST-EVENT NOTES: {post}
CONNECTED POST-EVENT DATA: {json.dumps(post_ctx, default=str) if post_ctx else 'none available'}
CLV: {cv}

Return:
1) Outcome explanation
2) Process grade A-F
3) Skill vs variance assessment
4) CLV/price assessment
5) What part of the original thesis was correct/incorrect
6) One repeatable strength
7) One change
8) 2-5 tags from: good_process, bad_process, good_price, bad_price, variance, matchup, role, injury, pace, game_script, weather, track, barrier_box, race_pace, sectionals, class, interference, market_move, unknown
Do not invent stats or claim to have accessed live data."""
            if not ai_commentary_enabled:
                st.success("Result saved. AI commentary is off, so no OpenAI API call was made and no API credits were used.")
            elif key:
                try:
                    used_provider,review=run_ai_commentary(prompt)
                    grade=""
                    for g in ["A+","A","A-","B+","B","B-","C+","C","C-","D","F"]:
                        if f"Process grade {g}" in review or f"**{g}**" in review: grade=g; break
                    execsql("UPDATE bets SET ai_review=?,process_grade=? WHERE id=?",(review,grade,int(chosen)))
                    execsql("INSERT INTO reviews(bet_id,created_at,review,grade,tags) VALUES(?,?,?,?,?)",(int(chosen),datetime.now().isoformat(),review,grade,""))
                    st.success("AI review saved.")
                    st.write(review)
                except Exception as ex:
                    msg=str(ex).lower()
                    if "insufficient_quota" in msg or "credit_balance_exhausted" in msg or "no credits" in msg:
                        st.success("Result saved.")
                        st.info("AI review was skipped because the API account has no credits. Leave AI commentary switched off while testing.")
                    elif "invalid_api_key" in msg or "incorrect api key" in msg:
                        st.success("Result saved.")
                        st.info("AI review was skipped because the configured API key was rejected.")
                    else:
                        st.success("Result saved.")
                        st.info("AI review is temporarily unavailable, but your result was saved normally.")
            else:
                st.success("Result saved.")
                st.info("AI commentary is enabled, but no GROQ_API_KEY or OPENAI_API_KEY is configured.")
        if r.ai_review:
            st.markdown("### Previous AI Review")
            st.write(r.ai_review)

# DATABASE
if page=="Bet History":
    st.markdown("<div class='page-kicker'>History & audit trail</div><div class='page-title'>Bet History</div>",unsafe_allow_html=True)
    st.caption("Your complete betting history and recorded analysis.")
    df=q("SELECT * FROM bets ORDER BY event_date DESC,id DESC")
    if not df.empty:
        st.dataframe(df,use_container_width=True,hide_index=True)
        csv=df.to_csv(index=False).encode()
        st.download_button("Download bets CSV",csv,"bets_export.csv","text/csv")
    od=q("SELECT * FROM odds_snapshots ORDER BY captured_at DESC")
    if not od.empty:
        st.subheader("Odds snapshots")
        st.dataframe(od,use_container_width=True,hide_index=True)

# DATA SOURCES
    st.markdown("---")
    st.markdown("### Remove past bets")
    st.caption("Delete an individual bet from EdgeLab. For multis, linked leg records are removed too.")

    delete_df = q("SELECT id,event_date,sport,event,bet_type,selection,odds,stake,result,pnl FROM bets ORDER BY event_date DESC,id DESC")
    if delete_df.empty:
        st.info("There are no bets to remove.")
    else:
        def _bet_label(row):
            event = str(row["event"] or "").strip()
            selection = str(row["selection"] or "").strip()
            parts = [
                f"#{int(row['id'])}",
                str(row["event_date"]),
                str(row["sport"]),
                str(row["bet_type"]),
                selection or event or "Unnamed bet",
                f"@ {float(row['odds']):.2f}" if pd.notna(row["odds"]) else "",
                f"{money(float(row['stake']))}" if pd.notna(row["stake"]) else "",
                str(row["result"]),
            ]
            return " · ".join([x for x in parts if x])

        delete_options = {
            _bet_label(row): int(row["id"])
            for _, row in delete_df.iterrows()
        }
        selected_label = st.selectbox(
            "Choose a bet to remove",
            list(delete_options.keys()),
            key="delete_bet_select"
        )
        selected_id = delete_options[selected_label]
        selected_row = delete_df.loc[delete_df["id"] == selected_id].iloc[0]

        st.warning(
            f"You are about to permanently remove bet #{selected_id}: "
            f"{selected_row['sport']} · {selected_row['selection'] or selected_row['event']} · "
            f"{selected_row['result']}."
        )
        confirm_delete = st.checkbox(
            "I understand this will permanently delete this bet from the current database.",
            key="confirm_delete_bet"
        )

        if st.button(
            "🗑️ Delete selected bet",
            type="primary",
            disabled=not confirm_delete,
            use_container_width=True,
            key="delete_selected_bet"
        ):
            execsql("DELETE FROM multi_legs WHERE bet_id=?", (selected_id,))
            execsql("DELETE FROM reviews WHERE bet_id=?", (selected_id,))
            execsql("DELETE FROM bets WHERE id=?", (selected_id,))
            st.success(f"Bet #{selected_id} was removed.")
            st.rerun()

if page=="Data Hub":
    st.markdown("<div class='page-kicker'>Odds, stats & models</div><div class='page-title'>Data Hub</div>",unsafe_allow_html=True)
    st.write("Pull free structured data into EdgeLab, store snapshots in the database, and make that context available to the pre-bet and post-game AI reviews.")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("### 🏀 NBA — free scoreboard/results")
        nba_day=st.date_input("NBA date",value=date.today(),key="nba_data_day")
        if st.button("Fetch NBA data",use_container_width=True):
            try:
                games=fetch_nba_scoreboard(nba_day)
                for g in games: save_event_snapshot("NBA",g.get("name") or "NBA game","scoreboard",g,"ESPN public scoreboard")
                st.success(f"Saved {len(games)} NBA game snapshots.")
                if games: st.dataframe(pd.DataFrame(games),use_container_width=True,hide_index=True)
            except Exception as ex: st.error(f"NBA fetch failed: {ex}")
        st.caption("Free starting layer: schedule, scores and game status. Player prop logs/advanced stats are the next connector.")
    with c2:
        st.markdown("### 🏉 AFL — free fixtures/results")
        afl_year=st.number_input("AFL season",min_value=2000,max_value=2100,value=date.today().year,step=1)
        if st.button("Fetch AFL data",use_container_width=True):
            try:
                games=fetch_afl_games(afl_year)
                for g in games:
                    event=f"{g.get('hteam','')} v {g.get('ateam','')}"
                    save_event_snapshot("AFL",event,"fixture/result",g,"Squiggle API")
                st.success(f"Saved {len(games)} AFL game snapshots.")
                if games: st.dataframe(pd.DataFrame(games),use_container_width=True,hide_index=True)
            except Exception as ex: st.error(f"AFL fetch failed: {ex}")
        st.caption("Squiggle gives us a free AFL fixture/results foundation. Detailed player props/CBA/TOG need a separate data source.")
    stored=q("SELECT captured_at,sport,event,subject,source FROM event_data ORDER BY captured_at DESC LIMIT 50")
    if not stored.empty:
        st.markdown("### Latest stored data")
        st.dataframe(stored,use_container_width=True,hide_index=True)
    st.markdown("### Sportsbet / odds")
    st.info("The app records Sportsbet as the default bookmaker, but a live Sportsbet feed/API must be supplied or connected. This build does not pretend to have direct Sportsbet access when no authenticated feed is available.")
    st.markdown("### API configuration")
    st.code("""# Optional environment variables
OPENAI_API_KEY=...
ODDS_API_KEY=...        # e.g. an odds provider that includes your required bookmaker
SPORTSBET_API_URL=...   # only if you have an authorized Sportsbet feed
SPORTSBET_API_KEY=...   # only if required by that feed""")
    st.markdown("### Importing external data")
    up=st.file_uploader("Import odds/event CSV",type=["csv"])
    if up:
        imp=pd.read_csv(up)
        st.write(imp.head())
        if st.button("Import rows as odds snapshots"):
            required={"sport","event","market","selection","odds"}
            if required.issubset(set(imp.columns)):
                for _,x in imp.iterrows():
                    execsql("INSERT INTO odds_snapshots(captured_at,sport,event,market,selection,line,bookmaker,odds,source) VALUES(?,?,?,?,?,?,?,?,?)",
                            (datetime.now().isoformat(),x.get("sport",""),x.get("event",""),x.get("market",""),x.get("selection",""),x.get("line",""),x.get("bookmaker","Sportsbet"),float(x.get("odds",0)), "CSV import"))
                st.success(f"Imported {len(imp)} odds rows.")
                st.rerun()
            else: st.error("CSV needs at least: sport,event,market,selection,odds")


if page=="Settings":
    st.markdown("<div class='page-kicker'>Preferences & system status</div><div class='page-title'>Settings</div><div class='page-copy'>Control AI usage and check what data layers are active.</div>",unsafe_allow_html=True)
    c1,c2=st.columns(2,gap="large")
    with c1:
        st.markdown("### AI commentary")
        st.write("Use the sidebar toggle to enable or disable AI commentary. EdgeLab prefers Groq when GROQ_API_KEY is configured and otherwise falls back to OpenAI.")
        st.success("AI commentary is enabled. API calls may use credits when analysis/review is requested.") if ai_commentary_enabled else st.info("AI commentary is off. EdgeLab will not make OpenAI API calls.")
        st.markdown("### Decision engine")
        st.caption("BET / LEAN / NO BET currently uses a transparent rule-based gate based on your probability estimate, market implied probability and evidence quality.")
    with c2:
        st.markdown("### Data status")
        dc=q("SELECT sport,source,MAX(captured_at) AS latest,COUNT(*) AS rows FROM event_data GROUP BY sport,source ORDER BY latest DESC")
        st.dataframe(dc,use_container_width=True,hide_index=True) if not dc.empty else st.info("No structured sports data stored yet.")
        st.markdown("### Database")
        st.caption(f"Local database: {DB}")
        st.warning("Streamlit Community Cloud local SQLite storage may reset on redeploy/restart. Move to a persistent cloud database before relying on this for permanent history.")


