
import streamlit as st
import pandas as pd
import sqlite3, os, json, math
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
    c.commit()
    return c

def clv(bet, close):
    try:
        b=float(bet); c=float(close)
        # Compare implied probabilities; positive means you obtained the lower implied probability price.
        def p(o): return 100/(o+100) if o>0 else (-o)/(-o+100)
        return (p(c)-p(b))*100
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

conn().close()

st.markdown("""
<div class="hero">
  <div class="hero-kicker">EDGE • PROCESS • PERFORMANCE</div>
  <div class="hero-title">EdgeLab Betting Intelligence</div>
  <p class="hero-copy">Track every wager, measure your closing-line value, and review the quality of your betting process.</p>
</div>
""", unsafe_allow_html=True)

tabs=st.tabs(["📊 Dashboard","＋ Log Bet","✨ AI Review","🗂 Database","🔌 Data Sources"])

# DASHBOARD
with tabs[0]:
    df=q("SELECT * FROM bets")
    if df.empty:
        st.info("Your dashboard is empty. Log your first bet to start building your performance history.")
    else:
        sport_filter=st.selectbox("Sport",["All"]+SPORTS,key="dashsport")
        d=df if sport_filter=="All" else df[df.sport==sport_filter]
        settled=d[d.result.isin(["Won","Lost","Push"])].copy()
        stake=settled.stake.sum() if not settled.empty else 0
        pnl=settled.pnl.sum() if not settled.empty else 0
        roi=pnl/stake*100 if stake else 0
        avgclv=settled.clv.mean() if not settled.empty else 0
        a,b,c,e=st.columns(4)
        a.metric("ROI",pct(roi)); b.metric("P&L",money(pnl)); c.metric("Avg CLV",pct(avgclv)); e.metric("Bets",len(d))
        if not settled.empty:
            st.markdown("### Performance by bet type")
            g=settled.groupby("bet_type").agg(Bets=("id","count"),Stake=("stake","sum"),PnL=("pnl","sum"),CLV=("clv","mean")).reset_index()
            g["ROI"]=g.apply(lambda r:r.PnL/r.Stake*100 if r.Stake else 0,axis=1)
            g["P&L"]=g.PnL.map(money); g["ROI"]=g.ROI.map(pct); g["CLV"]=g.CLV.map(pct)
            st.dataframe(g[["bet_type","Bets","Stake","P&L","ROI","CLV"]],use_container_width=True,hide_index=True)
            st.markdown("### Process grades")
            grades=settled[settled.process_grade.astype(str)!=""].groupby("process_grade").size().reset_index(name="Bets")
            if not grades.empty: st.dataframe(grades,use_container_width=True,hide_index=True)
            st.markdown("### Recent bets")
            cols=["id","event_date","sport","event","bet_type","selection","line","odds","closing_odds","result","pnl","clv","process_grade"]
            show=settled.sort_values("event_date",ascending=False)[cols].copy()
            show["pnl"]=show.pnl.map(money); show["clv"]=show.clv.map(pct)
            st.dataframe(show,use_container_width=True,hide_index=True)

# LOG BET
with tabs[1]:
    st.markdown("## Log a bet")
    st.caption("Capture the price and thesis at the time you place the wager. Optional context can be added now or later.")
    with st.form("log"):
        c1,c2,c3=st.columns(3)
        event_date=c1.date_input("Event date",date.today())
        sport=c2.selectbox("Sport",SPORTS)
        league=c3.text_input("League",value="")
        event=st.text_input("Event / Race")
        book=st.text_input("Sportsbook",value="Sportsbet")
        bt=c1.selectbox("Bet type",BET_TYPES[sport])
        market=c2.text_input("Market",placeholder="Over/Under, handicap, win, place...")
        selection=c3.text_input("Selection / Player / Runner")
        line=c1.text_input("Line")
        odds=c2.number_input("Odds taken (decimal)",min_value=1.01,value=1.91,step=0.01)
        close=c3.number_input("Closing odds (if known)",min_value=1.01,value=1.91,step=0.01)
        stake=c1.number_input("Stake",min_value=0.0,value=20.0,step=5.0)
        reasoning=st.text_area("Your reasoning",placeholder="What was your thesis? Why did you think the price was wrong?")
        factors={}
        st.markdown("### Analysis context")
        st.caption("Optional — leave this blank if you do not have the extra data yet.")
        raw=st.text_area(f"Key factors ({FACTOR_HINTS[sport]})",placeholder="Paste any relevant stats, race data, lineup notes, weather, sectionals, etc.")
        source_note=st.text_input("Data source / note",value="Manual entry")
        submit=st.form_submit_button("Save Bet",use_container_width=True)
        if submit:
            cv=clv(odds,close)
            execsql("""INSERT INTO bets(placed_at,event_date,sport,league,event,book,bet_type,market,selection,line,odds,closing_odds,stake,result,pnl,reasoning,post_game_reason,clv,ai_review,process_grade,factors_json,source_note)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (datetime.now().isoformat(),str(event_date),sport,league,event,book,bt,market,selection,line,odds,close,stake,"Pending",0,reasoning,"",cv,"","",json.dumps({"raw_factors":raw}),source_note))
            st.success("Bet saved to the SQLite database.")
            st.rerun()

# POST GAME
with tabs[2]:
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
            prompt=f"""You are an expert betting process analyst, not a tipster. Review this {r.sport} bet using ONLY supplied information and clearly label unknowns.
BET: {r.sport} | {r.bet_type} | {r.market} | {r.selection} | line {r.line} | odds {r.odds} | closing {closing} | stake {r.stake}
ORIGINAL REASONING: {r.reasoning}
SPORT FACTORS: {r.factors_json}
RESULT: {result} | P&L {pnl}
POST-EVENT NOTES: {post}
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
with tabs[3]:
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
with tabs[4]:
    st.markdown("## Data sources & connectors")
    st.write("The app is designed around a source layer so odds/stat feeds can be connected without changing the tracker database.")
    st.markdown("### Sportsbet")
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
st.sidebar.caption("Betting Intelligence v3.1")
st.sidebar.markdown("<span class='pill'>TRACK</span><span class='pill'>REVIEW</span>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.caption("Educational analytics only. Betting involves financial risk.")

   
