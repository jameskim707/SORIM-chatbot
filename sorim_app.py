import streamlit as st
import requests
import re
import json
import zipfile
import io
from datetime import datetime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.set_page_config(
    page_title="SORIM Studio | AI BGM Production System",
    page_icon="🎼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS — CLEAN WHITE PROFESSIONAL THEME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #f8f9fb; }

/* 헤더 */
.sorim-header {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #1e293b;
    border-radius: 8px;
    padding: 20px 28px;
    margin-bottom: 20px;
    box-shadow: 0 1px 8px rgba(0,0,0,0.06);
}
.sorim-title {
    font-size: 1.8em;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.5px;
    margin: 0;
}
.sorim-badge {
    display: inline-block;
    background: #0f172a;
    color: #ffffff;
    font-size: 0.65em;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    margin-left: 10px;
    letter-spacing: 1px;
    vertical-align: middle;
}
.sorim-subtitle {
    color: #64748b;
    font-size: 0.85em;
    margin-top: 4px;
    font-weight: 400;
}

/* 워크플로우 스텝 */
.workflow-bar {
    display: flex;
    align-items: center;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px 20px;
    margin-bottom: 20px;
    gap: 8px;
    overflow-x: auto;
}
.wf-step {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.78em;
    font-weight: 500;
    color: #94a3b8;
    white-space: nowrap;
}
.wf-step.active { color: #0f172a; font-weight: 600; }
.wf-step.done { color: #22c55e; }
.wf-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #e2e8f0;
}
.wf-dot.active { background: #0f172a; }
.wf-dot.done { background: #22c55e; }
.wf-arrow { color: #cbd5e1; font-size: 0.7em; }

/* 메트릭 카드 */
.metric-row {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
}
.metric-card {
    flex: 1;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 14px 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.metric-val {
    font-size: 1.8em;
    font-weight: 700;
    color: #0f172a;
    line-height: 1;
}
.metric-lbl {
    font-size: 0.72em;
    color: #94a3b8;
    margin-top: 4px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* 프로덕션 모드 버튼 */
.mode-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    margin-bottom: 16px;
}
.mode-btn {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 8px;
    padding: 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.15s;
    font-size: 0.82em;
    font-weight: 500;
    color: #374151;
}
.mode-btn:hover, .mode-btn.selected {
    border-color: #0f172a;
    background: #f8fafc;
    color: #0f172a;
}

/* 결과 블록 */
.result-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 18px;
    margin: 10px 0;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}
.result-label {
    font-size: 0.72em;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #94a3b8;
    margin-bottom: 10px;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
}

/* expander */
.streamlit-expanderHeader {
    background: #f8f9fb !important;
    border-radius: 6px !important;
    border: 1px solid #e2e8f0 !important;
    font-weight: 500 !important;
    font-size: 0.88em !important;
}

/* 채팅 */
.stChatMessage { border-radius: 8px !important; margin: 6px 0 !important; }

hr { border-color: #e2e8f0 !important; }

.stSuccess {
    background: #f0fdf4 !important;
    border: 1px solid #bbf7d0 !important;
    border-radius: 6px !important;
    font-size: 0.85em !important;
}

/* 선택 옵션 박스 */
.option-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECURITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_api_key():
    try:
        key = st.secrets["GROQ_API_KEY"]
        return key if key and len(key) > 10 else None
    except Exception:
        return None

API_KEY = get_api_key()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def init_session():
    defaults = {
        "messages": [],
        "projects": [],
        "current_project": None,
        "total_generated": 0,
        "last_gen_time": None,
        "workflow_step": 0,
        "production_mode": None,
        "selected_genre": None,
        "selected_mood": None,
        "selected_use": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SYSTEM PROMPT — BGM PRODUCTION SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEM_PROMPT = """
You are SORIM Studio — a professional AI-Directed BGM Production System.
This is NOT a casual chatbot. Operate as a structured music production director.

CRITICAL RULES:
1. Respond in Korean ONLY (except STEP 4 music prompts which must be English only).
2. Produce COMPLETE, DETAILED, production-grade outputs.
3. STEP 4 music generation prompts: English ONLY, professional music director brief format.
4. Use these EXACT markers for parsing:
   ###LYRICS_START### ... ###LYRICS_END###
   ###PROMPT_START### ... ###PROMPT_END###
   ###STRATEGY_START### ... ###STRATEGY_END###
   ###SUMMARY_START### ... ###SUMMARY_END###
5. Minimize unnecessary questions. Use structured intake then produce immediately.
6. Tone: Professional, directive, minimal. No excessive emoji. No hollow phrases.

PRODUCTION WORKFLOW:

[PHASE 1 — CONCEPT DEFINITION]
If user provides production mode, genre, mood, and use case → skip questions, produce immediately.
Otherwise ask max 2 structured questions using numbered options.

[PHASE 2 — TRACK DESIGN]
Define:
- Track concept (one clear sentence)
- Target platform and audience
- Emotional arc (3 stages: open → build → release)
- Tempo character (slow/mid/uptempo)
- Instrumentation palette (3-5 core instruments)

[PHASE 3 — LYRIC BRIEF] (if vocal track requested)
Output between ###LYRICS_START### and ###LYRICS_END###
First, suggest 3 track title candidates (Korean) with brief reasoning for each.
Then write:
Variation A (Direct): [Verse 1][Pre-Chorus][Chorus][Verse 2][Bridge] — clear, universal
Variation B (Cinematic): Same structure — poetic, layered, visual
Hook Line: 1-2 lines optimized for 15s hook

[PHASE 4 — MUSIC PRODUCTION BRIEF] ★ ENGLISH ONLY ★
Output between ###PROMPT_START### and ###PROMPT_END###

--- SHORTS VERSION (30s) ---
[SORIM BGM BRIEF — SHORTS]
Genre: / Mood: / BPM: (range) / Key: / Time Sig:
Hook target: by 12-15 seconds
Instrumentation timeline:
  0:00-0:05 | [texture + reverb type]
  0:05-0:13 | [layering entries]
  0:13-0:25 | [peak arrangement]
  0:25-0:30 | [resolution]
Dynamic arc: Intro(30%) > Build(55%) > Peak(85%) > Out(40%)
Vocal: type / tone / register / harmony / mic proximity / breath notes
Mix: reverb style / stereo / compression / EQ guidance
Safety: Do not imitate any specific artist or copyrighted work.

--- FULL TRACK (2-4 min) ---
[SORIM BGM BRIEF — FULL TRACK]
Genre: / Mood: / BPM: (range) / Key + modulation: / Time Sig: / Duration:
Structure table:
| Time | Section | Instruments | Intensity |
|------|---------|-------------|-----------|
| 0:00 | Intro   | ...         | 25%       |
| ...  | ...     | ...         | ...       |
Instrument details: (felt piano / fingerstyle guitar / cello / pad / percussion)
Dynamic arc: Intro(25%)>V1(40%)>Pre(60%)>Ch1(85%)>V2(45%)>Pre(65%)>Ch2(90%)>Bridge(35%)>FinalCh(95%)>Outro(15%)
Key modulation: [specify or None]
Vocal direction: type / tone / register progression / harmony entry / breath notes
Production: reverb (hall/plate/room per instrument) / stereo width / mix guidance / master target (-14 LUFS)
Safety: Do not imitate any specific artist or copyrighted work.

[PHASE 5 — MARKET STRATEGY]
Output between ###STRATEGY_START### and ###STRATEGY_END###
Platform fit analysis (YouTube BGM / Shorts / Streaming / Stock / Game BGM)
Metadata: Title (KR + EN) / Tags / Description / Avoid list
Packaging: track versions + pricing tier

[PHASE 6 — PRODUCTION SUMMARY]
Output between ###SUMMARY_START### and ###SUMMARY_END###
Concise table: Concept / Genre / BPM / Key / Vocal / Platform / Next action

PRODUCTION MODES:
- Single Track: one complete BGM package
- Album Pack: 3-track thematic set (intro/main/outro)
- Shorts Pack: 3x30s hook-forward variants
- Target Market: optimized for specific platform (YouTube/Spotify/Stock)

FAST MODE: if user says "빠르게" → skip to PHASE 4 Shorts only.
REFUSAL: copyright/imitation requests → "해당 요청은 저작권 정책상 처리할 수 없습니다. 유사한 방향으로 새롭게 제작해드릴 수 있습니다."
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXTRACTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_section(text, start, end):
    match = re.search(f"{start}(.*?){end}", text, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_all(text):
    return {
        "lyrics": extract_section(text, "###LYRICS_START###", "###LYRICS_END###"),
        "prompt": extract_section(text, "###PROMPT_START###", "###PROMPT_END###"),
        "strategy": extract_section(text, "###STRATEGY_START###", "###STRATEGY_END###"),
        "summary": extract_section(text, "###SUMMARY_START###", "###SUMMARY_END###"),
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ZIP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def create_zip(project):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if project.get("lyrics"): zf.writestr("lyrics.txt", project["lyrics"])
        if project.get("prompt"): zf.writestr("music_brief.txt", project["prompt"])
        if project.get("strategy"): zf.writestr("market_strategy.txt", project["strategy"])
        if project.get("summary"): zf.writestr("summary.txt", project["summary"])
        meta = {k: v for k, v in project.items()}
        zf.writestr("project.json", json.dumps(meta, ensure_ascii=False, indent=2))
    buf.seek(0)
    return buf

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GROQ API
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def call_groq(messages):
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": 0.72, "max_tokens": 4096}
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("**SORIM Studio**")
    st.caption("AI BGM Production System")
    st.markdown("---")

    # 메트릭
    c1, c2 = st.columns(2)
    with c1:
        st.metric("생성된 트랙", st.session_state.total_generated)
    with c2:
        t = st.session_state.last_gen_time
        st.metric("마지막 생성", t.strftime("%H:%M") if t else "—")

    st.markdown("---")

    # 프로덕션 모드 선택
    st.markdown("**프로덕션 모드**")
    modes = ["Single Track", "Album Pack", "Shorts Pack", "Target Market"]
    selected_mode = st.radio("", modes, label_visibility="collapsed",
                             index=modes.index(st.session_state.production_mode)
                             if st.session_state.production_mode in modes else 0)
    st.session_state.production_mode = selected_mode

    st.markdown("---")

    # 빠른 설정
    st.markdown("**빠른 설정**")
    genre = st.selectbox("장르", [
        "선택 안함", "시네마틱 발라드", "어쿠스틱 팝", "Lo-fi",
        "국악 퓨전", "재즈", "R&B", "힙합", "EDM", "인디 팝", "클래식 크로스오버"
    ])
    mood = st.selectbox("무드", [
        "선택 안함", "그리움/향수", "해방감", "설렘", "위로",
        "활력", "차분함", "긴장감", "감동", "중립 BGM"
    ])
    use_case = st.selectbox("용도", [
        "선택 안함", "유튜브 BGM", "숏츠/릴스", "스트리밍",
        "스톡 뮤직", "인디 게임 BGM", "광고/브랜드", "명상/힐링"
    ])
    st.session_state.selected_genre = genre
    st.session_state.selected_mood = mood
    st.session_state.selected_use = use_case

    st.markdown("---")

    # 프로젝트 히스토리
    st.markdown("**프로젝트 히스토리**")
    if st.session_state.projects:
        labels = [f"{p['timestamp']} | {p.get('concept','')[:12]}..."
                  for p in reversed(st.session_state.projects)]
        sel = st.selectbox("", labels, label_visibility="collapsed")
        idx = len(st.session_state.projects) - 1 - labels.index(sel)
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("불러오기", use_container_width=True):
                st.session_state.current_project = st.session_state.projects[idx]
                st.rerun()
        with col_b:
            if st.button("전체삭제", use_container_width=True):
                st.session_state.projects = []
                st.rerun()
    else:
        st.caption("생성된 프로젝트 없음")

    st.markdown("---")

    # 내보내기
    st.markdown("**내보내기**")
    cp = st.session_state.current_project
    if cp:
        today = datetime.now().strftime("%Y%m%d_%H%M")
        if cp.get("lyrics"):
            st.download_button("가사 TXT", cp["lyrics"],
                               file_name=f"SORIM_lyrics_{today}.txt", use_container_width=True)
        if cp.get("prompt"):
            st.download_button("프롬프트 TXT", cp["prompt"],
                               file_name=f"SORIM_brief_{today}.txt", use_container_width=True)
        zb = create_zip(cp)
        st.download_button("전체 ZIP", zb,
                           file_name=f"SORIM_project_{today}.zip",
                           mime="application/zip", use_container_width=True)
    else:
        st.caption("프로젝트 생성 후 활성화됩니다")

    st.markdown("---")
    if st.button("새 프로젝트", use_container_width=True):
        for k in ["messages", "current_project", "workflow_step"]:
            st.session_state[k] = [] if k == "messages" else (None if k == "current_project" else 0)
        st.rerun()
    st.caption("v4.1 · Groq · LLaMA 3.3")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메인 — 헤더
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class='sorim-header'>
    <div class='sorim-title'>SORIM Studio
        <span class='sorim-badge'>BGM PRODUCTION</span>
    </div>
    <div class='sorim-subtitle'>AI-Directed BGM Production System · 콘셉트에서 완성 브리프까지</div>
</div>
""", unsafe_allow_html=True)

if not API_KEY:
    st.error("서비스 설정 오류입니다. 관리자에게 문의하세요.")
    st.stop()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 워크플로우 진행 바
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
steps = ["Concept", "Track Design", "Brief", "Hook", "Export"]
step = st.session_state.workflow_step

wf_html = "<div class='workflow-bar'>"
for i, s in enumerate(steps):
    cls = "done" if i < step else ("active" if i == step else "")
    dot_cls = cls
    wf_html += f"<div class='wf-step {cls}'><div class='wf-dot {dot_cls}'></div>{s}</div>"
    if i < len(steps) - 1:
        wf_html += "<span class='wf-arrow'>›</span>"
wf_html += "</div>"
st.markdown(wf_html, unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메트릭 대시보드
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-val'>{st.session_state.total_generated}</div>
        <div class='metric-lbl'>Total Tracks</div></div>""", unsafe_allow_html=True)
with m2:
    mode_display = st.session_state.production_mode or "—"
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-val' style='font-size:1em;padding-top:6px'>{mode_display}</div>
        <div class='metric-lbl'>Mode</div></div>""", unsafe_allow_html=True)
with m3:
    genre_display = st.session_state.selected_genre if st.session_state.selected_genre != "선택 안함" else "—"
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-val' style='font-size:0.95em;padding-top:6px'>{genre_display}</div>
        <div class='metric-lbl'>Genre</div></div>""", unsafe_allow_html=True)
with m4:
    use_display = st.session_state.selected_use if st.session_state.selected_use != "선택 안함" else "—"
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-val' style='font-size:0.9em;padding-top:6px'>{use_display}</div>
        <div class='metric-lbl'>Target</div></div>""", unsafe_allow_html=True)

st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 현재 프로젝트 결과물
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cp = st.session_state.current_project
if cp:
    st.markdown("#### 현재 프로젝트")
    c1, c2 = st.columns(2)
    with c1:
        if cp.get("lyrics"):
            with st.expander("가사 (Lyrics)", expanded=False):
                st.markdown(cp["lyrics"])
        if cp.get("strategy"):
            with st.expander("마켓 전략 (Strategy)", expanded=False):
                st.markdown(cp["strategy"])
    with c2:
        if cp.get("prompt"):
            with st.expander("프로덕션 브리프 (Music Brief)", expanded=False):
                st.code(cp["prompt"], language="markdown")
        if cp.get("summary"):
            with st.expander("최종 요약 (Summary)", expanded=False):
                st.markdown(cp["summary"])
    st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 대화
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if not st.session_state.messages:
    welcome = (
        "**SORIM Studio에 오신 것을 환영합니다.**\n\n"
        "왼쪽 사이드바에서 프로덕션 모드, 장르, 무드, 용도를 먼저 설정하세요.\n\n"
        "설정 완료 후 제작할 BGM의 주제나 콘셉트를 입력하시면 "
        "트랙 디자인부터 프로덕션 브리프, 마켓 전략까지 한 번에 제작합니다.\n\n"
        "예시: `고향 귀성길, 중년의 감성, 국악 퓨전` / `카페 Lo-fi BGM, 잔잔한 집중` / `빠르게`"
    )
    st.session_state.messages.append({"role": "assistant", "content": welcome})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 입력 처리
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if prompt := st.chat_input("BGM 콘셉트, 주제, 또는 감정을 입력하세요..."):
    # 사이드바 설정값 자동 주입
    context_parts = []
    if st.session_state.production_mode:
        context_parts.append(f"프로덕션 모드: {st.session_state.production_mode}")
    if st.session_state.selected_genre != "선택 안함":
        context_parts.append(f"장르: {st.session_state.selected_genre}")
    if st.session_state.selected_mood != "선택 안함":
        context_parts.append(f"무드: {st.session_state.selected_mood}")
    if st.session_state.selected_use != "선택 안함":
        context_parts.append(f"용도: {st.session_state.selected_use}")

    enriched = prompt
    if context_parts:
        enriched = f"[설정값: {' / '.join(context_parts)}]\n{prompt}"

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("프로덕션 브리프 생성 중..."):
            try:
                api_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
                for m in st.session_state.messages[:-1]:
                    api_msgs.append({"role": m["role"], "content": m["content"]})
                api_msgs.append({"role": "user", "content": enriched})

                result = call_groq(api_msgs)
                display = re.sub(r"###\w+_(START|END)###", "", result).strip()
                st.markdown(display)
                st.session_state.messages.append({"role": "assistant", "content": result})

                extracted = extract_all(result)

                if any(extracted.values()):
                    now = datetime.now()
                    project = {
                        "timestamp": now.strftime("%m/%d %H:%M"),
                        "concept": prompt[:30],
                        "mode": st.session_state.production_mode,
                        **extracted
                    }
                    st.session_state.projects.append(project)
                    st.session_state.current_project = project
                    st.session_state.total_generated += 1
                    st.session_state.last_gen_time = now
                    st.session_state.workflow_step = min(4, st.session_state.workflow_step + 1)

                    st.success("프로젝트가 저장되었습니다. 사이드바에서 내보내기가 가능합니다.")

                    c1, c2 = st.columns(2)
                    with c1:
                        if extracted["lyrics"]:
                            with st.expander("가사", expanded=True):
                                st.markdown(extracted["lyrics"])
                        if extracted["strategy"]:
                            with st.expander("마켓 전략", expanded=False):
                                st.markdown(extracted["strategy"])
                    with c2:
                        if extracted["prompt"]:
                            with st.expander("프로덕션 브리프 (영문)", expanded=True):
                                st.code(extracted["prompt"], language="markdown")
                        if extracted["summary"]:
                            with st.expander("최종 요약", expanded=False):
                                st.markdown(extracted["summary"])

            except Exception:
                st.error("오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
