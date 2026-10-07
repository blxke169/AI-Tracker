

import streamlit as st
import pandas as pd
import sqlite3, os, json, math, requests
from datetime import datetime, date
from pathlib import Path

st.set_page_config(page_title="EdgeLab | Betting Intelligence", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

st.markdown(r"""
<style>
:root { --panel:#111827; --panel2:#0b1220; --line:#263244; --muted:#94a3b8; --green:#22c55e; }
[data-testid="stAppViewContainer"] { background: radial-gradient(circle at 15% 0%, #172033 0, #0b0f17 36%, #070a10 100%); color:#f8fafc; }
[data-testid="stHeader"] { background: rgba(7,10,16,.72); }
[data-testid="stSidebar"] { background:#090d14; border-right:1px solid #1e293b; }
.block-container { max-width:1380px; padding-top:2rem; padding-bottom:4rem; }
h1,h2,h3 { letter-spacing:-.025em; }
h1 { font-size:2.25rem !important; }
[data-testid="stMetric"] { background:linear-gradient(145deg,#121a29,#0c121d); border:1px solid #243044; padding:18px 20px; border-radius:16px; box-shadow:0 10px 30px rgba(0,0,0,.18); }
[data-testid="stMetricLabel"] { color:#94a3b8; }
[data-testid="stMetricValue"] { font-weight:800; }
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button { border-radius:12px; min-height:46px; font-weight:700; border:1px solid #334155; }
[data-testid="stFormSubmitButton"] > button { background:linear-gradient(90deg,#16a34a,#22c55e); color:#04120a; border:0; }
[data-testid="stForm"] { background:rgba(15,23,42,.72); border:1px solid #243044; border-radius:18px; padding:1.25rem; }
[data-baseweb="input"] > div, [data-baseweb="select"] > div, textarea { border-radius:10px !important; }
[data-testid="stDataFrame"] { border:1px solid #243044; border-radius:14px; overflow:hidden; }
.stTabs [data-baseweb="tab-list"] { gap:8px; background:#0b111b; border:1px solid #1e293b; border-radius:14px; padding:6px; }
.stTabs [data-baseweb="tab"] { border-radius:10px; padding:8px 18px; }
.stTabs [aria-selected="true"] { background:#172033; }
.hero { padding:22px 24px; border:1px solid #263244; border-radius:20px; background:linear-gradient(120deg,rgba(34,197,94,.12),rgba(15,23,42,.82) 48%,rgba(59,130,246,.08)); margin-bottom:18px; }
.hero-kicker { color:#22c55e; font-size:.78rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
.hero-title { font-size:2.15rem; font-weight:850; letter-spacing:-.04em; margin:.2rem 0; }
.hero-copy { color:#a8b3c5; margin:0; }
.section-card { background:rgba(15,23,42,.62); border:1px solid #243044; border-radius:16px; padding:16px 18px; margin:10px 0 18px; }
.pill { display:inline-block; padding:5px 10px; border-radius:999px; background:rgba(34,197,94,.12); color:#86efac; border:1px solid rgba(34,197,94,.25); font-size:.78rem; font-weight:700; margin-right:6px; }
.small-muted { color:#94a3b8; font-size:.9rem; }
hr { border-color:#1e293b !important; }
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
    "Greyhounds":["Win","Place","Top 2","Top 3","Exacta","Quinella","Trifecta","Other"]
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

st.markdown("""
<div class="hero">
  <div class="hero-kicker">EDGE • PROCESS • PERFORMANCE</div>
  <div class="hero-title">EdgeLab Betting Intelligence</div>
  <p class="hero-copy">Track every wager, measure your closing-line value, and review the quality of your betting process.</p>
</div>
""", unsafe_allow_html=True)

tabs=st.tabs(["📊 Dashboard","💰 Bankroll","＋ Log Bet","🧠 Pre-Bet Analyst","✨ AI Review","🗂 Database","🔌 Data Sources"])

# DASHBOARD
with tabs[0]:
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
with tabs[1]:
    st.markdown("## 💰 Bankroll Manager")
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
with tabs[2]:
    st.markdown("## Log a bet")
    st.caption("Log a single or a multi. Multi legs are stored individually so you can later see which markets are helping or hurting your parlays.")
    wager_type=st.radio("Wager type",["Single","Multi / Parlay"],horizontal=True)
    if wager_type=="Single":
        with st.form("log_single"):
            c1,c2,c3=st.columns(3)
            event_date=c1.date_input("Event date",date.today(),key="sdate")
            sport=c2.selectbox("Sport",SPORTS,key="ssport")
            league=c3.text_input("League",value="",key="sleague")
            event=st.text_input("Event / Race",key="sevent")
            book=st.text_input("Sportsbook",value="Sportsbet",key="sbook")
            bt=c1.selectbox("Bet type",BET_TYPES[sport],key="sbt")
            market=c2.text_input("Market",placeholder="Over/Under, handicap, win, place...",key="smarket")
            selection=c3.text_input("Selection / Player / Runner",key="ssel")
            line=c1.text_input("Line",key="sline")
            odds=c2.number_input("Odds taken (decimal)",min_value=1.01,value=1.91,step=0.01,key="sodds")
            close=c3.number_input("Closing odds (if known)",min_value=1.01,value=1.91,step=0.01,key="sclose")
            stake=c1.number_input("Stake",min_value=0.0,value=20.0,step=5.0,key="sstake")
            reasoning=st.text_area("Your reasoning",placeholder="What was your thesis? Why did you think the price was wrong?",key="sreason")
            st.markdown("### Analysis context")
            raw=st.text_area(f"Key factors ({FACTOR_HINTS[sport]})",placeholder="Optional. Paste relevant stats, lineup/race notes, weather, sectionals, etc.",key="sfactors")
            source_note=st.text_input("Data source / note",value="Manual entry",key="ssource")
            submit=st.form_submit_button("Save Single",use_container_width=True)
            if submit:
                cv=clv(odds,close)
                execsql("""INSERT INTO bets(placed_at,event_date,sport,league,event,book,bet_type,market,selection,line,odds,closing_odds,stake,result,pnl,reasoning,post_game_reason,clv,ai_review,process_grade,factors_json,source_note)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (datetime.now().isoformat(),str(event_date),sport,league,event,book,bt,market,selection,line,odds,close,stake,"Pending",0,reasoning,"",cv,"","",json.dumps({"raw_factors":raw,"wager_type":"single"}),source_note))
                st.success("Single saved."); st.rerun()
    else:
        st.info("Choose the number of legs, then fill each leg. Combined odds and potential return update automatically after you submit.")
        nlegs=st.number_input("Number of legs",min_value=2,max_value=12,value=3,step=1)
        with st.form("log_multi"):
            c1,c2,c3=st.columns(3)
            event_date=c1.date_input("Bet date / main event date",date.today(),key="mdate")
            book=c2.text_input("Sportsbook",value="Sportsbet",key="mbook")
            stake=c3.number_input("Stake",min_value=0.0,value=20.0,step=5.0,key="mstake")
            multi_name=st.text_input("Multi name",placeholder="e.g. Wednesday NBA 4-leg")
            reasoning=st.text_area("Overall multi reasoning",placeholder="Why do these legs belong in the multi? Note any correlations or risks.")
            legs=[]
            for i in range(int(nlegs)):
                st.markdown(f"#### Leg {i+1}")
                a,b,c,d=st.columns(4)
                lsport=a.selectbox("Sport",SPORTS,key=f"lsport{i}")
                lbet_type=b.selectbox("Bet type",BET_TYPES[lsport],key=f"lbt{i}")
                levent=c.text_input("Event",key=f"levent{i}")
                lodds=d.number_input("Odds",min_value=1.01,value=1.50,step=0.01,key=f"lodds{i}")
                e,f,g,h=st.columns(4)
                lmarket=e.text_input("Market",placeholder="Over/Under, handicap, win, place...",key=f"lmarket{i}")
                lselection=f.text_input("Selection",key=f"lsel{i}")
                lline=g.text_input("Line",key=f"lline{i}")
                lnotes=h.text_input("Notes",key=f"lnotes{i}")
                legs.append((lsport,lbet_type,levent,lmarket,lselection,lline,lodds,lnotes))
            source_note=st.text_input("Data source / note",value="Manual entry",key="msource")
            submit=st.form_submit_button("Save Multi",use_container_width=True)
            if submit:
                combined=math.prod([x[6] for x in legs])
                label=multi_name.strip() or f"{len(legs)}-Leg Multi"
                bet_id=execsql("""INSERT INTO bets(placed_at,event_date,sport,league,event,book,bet_type,market,selection,line,odds,closing_odds,stake,result,pnl,reasoning,post_game_reason,clv,ai_review,process_grade,factors_json,source_note)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (datetime.now().isoformat(),str(event_date),"Multi","",label,book,"Multi / Parlay","Multi",label,f"{len(legs)} legs",combined,combined,stake,"Pending",0,reasoning,"",None,"","",json.dumps({"wager_type":"multi","legs":len(legs)}),source_note))
                for i,leg in enumerate(legs,1):
                    execsql("INSERT INTO multi_legs(bet_id,leg_no,sport,bet_type,event,market,selection,line,odds,closing_odds,result,clv,notes) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
                            (bet_id,i,leg[0],leg[1],leg[2],leg[3],leg[4],leg[5],leg[6],leg[6],"Pending",None,leg[7]))
                st.success(f"Multi saved — combined odds {combined:.2f} · potential return {money(stake*combined)} · potential profit {money(stake*(combined-1))}"); st.rerun()

# PRE-BET ANALYST
with tabs[3]:
    st.markdown("## 🧠 Pre-Bet Analyst")
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
        st.markdown(f"### Decision: **{gate}**")
        st.write(reason)
        x1,x2,x3=st.columns(3)
        x1.metric("Market implied probability",f"{implied:.1f}%")
        x2.metric("Your probability",f"{aprob:.1f}%" if aprob else "Not supplied")
        x3.metric("Estimated edge",f"{edge:.1f} pp" if edge is not None else "Unknown")
        data_ctx=latest_context(asport, aselection or amarket, 8)
        if data_ctx:
            st.markdown("### Connected data context")
            st.caption("Recent structured snapshots stored by EdgeLab. The AI may use these, but must still label missing player/market data as unknown.")
            st.dataframe(pd.DataFrame(data_ctx)[["captured_at","event","subject","source"]],use_container_width=True,hide_index=True)
        key=os.getenv("OPENAI_API_KEY","")
        try:
            if not key and "OPENAI_API_KEY" in st.secrets: key=st.secrets["OPENAI_API_KEY"]
        except: pass
        if key:
            try:
                from openai import OpenAI
                prompt=f"""Act as a conservative betting process analyst. Do not invent facts, statistics, injuries, odds movement, or live data.\nSPORT: {asport}\nSELECTION: {aselection}\nMARKET: {amarket}\nODDS: {aodds}\nUSER PROBABILITY: {aprob if aprob else 'not supplied'}\nEVIDENCE QUALITY: {confidence}\nSUPPLIED EVIDENCE: {evidence}\nSAFETY GATE: {gate} — {reason}\n\nExplain the decision in five short sections: Verdict, Price/Edge, Evidence For, Risks/Missing Data, What would change the decision. Never upgrade a NO BET safety gate to BET. If evidence is inadequate, explicitly say NO BET."""
                resp=OpenAI(api_key=key).responses.create(model="gpt-5-mini",input=prompt)
                st.markdown("### AI assessment")
                st.write(resp.output_text)
            except Exception as ex: st.warning(f"The rule-based decision worked, but AI commentary failed: {ex}")
        else:
            st.caption("Add OPENAI_API_KEY in Streamlit Secrets for the written AI assessment. The BET/LEAN/NO BET safety gate works without it.")

# POST GAME
with tabs[4]:
    st.markdown("## AI bet review")
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
        if st.button("Save result + generate AI review",use_container_width=True):
            cv=clv(r.odds,closing)
            execsql("UPDATE bets SET result=?,pnl=?,closing_odds=?,clv=?,post_game_reason=? WHERE id=?",(result,pnl,closing,cv,post,int(chosen)))
            key=os.getenv("OPENAI_API_KEY","")
            try:
                if not key and "OPENAI_API_KEY" in st.secrets: key=st.secrets["OPENAI_API_KEY"]
            except: pass
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
            if key:
                try:
                    from openai import OpenAI
                    client=OpenAI(api_key=key)
                    resp=client.responses.create(model="gpt-5-mini",input=prompt)
                    review=resp.output_text
                    grade=""
                    for g in ["A+","A","A-","B+","B","B-","C+","C","C-","D","F"]:
                        if f"Process grade {g}" in review or f"**{g}**" in review: grade=g; break
                    execsql("UPDATE bets SET ai_review=?,process_grade=? WHERE id=?",(review,grade,int(chosen)))
                    execsql("INSERT INTO reviews(bet_id,created_at,review,grade,tags) VALUES(?,?,?,?,?)",(int(chosen),datetime.now().isoformat(),review,grade,""))
                    st.success("AI review saved.")
                    st.write(review)
                except Exception as ex: st.error(f"AI error: {ex}")
            else:
                st.warning("Set OPENAI_API_KEY to enable automatic AI reviews.")
        if r.ai_review:
            st.markdown("### Previous AI Review")
            st.write(r.ai_review)

# DATABASE
with tabs[5]:
    st.markdown("## Bet database")
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
with tabs[6]:
    st.markdown("## Data Hub")
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

st.sidebar.divider()
st.sidebar.markdown("### 📈 EdgeLab")
st.sidebar.caption("Betting Intelligence v4.1 · Free Data Hub")
st.sidebar.markdown("<span class='pill'>TRACK</span><span class='pill'>REVIEW</span>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.caption("Educational analytics only. Betting involves financial risk.")
