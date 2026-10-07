
import streamlit as st
import pandas as pd
import sqlite3, os, json, math
from datetime import datetime, date
from pathlib import Path

st.set_page_config(page_title="AI Betting Intelligence", page_icon="🤖", layout="wide")

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

st.title("🤖 AI Betting Intelligence")
st.caption("Database + tracker + CLV + sport-specific analysis + AI post-game/race review")

tabs=st.tabs(["Dashboard","Log Bet","Post-Game AI","Database","Data Sources"])

# DASHBOARD
with tabs[0]:
    df=q("SELECT * FROM bets")
    if df.empty:
        st.info("No bets yet. Use Log Bet to start.")
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
            st.subheader("Performance by Bet Type")
            g=settled.groupby("bet_type").agg(Bets=("id","count"),Stake=("stake","sum"),PnL=("pnl","sum"),CLV=("clv","mean")).reset_index()
            g["ROI"]=g.apply(lambda r:r.PnL/r.Stake*100 if r.Stake else 0,axis=1)
            g["P&L"]=g.PnL.map(money); g["ROI"]=g.ROI.map(pct); g["CLV"]=g.CLV.map(pct)
            st.dataframe(g[["bet_type","Bets","Stake","P&L","ROI","CLV"]],use_container_width=True,hide_index=True)
            st.subheader("AI Process Tags / Grades")
            grades=settled[settled.process_grade.astype(str)!=""].groupby("process_grade").size().reset_index(name="Bets")
            if not grades.empty: st.dataframe(grades,use_container_width=True,hide_index=True)
            st.subheader("Recent Bets")
            cols=["id","event_date","sport","event","bet_type","selection","line","odds","closing_odds","result","pnl","clv","process_grade"]
            show=settled.sort_values("event_date",ascending=False)[cols].copy()
            show["pnl"]=show.pnl.map(money); show["clv"]=show.clv.map(pct)
            st.dataframe(show,use_container_width=True,hide_index=True)

# LOG BET
with tabs[1]:
    st.subheader("Log a Bet")
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
        st.markdown("**Sport-specific information for the AI**")
        st.caption("You can leave these blank if the data source will populate them later.")
        raw=st.text_area(f"Key factors ({FACTOR_HINTS[sport]})",placeholder="Paste any relevant stats, race data, lineup notes, weather, sectionals, etc.")
        source_note=st.text_input("Data source / note",value="Manual entry")
        submit=st.form_submit_button("Save Bet",use_container_width=True)
        if submit:
            cv=clv(odds,close)
            execsql("""INSERT INTO bets(placed_at,event_date,sport,league,event,book,bet_type,market,selection,line,odds,closing_odds,stake,result,pnl,reasoning,post_game_reason,clv,ai_review,process_grade,factors_json,source_note)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (datetime.now().isoformat(),str(event_date),sport,league,event,book,bt,market,selection,line,odds,close,stake,"Pending",0,reasoning,"",cv,"","","",json.dumps({"raw_factors":raw}),source_note))
            st.success("Bet saved to the SQLite database.")
            st.rerun()

# POST GAME
with tabs[2]:
    st.subheader("AI Post-Game / Post-Race Review")
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
    st.subheader("Database")
    st.caption("SQLite database: betting.db")
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
    st.subheader("Data Sources & Connectors")
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
st.sidebar.caption("AI Betting Intelligence v3")
st.sidebar.caption("Educational analytics only. Betting involves financial risk.")
