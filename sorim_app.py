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
    page_title="SORIM Studio | AI Music Production Suite",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CSS — PREMIUM DARK THEME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0a0a14 0%, #0e0e1e 50%, #12101a 100%);
    }

    /* 헤더 */
    .sorim-header {
        background: linear-gradient(90deg, #1a0533 0%, #0d1a3a 100%);
        border: 1px solid #3a1f6e;
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 32px rgba(100, 50, 200, 0.2);
    }
    .sorim-title {
        font-size: 2.4em;
        font-weight: 700;
        background: linear-gradient(90deg, #c084fc, #818cf8, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .sorim-subtitle {
        color: #94a3b8;
        font-size: 0.95em;
        margin-top: 6px;
    }

    /* 결과물 블록 */
    .result-block {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 2px 16px rgba(0,0,0,0.3);
        transition: box-shadow 0.2s ease;
    }
    .result-block:hover {
        box-shadow: 0 4px 24px rgba(100, 50, 200, 0.15);
    }

    /* 메트릭 */
    .metric-box {
        background: linear-gradient(135deg, #1e1033 0%, #0f1e35 100%);
        border: 1px solid #2d1f5e;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 2em;
        font-weight: 700;
        color: #c084fc;
    }
    .metric-label {
        font-size: 0.8em;
        color: #64748b;
        margin-top: 4px;
    }

    /* 프로젝트 히스토리 */
    .project-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 12px;
        margin: 6px 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    .project-card:hover {
        border-color: #7c3aed;
        background: rgba(124, 58, 237, 0.08);
    }

    /* 채팅 메시지 */
    .stChatMessage {
        border-radius: 12px !important;
        margin: 8px 0 !important;
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a14 0%, #0d0d1a 100%);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* 구분선 */
    hr { border-color: rgba(255,255,255,0.06) !important; }

    /* 성공 메시지 */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SECURITY — API KEY FROM SECRETS ONLY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def get_api_key():
    try:
        key = st.secrets["GROQ_API_KEY"]
        if not key or len(key) < 10:
            return None
        return key
    except Exception:
        return None

API_KEY = get_api_key()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SESSION STATE 초기화
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def init_session():
    defaults = {
        "messages": [],
        "projects": [],
        "current_project": None,
        "total_generated": 0,
        "last_gen_time": None,
        "last_lyrics": "",
        "last_prompt": "",
        "last_strategy": "",
        "last_summary": "",
        "last_emotion": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SYSTEM PROMPT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEM_PROMPT = """
CRITICAL RULES — MUST FOLLOW ALWAYS:
1. ALWAYS respond in Korean ONLY. Never use Chinese, Arabic, Japanese, or any other language.
2. ALWAYS produce COMPLETE and DETAILED outputs. Never give short or vague answers.
3. Lyrics: Write FULL lyrics — [Verse 1][Pre-Chorus][Chorus][Verse 2][Bridge] — minimum 16 lines.
4. Do NOT ask unnecessary questions. If enough info exists, produce outputs immediately.
5. Never mix languages mid-sentence.
6. STEP 4 music prompts MUST be in English ONLY. Non-negotiable.
7. Music prompts must be PRODUCTION-GRADE — like a professional music director's brief.
8. Always use these EXACT section markers so results can be parsed:
   ###LYRICS_START### ... ###LYRICS_END###
   ###PROMPT_START### ... ###PROMPT_END###
   ###STRATEGY_START### ... ###STRATEGY_END###
   ###SUMMARY_START### ... ###SUMMARY_END###

[MASTER SYSTEM PROMPT — SORIM STUDIO v4.0]
You are SORIM, a professional AI Music Production Suite.
Role: Emotional Lyricist + Music Producer + Content Monetization Strategist.
Mission: Transform emotion into commercially viable music packages.

WORKFLOW:

[STEP 1 - INTAKE] Korean
Max 3 questions. If enough info → skip to STEP 2.

[STEP 2 - LYRIC GENERATION] Korean
Output between ###LYRICS_START### and ###LYRICS_END###

Write TWO versions:
Variation A (접근형):
[Verse 1] 4줄 / [Pre-Chorus] 2줄 / [Chorus] 4줄 / [Verse 2] 4줄 / [Bridge] 2줄

Variation B (시네마틱형): Same structure, more poetic.
+ Shorts Hook: 1-2 lines

[STEP 3 - GENRE CURATION] Korean
1 Primary + 2 Alternative genres with reasoning.

[STEP 4 - MUSIC PROMPTS] English ONLY
Output between ###PROMPT_START### and ###PROMPT_END###

**[SORIM MUSIC BRIEF — SHORTS 30s]**
Genre & Mood / BPM range / Key / Time Signature
Instrumentation & Entry Timeline (0:00 → 0:30 with timestamps)
Dynamic Arc: Intro(30%) → Build(55%) → Hook(85%) → Resolution(40%)
Vocal Direction: Type / Tone / Register / Harmony / Mic proximity / Performance note
Production & Mix Notes: Reverb / Percussion / Swell point / Mixing guidance
Safety: Do NOT imitate any specific artist or copyrighted material.

**[SORIM MUSIC BRIEF — FULL TRACK]**
Genre & Mood / BPM range / Key + modulation / Time Signature / Duration
Full Structure Table: Timestamp | Section | Instrumentation | Intensity %
Dynamic Arc: Intro(25%)→V1(40%)→Pre(60%)→Ch1(85%)→V2(45%)→Pre(65%)→Ch2(90%)→Bridge(35%)→FinalCh(95%)→Outro(15%)
Instrumentation Details: felt piano / fingerstyle guitar / cello / ambient pad / percussion
Vocal Direction: Type / Tone / Register progression / Harmony entry / Breath notes
Production: Reverb (hall/plate/room) / Stereo field / Mixing / Mastering (-14 LUFS)
Safety: Do NOT imitate any specific artist or copyrighted material.

[STEP 5 - MONETIZATION] Korean
Output between ###STRATEGY_START### and ###STRATEGY_END###
2-4 channels + reasoning + Metadata (Title KR+EN, Tags, Description) + Packaging

[STEP 6 - SUMMARY] Korean
Output between ###SUMMARY_START### and ###SUMMARY_END###
Clean final summary + next action for user.

FAST MODE: "빠르게" → STEP1(1Q) → STEP3 → STEP4(Shorts only)
REFUSAL: "저작권 위반 가능성이 있어 도움드리기 어려워요. 비슷한 감성으로 새롭게 만들어드릴게요."
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXTRACTION FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def extract_section(text, start_marker, end_marker):
    pattern = f"{start_marker}(.*?){end_marker}"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_all(text):
    return {
        "lyrics": extract_section(text, "###LYRICS_START###", "###LYRICS_END###"),
        "prompt": extract_section(text, "###PROMPT_START###", "###PROMPT_END###"),
        "strategy": extract_section(text, "###STRATEGY_START###", "###STRATEGY_END###"),
        "summary": extract_section(text, "###SUMMARY_START###", "###SUMMARY_END###"),
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ZIP 생성 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def create_zip(project):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        ts = project["timestamp"]
        if project.get("lyrics"):
            zf.writestr(f"lyrics.txt", project["lyrics"])
        if project.get("prompt"):
            zf.writestr(f"music_prompt.txt", project["prompt"])
        if project.get("strategy"):
            zf.writestr(f"monetization.txt", project["strategy"])
        if project.get("summary"):
            zf.writestr(f"summary.txt", project["summary"])
        meta = {k: v for k, v in project.items() if k != "timestamp"}
        meta["timestamp"] = ts
        zf.writestr("project.json", json.dumps(meta, ensure_ascii=False, indent=2))
    buf.seek(0)
    return buf

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GROQ API 호출
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def call_groq(messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.75,
        "max_tokens": 4096
    }
    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIDEBAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("### 🎵 SORIM Studio")
    st.markdown("---")

    # 메트릭
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class='metric-box'>
            <div class='metric-value'>{st.session_state.total_generated}</div>
            <div class='metric-label'>생성된 곡</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        last_time = st.session_state.last_gen_time
        display_time = last_time.strftime("%H:%M") if last_time else "—"
        st.markdown(f"""
        <div class='metric-box'>
            <div class='metric-value' style='font-size:1.3em'>{display_time}</div>
            <div class='metric-label'>마지막 생성</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # 프로젝트 히스토리
    st.markdown("### 📁 프로젝트 히스토리")
    if st.session_state.projects:
        project_labels = [
            f"🎵 {p['timestamp']} | {p.get('emotion','')[:15]}..."
            for p in reversed(st.session_state.projects)
        ]
        selected = st.selectbox("프로젝트 선택", project_labels, label_visibility="collapsed")
        idx = len(st.session_state.projects) - 1 - project_labels.index(selected)

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📂 불러오기", use_container_width=True):
                p = st.session_state.projects[idx]
                st.session_state.last_lyrics = p.get("lyrics", "")
                st.session_state.last_prompt = p.get("prompt", "")
                st.session_state.last_strategy = p.get("strategy", "")
                st.session_state.last_summary = p.get("summary", "")
                st.session_state.current_project = p
                st.rerun()
        with col_b:
            if st.button("🗑️ 전체삭제", use_container_width=True):
                st.session_state.projects = []
                st.rerun()
    else:
        st.caption("아직 생성된 프로젝트가 없어요")

    st.markdown("---")

    # 내보내기
    st.markdown("### 💾 내보내기")
    current = st.session_state.current_project

    if current:
        today = datetime.now().strftime("%Y%m%d_%H%M")

        if current.get("lyrics"):
            st.download_button("🎤 가사 TXT", current["lyrics"],
                             file_name=f"SORIM_가사_{today}.txt", use_container_width=True)
        if current.get("prompt"):
            st.download_button("🎼 프롬프트 TXT", current["prompt"],
                             file_name=f"SORIM_프롬프트_{today}.txt", use_container_width=True)

        # ZIP 전체 다운로드
        zip_buf = create_zip(current)
        st.download_button(
            "📦 전체 ZIP 다운로드",
            zip_buf,
            file_name=f"SORIM_프로젝트_{today}.zip",
            mime="application/zip",
            use_container_width=True
        )
    else:
        st.caption("프로젝트를 생성하거나 불러오세요")

    st.markdown("---")

    # 대화 초기화
    if st.button("🔄 새 대화 시작", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_project = None
        st.session_state.last_lyrics = ""
        st.session_state.last_prompt = ""
        st.session_state.last_strategy = ""
        st.session_state.last_summary = ""
        st.rerun()

    st.markdown("---")
    st.caption("**Fast Mode:** '빠르게' 입력")
    st.caption("v4.0 | Powered by Groq + LLaMA")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 메인 헤더
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
st.markdown("""
<div class='sorim-header'>
    <div class='sorim-title'>🎵 SORIM Studio</div>
    <div class='sorim-subtitle'>Professional AI Music Production Suite · 당신의 감정을 음악으로</div>
</div>
""", unsafe_allow_html=True)

# API 키 오류 처리
if not API_KEY:
    st.error("⚠️ 서비스 설정 오류가 발생했습니다. 관리자에게 문의해주세요.")
    st.stop()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 현재 프로젝트 결과물 표시 (expander)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
cp = st.session_state.current_project
if cp:
    st.markdown("#### 📋 현재 프로젝트 결과물")
    col1, col2 = st.columns(2)
    with col1:
        if cp.get("lyrics"):
            with st.expander("🎤 가사", expanded=False):
                st.markdown(cp["lyrics"])
        if cp.get("strategy"):
            with st.expander("💰 수익화 전략", expanded=False):
                st.markdown(cp["strategy"])
    with col2:
        if cp.get("prompt"):
            with st.expander("🎼 음악 프롬프트 (영문)", expanded=False):
                st.code(cp["prompt"], language="markdown")
        if cp.get("summary"):
            with st.expander("📦 최종 요약", expanded=False):
                st.markdown(cp["summary"])
    st.markdown("---")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 대화 표시
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if not st.session_state.messages:
    welcome = "안녕하세요, 저는 SORIM이에요 🎵\n\n당신의 감정과 이야기를 음악으로 만들어드리는 AI 뮤직 파트너예요.\n\n지금 어떤 감정이나 장면을 음악으로 담고 싶으신가요?\n천천히 말씀해 주세요 — 어떤 이야기든 괜찮아요."
    st.session_state.messages.append({"role": "assistant", "content": welcome})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 입력 처리
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if prompt := st.chat_input("감정이나 상황을 말씀해 주세요..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("SORIM이 음악을 구상하고 있어요... 🎵"):
            try:
                api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
                for msg in st.session_state.messages:
                    api_messages.append({"role": msg["role"], "content": msg["content"]})

                result = call_groq(api_messages)

                # 마커 제거 후 표시
                display_result = re.sub(r"###\w+_(START|END)###", "", result).strip()
                st.markdown(display_result)
                st.session_state.messages.append({"role": "assistant", "content": result})

                # 결과물 추출
                extracted = extract_all(result)

                # 프로젝트 저장
                if any(extracted.values()):
                    now = datetime.now()
                    project = {
                        "timestamp": now.strftime("%m/%d %H:%M"),
                        "emotion": prompt[:30],
                        **extracted
                    }
                    st.session_state.projects.append(project)
                    st.session_state.current_project = project
                    st.session_state.total_generated += 1
                    st.session_state.last_gen_time = now

                    # 결과물 expander 표시
                    st.markdown("---")
                    st.success("✅ 프로젝트가 저장됐어요! 사이드바에서 다운로드하세요.")

                    c1, c2 = st.columns(2)
                    with c1:
                        if extracted["lyrics"]:
                            with st.expander("🎤 가사 보기", expanded=True):
                                st.markdown(extracted["lyrics"])
                        if extracted["strategy"]:
                            with st.expander("💰 수익화 전략", expanded=False):
                                st.markdown(extracted["strategy"])
                    with c2:
                        if extracted["prompt"]:
                            with st.expander("🎼 음악 프롬프트 (영문)", expanded=True):
                                st.code(extracted["prompt"], language="markdown")
                        if extracted["summary"]:
                            with st.expander("📦 최종 요약", expanded=False):
                                st.markdown(extracted["summary"])

            except Exception as e:
                st.error(f"❌ 오류가 발생했어요. 잠시 후 다시 시도해주세요.")
