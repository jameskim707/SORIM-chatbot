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
    page_title="SORIM Studio | AI BGM Production",
    page_icon="🎼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f5f7fa; }

.sorim-header {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #1a1f3c;
    border-radius: 10px;
    padding: 18px 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(26,31,60,0.08), 0 1px 4px rgba(0,0,0,0.04);
}
.sorim-title { font-size: 1.6em; font-weight: 700; color: #12172b; margin: 0; letter-spacing: -0.3px; }
.sorim-badge {
    display: inline-block; background: #1a1f3c; color: #fff;
    font-size: 0.6em; font-weight: 600; padding: 2px 8px;
    border-radius: 4px; margin-left: 8px; letter-spacing: 1px; vertical-align: middle;
}
.sorim-sub { color: #64748b; font-size: 0.82em; margin-top: 3px; font-weight: 400; }

.wf-bar {
    display: flex; align-items: center; background: #ffffff;
    border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 10px 18px; margin-bottom: 16px; gap: 6px; overflow-x: auto;
    box-shadow: 0 1px 4px rgba(26,31,60,0.04);
}
.wf-step { display: flex; align-items: center; gap: 5px; font-size: 0.75em; font-weight: 500; color: #94a3b8; white-space: nowrap; }
.wf-step.active { color: #1a1f3c; font-weight: 700; }
.wf-step.done { color: #22c55e; }
.wf-dot { width: 7px; height: 7px; border-radius: 50%; background: #e2e8f0; }
.wf-dot.active { background: #1a1f3c; }
.wf-dot.done { background: #22c55e; }
.wf-arrow { color: #cbd5e1; font-size: 0.7em; }

.metric-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 2px 8px rgba(26,31,60,0.06), 0 1px 3px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease;
}
.metric-card:hover {
    box-shadow: 0 4px 16px rgba(26,31,60,0.10), 0 1px 4px rgba(0,0,0,0.05);
}
.metric-val { font-size: 1.6em; font-weight: 700; color: #12172b; line-height: 1; }
.metric-lbl { font-size: 0.68em; color: #94a3b8; margin-top: 3px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }

.form-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 20px 24px; margin-bottom: 16px;
    box-shadow: 0 3px 14px rgba(26,31,60,0.07), 0 1px 4px rgba(0,0,0,0.04);
    transition: box-shadow 0.2s ease;
}
.form-card:focus-within {
    box-shadow: 0 4px 20px rgba(26,31,60,0.10), 0 0 0 2px rgba(26,31,60,0.06);
}
.form-title {
    font-size: 0.75em; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.2px; color: #475569; margin-bottom: 14px;
    border-bottom: 1px solid #e2e8f0; padding-bottom: 8px;
}

.preset-btn {
    display: inline-block; background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 6px; padding: 6px 12px; font-size: 0.78em; font-weight: 500;
    color: #374151; cursor: pointer; margin: 3px; transition: all 0.15s;
}
.preset-btn:hover { border-color: #0f172a; background: #f1f5f9; }

.result-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 16px; margin: 8px 0; box-shadow: 0 1px 4px rgba(0,0,0,0.03);
}
.result-label {
    font-size: 0.68em; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; color: #64748b; margin-bottom: 8px;
}

.version-tag {
    display: inline-block; background: #f1f5f9; border: 1px solid #e2e8f0;
    border-radius: 4px; padding: 2px 8px; font-size: 0.72em;
    color: #475569; font-weight: 500; margin-right: 4px;
}
.version-tag.active { background: #0f172a; color: #fff; border-color: #0f172a; }

section[data-testid="stSidebar"] { background: #f5f7fa; border-right: 1px solid #e2e8f0; }
.streamlit-expanderHeader {
    background: #f5f7fa !important; border-radius: 8px !important;
    border: 1px solid #e2e8f0 !important; font-size: 0.85em !important; font-weight: 500 !important;
}
.stChatMessage { border-radius: 8px !important; margin: 4px 0 !important; }
hr { border-color: #e2e8f0 !important; }
.stSuccess { background: #f0fdf4 !important; border: 1px solid #bbf7d0 !important; border-radius: 6px !important; font-size: 0.82em !important; }
.stButton button { 
    border-radius: 7px !important; font-weight: 500 !important; font-size: 0.85em !important;
    transition: all 0.15s ease !important;
}
.stButton button[kind="primary"] {
    background: #1a1f3c !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(26,31,60,0.20) !important;
    color: #ffffff !important;
}
.stButton button[kind="primary"]:hover {
    background: #252b4a !important;
    box-shadow: 0 4px 14px rgba(26,31,60,0.28) !important;
    transform: translateY(-1px) !important;
}
.stButton button:not([kind="primary"]):hover {
    border-color: #1a1f3c !important;
    color: #1a1f3c !important;
    background: #f0f2f8 !important;
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
        "projects": [],           # 프로젝트 목록
        "current_project": None,  # 현재 프로젝트
        "total_generated": 0,
        "last_gen_time": None,
        "workflow_step": 0,
        "form_concept": "",
        "form_preset": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PRESETS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRESETS = {
    "카페 Lo-fi": {"genre": "Lo-fi", "mood": "차분함", "use": "유튜브 BGM", "concept": "카페 분위기, 잔잔한 집중, 커피향 같은 음악"},
    "국악 시네마틱": {"genre": "국악 퓨전", "mood": "그리움/향수", "use": "스트리밍", "concept": "한국 전통 감성, 가야금과 오케스트라 융합"},
    "힐링 어쿠스틱": {"genre": "어쿠스틱 팝", "mood": "위로", "use": "명상/힐링", "concept": "자연 속 치유, 어쿠스틱 기타와 피아노"},
    "숏츠 훅": {"genre": "인디 팝", "mood": "설렘", "use": "숏츠/릴스", "concept": "짧고 강렬한 훅, 15초 안에 감정 폭발"},
    "감성 발라드": {"genre": "시네마틱 발라드", "mood": "감동", "use": "스트리밍", "concept": "중년 감성, 부모님, 고향, 회상"},
    "게임 BGM": {"genre": "시네마틱 발라드", "mood": "긴장감", "use": "인디 게임 BGM", "concept": "판타지 인디 게임, 긴장과 해방의 반복"},
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SYSTEM PROMPTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BASE_RULES = """
CRITICAL RULES:
1. Respond in Korean ONLY (except STEP 4 music prompts — English ONLY).
2. Produce COMPLETE, DETAILED, production-grade outputs every time.
3. Use EXACT markers: ###LYRICS_START### ###LYRICS_END### ###PROMPT_START### ###PROMPT_END### ###STRATEGY_START### ###STRATEGY_END### ###SUMMARY_START### ###SUMMARY_END###
4. Tone: Professional, directive, minimal. No excessive filler phrases.
5. For lyrics: always suggest 3 title candidates first, then write full lyrics.
"""

SINGLE_PROMPT = BASE_RULES + """
You are SORIM Studio — AI-Directed BGM Production System.
Mode: SINGLE TRACK

Produce a complete single BGM package:

[PHASE 1 - TRACK DESIGN]
- Track concept (one sentence)
- Target platform and audience
- Emotional arc (3 stages)
- Tempo / Key / Instrumentation palette

[PHASE 2 - LYRICS] (if vocal)
###LYRICS_START###
제목 후보 3개 (각 이유 포함)
Variation A (접근형): [Verse1][Pre-Chorus][Chorus][Verse2][Bridge]
Variation B (시네마틱): 동일 구조, 시적 표현
Hook Line: 15초용 1-2줄
###LYRICS_END###

[PHASE 3 - MUSIC BRIEF] English ONLY
###PROMPT_START###
[SORIM BGM BRIEF — SHORTS 30s]
Genre / Mood / BPM range / Key / Time Sig
Hook target: 12-15s
Timeline: 0:00 / 0:05 / 0:13 / 0:25 / 0:30
Dynamic: Intro(30%)>Build(55%)>Peak(85%)>Out(40%)
Vocal: type / tone / register / harmony / mic proximity
Mix: reverb / stereo / compression / EQ

[SORIM BGM BRIEF — FULL TRACK]
Genre / Mood / BPM / Key+modulation / Duration
Full structure table: Time|Section|Instruments|Intensity%
Dynamic arc: Intro(25%)>V1(40%)>Pre(60%)>Ch1(85%)>V2(45%)>Pre(65%)>Ch2(90%)>Bridge(35%)>FinalCh(95%)>Outro(15%)
Instrument details / Vocal direction / Production notes / -14 LUFS
Safety: Do not imitate any specific artist or copyrighted work.
###PROMPT_END###

[PHASE 4 - MARKET STRATEGY]
###STRATEGY_START###
Platform fit / Metadata (Title KR+EN, Tags, Description) / Packaging / Pricing
###STRATEGY_END###

[PHASE 5 - SUMMARY]
###SUMMARY_START###
Table: Concept / Genre / BPM / Key / Vocal / Platform / Next action
###SUMMARY_END###
"""

ALBUM_PROMPT = BASE_RULES + """
You are SORIM Studio — AI-Directed BGM Production System.
Mode: ALBUM PACK (3-track structured set)

Produce a complete 3-track album package with thematic consistency:

TRACK 1 — INTRO TRACK
- Lighter, atmospheric, sets the mood
- Shorter (1:30-2:00), instrumental preferred
- Establishes the album's sonic identity

TRACK 2 — MAIN TRACK
- Full production, vocal if requested
- Complete structure (2:30-3:30)
- Emotional peak of the album

TRACK 3 — OUTRO TRACK
- Resolution, softer, reflective
- Mirror of intro but with emotional closure
- Fade or ambient ending

For EACH track produce:
###PROMPT_START###
[TRACK 1 — INTRO]
Full English brief: Genre/Mood/BPM/Key/Structure/Instruments/Mix
[TRACK 2 — MAIN]
Full English brief + Vocal direction if applicable
[TRACK 3 — OUTRO]
Full English brief: Resolution/Fade/Ambient
Safety: Do not imitate any specific artist or copyrighted work.
###PROMPT_END###

###LYRICS_START###
(Main track lyrics only — 3 title candidates + Variation A + Variation B + Hook)
###LYRICS_END###

###STRATEGY_START###
Album packaging strategy / Bundle pricing / Platform submission plan
###STRATEGY_END###

###SUMMARY_START###
Album concept table: Track | Title | Genre | BPM | Duration | Role
###SUMMARY_END###
"""

SHORTS_PROMPT = BASE_RULES + """
You are SORIM Studio — AI-Directed BGM Production System.
Mode: SHORTS PACK (3x30s hook-forward variants)

Produce 3 distinct 30-second variants optimized for Shorts/Reels/TikTok:

VARIANT 1 — ENERGY VERSION: High impact, fast build, peak by 10s
VARIANT 2 — EMOTIONAL VERSION: Slower build, intimate, peak by 15s
VARIANT 3 — NEUTRAL/BACKGROUND: Subtle, non-distracting, consistent energy

###PROMPT_START###
[VARIANT 1 — ENERGY]
BPM / Key / Hook at: 0:08 / Instruments / Dynamic arc / Vocal / Mix
[VARIANT 2 — EMOTIONAL]
BPM / Key / Hook at: 0:13 / Instruments / Dynamic arc / Vocal / Mix
[VARIANT 3 — NEUTRAL BGM]
BPM / Key / Consistent energy / Instruments / No vocal / Mix
Safety: Do not imitate any specific artist or copyrighted work.
###PROMPT_END###

###LYRICS_START###
(Variant 1 & 2 hook lines only — 1-2 lines each, Korean)
###LYRICS_END###

###STRATEGY_START###
Shorts platform strategy / Hook timing tips / Metadata for each variant
###STRATEGY_END###

###SUMMARY_START###
Table: Variant | BPM | Hook Target | Best For
###SUMMARY_END###
"""

TARGET_PROMPT = BASE_RULES + """
You are SORIM Studio — AI-Directed BGM Production System.
Mode: TARGET MARKET (platform-optimized single)

Analyze the target platform deeply and optimize every production decision for it:
- YouTube BGM: long-form friendly, non-distracting, loop-ready
- Spotify/Streaming: hook within 30s, playlist-friendly, emotional arc
- Stock Music (Artlist/Musicbed): neutral, versatile, no lyrics preferred
- Game BGM: loopable, layered, mood-adaptive

###PROMPT_START###
[TARGET MARKET BRIEF]
Platform analysis / Listener behavior / Optimization decisions
Full production brief (BPM/Key/Structure/Instruments/Mix)
Platform-specific mix notes
Safety: Do not imitate any specific artist or copyrighted work.
###PROMPT_END###

###LYRICS_START###
(Only if platform supports vocal — 3 titles + Variation A + Hook)
###LYRICS_END###

###STRATEGY_START###
Submission strategy / Metadata optimization / Pricing / Distribution plan
###STRATEGY_END###

###SUMMARY_START###
Platform fit score / Key decisions / Action plan
###SUMMARY_END###
"""

MODE_PROMPTS = {
    "Single Track": SINGLE_PROMPT,
    "Album Pack": ALBUM_PROMPT,
    "Shorts Pack": SHORTS_PROMPT,
    "Target Market": TARGET_PROMPT,
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# HELPERS
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

def create_zip(project):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        if project.get("lyrics"): zf.writestr("lyrics.txt", project["lyrics"])
        if project.get("prompt"): zf.writestr("music_brief.txt", project["prompt"])
        if project.get("strategy"): zf.writestr("market_strategy.txt", project["strategy"])
        if project.get("summary"): zf.writestr("summary.txt", project["summary"])
        meta = {k: v for k, v in project.items() if k not in ["versions"]}
        zf.writestr("project.json", json.dumps(meta, ensure_ascii=False, indent=2))
    buf.seek(0)
    return buf

def call_groq(system_prompt, messages):
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": system_prompt}] + messages,
            "temperature": 0.72,
            "max_tokens": 4096
        }
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def determine_workflow_step(project):
    if not project: return 0
    if project.get("summary"): return 4
    if project.get("strategy"): return 3
    if project.get("prompt"): return 2
    if project.get("lyrics"): return 1
    return 0

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("**SORIM Studio**")
    st.caption("AI BGM Production System v5.0")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.metric("트랙 수", st.session_state.total_generated)
    with c2:
        t = st.session_state.last_gen_time
        st.metric("마지막", t.strftime("%H:%M") if t else "—")

    st.markdown("---")
    st.markdown("**프로젝트 히스토리**")

    if st.session_state.projects:
        labels = [f"[{p.get('mode','?')[:3]}] {p['timestamp']} · {p.get('concept','')[:10]}..."
                  for p in reversed(st.session_state.projects)]
        sel = st.selectbox("", labels, label_visibility="collapsed")
        idx = len(st.session_state.projects) - 1 - labels.index(sel)
        selected_p = st.session_state.projects[idx]

        # 버전 관리
        versions = selected_p.get("versions", [selected_p])
        if len(versions) > 1:
            st.caption(f"버전 {len(versions)}개 보유")
            ver_idx = st.selectbox("버전 선택",
                [f"v{i+1} — {v.get('ver_time','')}" for i, v in enumerate(versions)],
                label_visibility="collapsed")
            v_num = int(ver_idx.split(" ")[0][1:]) - 1
            view_project = versions[v_num]
        else:
            view_project = selected_p

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("불러오기", use_container_width=True):
                st.session_state.current_project = view_project
                st.session_state.workflow_step = determine_workflow_step(view_project)
                st.rerun()
        with col_b:
            if st.button("전체삭제", use_container_width=True):
                st.session_state.projects = []
                st.session_state.current_project = None
                st.rerun()
    else:
        st.caption("생성된 프로젝트 없음")

    st.markdown("---")
    st.markdown("**내보내기**")
    cp = st.session_state.current_project
    if cp:
        today = datetime.now().strftime("%Y%m%d_%H%M")
        if cp.get("lyrics"):
            st.download_button("가사 TXT", cp["lyrics"],
                               file_name=f"SORIM_lyrics_{today}.txt", use_container_width=True)
        if cp.get("prompt"):
            st.download_button("브리프 TXT", cp["prompt"],
                               file_name=f"SORIM_brief_{today}.txt", use_container_width=True)
        zb = create_zip(cp)
        st.download_button("전체 ZIP", zb,
                           file_name=f"SORIM_project_{today}.zip",
                           mime="application/zip", use_container_width=True)
    else:
        st.caption("프로젝트 생성 후 활성화")

    st.markdown("---")
    if st.button("새 프로젝트", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_project = None
        st.session_state.workflow_step = 0
        st.session_state.form_concept = ""
        st.session_state.form_preset = None
        st.rerun()
    st.caption("v5.0 · Groq · LLaMA 3.3-70b")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if not API_KEY:
    st.error("서비스 설정 오류입니다. 관리자에게 문의하세요.")
    st.stop()

# 헤더
st.markdown("""
<div class='sorim-header'>
    <div class='sorim-title'>SORIM Studio <span class='sorim-badge'>BGM PRODUCTION</span></div>
    <div class='sorim-sub'>AI-Directed BGM Production System · Form-Driven Workflow</div>
</div>
""", unsafe_allow_html=True)

# 워크플로우 바
steps = ["Concept", "Track Design", "Brief", "Strategy", "Export"]
step = st.session_state.workflow_step
wf = "<div class='wf-bar'>"
for i, s in enumerate(steps):
    cls = "done" if i < step else ("active" if i == step else "")
    wf += f"<div class='wf-step {cls}'><div class='wf-dot {cls}'></div>{s}</div>"
    if i < len(steps)-1: wf += "<span class='wf-arrow'>›</span>"
wf += "</div>"
st.markdown(wf, unsafe_allow_html=True)

# 메트릭
m1, m2, m3, m4 = st.columns(4)
cp = st.session_state.current_project
with m1:
    st.markdown(f"<div class='metric-card'><div class='metric-val'>{st.session_state.total_generated}</div><div class='metric-lbl'>Total Tracks</div></div>", unsafe_allow_html=True)
with m2:
    mode_d = cp.get("mode", "—") if cp else "—"
    st.markdown(f"<div class='metric-card'><div class='metric-val' style='font-size:0.9em;padding-top:4px'>{mode_d}</div><div class='metric-lbl'>Mode</div></div>", unsafe_allow_html=True)
with m3:
    genre_d = cp.get("genre", "—") if cp else "—"
    st.markdown(f"<div class='metric-card'><div class='metric-val' style='font-size:0.9em;padding-top:4px'>{genre_d}</div><div class='metric-lbl'>Genre</div></div>", unsafe_allow_html=True)
with m4:
    ver_d = f"v{len(cp.get('versions',[1]))}" if cp else "—"
    st.markdown(f"<div class='metric-card'><div class='metric-val'>{ver_d}</div><div class='metric-lbl'>Version</div></div>", unsafe_allow_html=True)

st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 프로덕션 폼
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("<div class='form-card'>", unsafe_allow_html=True)
st.markdown("<div class='form-title'>PRODUCTION SETUP</div>", unsafe_allow_html=True)

# 빠른 프리셋
st.markdown("**빠른 프리셋**")
preset_cols = st.columns(6)
preset_names = list(PRESETS.keys())
for i, pname in enumerate(preset_names):
    with preset_cols[i]:
        if st.button(pname, use_container_width=True, key=f"preset_{i}"):
            st.session_state.form_preset = pname
            st.rerun()

# 프리셋 적용 표시
if st.session_state.form_preset:
    p = PRESETS[st.session_state.form_preset]
    st.info(f"프리셋 적용: **{st.session_state.form_preset}** — {p['concept']}")

st.markdown("---")

# 폼 입력
col_left, col_right = st.columns([1, 1])

with col_left:
    preset_data = PRESETS.get(st.session_state.form_preset, {})

    production_mode = st.selectbox("프로덕션 모드", ["Single Track", "Album Pack", "Shorts Pack", "Target Market"])
    genre_list = ["시네마틱 발라드", "어쿠스틱 팝", "Lo-fi", "국악 퓨전", "재즈", "R&B", "힙합", "EDM", "인디 팝", "클래식 크로스오버"]
    genre_default = genre_list.index(preset_data["genre"]) if preset_data.get("genre") in genre_list else 0
    genre = st.selectbox("장르", genre_list, index=genre_default)

    mood_list = ["그리움/향수", "해방감", "설렘", "위로", "활력", "차분함", "긴장감", "감동", "중립 BGM"]
    mood_default = mood_list.index(preset_data["mood"]) if preset_data.get("mood") in mood_list else 0
    mood = st.selectbox("무드", mood_list, index=mood_default)

with col_right:
    use_list = ["유튜브 BGM", "숏츠/릴스", "스트리밍", "스톡 뮤직", "인디 게임 BGM", "광고/브랜드", "명상/힐링"]
    use_default = use_list.index(preset_data["use"]) if preset_data.get("use") in use_list else 0
    use_case = st.selectbox("용도", use_list, index=use_default)
    vocal = st.selectbox("보컬", ["보컬 없음 (순수 BGM)", "여성 보컬", "남성 보컬", "듀엣"])
    tempo = st.selectbox("템포", ["Slow (60-75 BPM)", "Mid (76-100 BPM)", "Uptempo (101-130 BPM)"])

concept = st.text_area(
    "콘셉트 / 주제 / 감정",
    value=preset_data.get("concept", st.session_state.form_concept),
    placeholder="예: 비 오는 날 카페에서 느끼는 고독함, 창밖의 빗소리와 피아노...",
    height=80
)

# 추가 지시사항 (접기)
with st.expander("추가 지시사항 (선택)", expanded=False):
    additional = st.text_area("악기, 참고 분위기, 특별 요청 등", height=60, placeholder="예: 가야금 필수 포함, 드럼 없이, 잔향이 많은 사운드...")
    
if 'additional' not in dir():
    additional = ""

generate_col, clear_col = st.columns([3, 1])
with generate_col:
    generate_btn = st.button("프로덕션 시작", type="primary", use_container_width=True)
with clear_col:
    if st.button("초기화", use_container_width=True):
        st.session_state.form_preset = None
        st.session_state.form_concept = ""
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 결과물 표시 (현재 프로젝트)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cp = st.session_state.current_project
if cp:
    st.markdown("---")
    # 버전 태그 표시
    versions = cp.get("versions", [cp])
    ver_html = "".join([
        f"<span class='version-tag {'active' if i == len(versions)-1 else ''}'>"
        f"v{i+1} {v.get('ver_time','')}</span>"
        for i, v in enumerate(versions)
    ])
    st.markdown(f"**현재 프로젝트** — {cp.get('concept','')[:30]}... {ver_html}", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if cp.get("lyrics"):
            with st.expander("가사 (Lyrics)", expanded=True):
                st.markdown(cp["lyrics"])
        if cp.get("strategy"):
            with st.expander("마켓 전략 (Strategy)", expanded=False):
                st.markdown(cp["strategy"])
    with c2:
        if cp.get("prompt"):
            with st.expander("프로덕션 브리프 (Music Brief)", expanded=True):
                st.code(cp["prompt"], language="markdown")
        if cp.get("summary"):
            with st.expander("최종 요약 (Summary)", expanded=False):
                st.markdown(cp["summary"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 생성 처리
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if generate_btn:
    if not concept.strip():
        st.warning("콘셉트를 입력해주세요.")
        st.stop()

    # 프롬프트 구성
    user_input = f"""
프로덕션 모드: {production_mode}
장르: {genre}
무드: {mood}
용도: {use_case}
보컬: {vocal}
템포: {tempo}
콘셉트: {concept}
{f'추가 지시: {additional}' if additional else ''}

위 설정으로 완전한 BGM 프로덕션 패키지를 제작해주세요.
"""

    system_prompt = MODE_PROMPTS.get(production_mode, SINGLE_PROMPT)

    with st.spinner("프로덕션 브리프 생성 중..."):
        try:
            result = call_groq(system_prompt, [{"role": "user", "content": user_input}])
            extracted = extract_all(result)
            display = re.sub(r"###\w+_(START|END)###", "", result).strip()

            now = datetime.now()
            new_project = {
                "timestamp": now.strftime("%m/%d %H:%M"),
                "ver_time": now.strftime("%H:%M"),
                "concept": concept[:40],
                "mode": production_mode,
                "genre": genre,
                "mood": mood,
                "use": use_case,
                **extracted,
            }

            # 버전 관리 — 같은 콘셉트면 버전 추가, 아니면 새 프로젝트
            cp_existing = st.session_state.current_project
            if cp_existing and cp_existing.get("concept","")[:20] == concept[:20]:
                versions = cp_existing.get("versions", [cp_existing])
                versions.append(new_project)
                new_project["versions"] = versions
                # 기존 프로젝트 업데이트
                for i, p in enumerate(st.session_state.projects):
                    if p.get("timestamp") == cp_existing.get("timestamp"):
                        st.session_state.projects[i] = new_project
                        break
            else:
                new_project["versions"] = [new_project]
                st.session_state.projects.append(new_project)

            st.session_state.current_project = new_project
            st.session_state.total_generated += 1
            st.session_state.last_gen_time = now
            st.session_state.workflow_step = determine_workflow_step(new_project)

            st.success("프로덕션 완료. 사이드바에서 내보내기가 가능합니다.")
            st.rerun()

        except Exception as e:
            st.error("생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
