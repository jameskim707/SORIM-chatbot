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
        background: linear-gradient(135deg, #f0faf5 0%, #e8f8f0 50%, #f5fdf8 100%);
    }

    /* 헤더 */
    .sorim-header {
        background: linear-gradient(90deg, #d4f5e9 0%, #c8f0e0 100%);
        border: 1px solid #6fcfa0;
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 32px rgba(80, 200, 140, 0.2);
    }
    .sorim-title {
        font-size: 2.4em;
        font-weight: 700;
        background: linear-gradient(90deg, #10b981, #34d399, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .sorim-subtitle {
        color: #374151;
        font-size: 0.95em;
        margin-top: 6px;
    }

    /* 결과물 블록 */
    .result-block {
        background: rgba(255,255,255,0.7);
        border: 1px solid rgba(80, 200, 140, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 2px 16px rgba(80, 200, 140, 0.1);
        transition: box-shadow 0.2s ease;
    }
    .result-block:hover {
        box-shadow: 0 4px 24px rgba(80, 200, 140, 0.25);
    }

    /* 메트릭 */
    .metric-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 1px solid #6ee7b7;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 2em;
        font-weight: 700;
        color: #059669;
    }
    .metric-label {
        font-size: 0.8em;
        color: #374151;
        margin-top: 4px;
    }

    /* 프로젝트 히스토리 */
    .project-card {
        background: rgba(255,255,255,0.7);
        border: 1px solid rgba(80, 200, 140, 0.2);
        border-radius: 8px;
        padding: 12px;
        margin: 6px 0;
        cursor: pointer;
        transition: all 0.2s;
    }
    .project-card:hover {
        border-color: #10b981;
        background: rgba(16, 185, 129, 0.08);
    }

    /* 채팅 메시지 */
    .stChatMessage {
        border-radius: 12px !important;
        margin: 8px 0 !important;
    }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ecfdf5 0%, #d1fae5 100%);
        border-right: 1px solid rgba(80, 200, 140, 0.3);
    }

    /* expander */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.6) !important;
        border-radius: 8px !important;
        border: 1px solid rgba(80, 200, 140, 0.2) !important;
    }

    /* 구분선 */
    hr { border-color: rgba(80, 200, 140, 0.2) !important; }

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
7. Music prompts must be PRODUCTION-GRADE — written as a professional music director's brief.
8. REPLACE all vague emotional descriptors with concrete acoustic/performance directives.
9. Always use these EXACT section markers:
   ###LYRICS_START### ... ###LYRICS_END###
   ###PROMPT_START### ... ###PROMPT_END###
   ###STRATEGY_START### ... ###STRATEGY_END###
   ###SUMMARY_START### ... ###SUMMARY_END###

[MASTER SYSTEM PROMPT — SORIM STUDIO v5.0]
You are SORIM, a professional AI Music Production Suite.
Role: Emotional Lyricist + Music Producer + Content Monetization Strategist.
Mission: Transform emotion into commercially viable, production-ready music packages.

WORKFLOW:

[STEP 1 - INTAKE] Korean
Max 3 questions. If enough info → skip to STEP 2.

[STEP 2 - LYRIC GENERATION] Korean
Output between ###LYRICS_START### and ###LYRICS_END###
Write TWO versions:
Variation A (접근형): [Verse 1] 4줄 / [Pre-Chorus] 2줄 / [Chorus] 4줄 / [Verse 2] 4줄 / [Bridge] 2줄
Variation B (시네마틱형): Same structure, more poetic and visual.
+ Shorts Hook: 1-2 lines

[STEP 3 - GENRE CURATION] Korean
1 Primary + 2 Alternative genres with acoustic reasoning (not emotional labels).

[STEP 4 - MUSIC PROMPTS] ★ ENGLISH ONLY — PRODUCTION-GRADE ★
Output between ###PROMPT_START### and ###PROMPT_END###

RULES FOR STEP 4:
- NO vague emotional words (e.g. do NOT write "emotional", "sad", "beautiful" alone).
- ALWAYS translate emotion into acoustic terms:
  BAD: "emotional piano" → GOOD: "felt piano, single-note melody, pp dynamic, 1.4s room reverb, center-panned"
  BAD: "sad strings" → GOOD: "cello section x2, bowed legato at low bow pressure, sustained whole notes, hall reverb 2.0s decay"
  BAD: "soft vocals" → GOOD: "female mezzo-soprano, breathy head voice dominant, close-mic (3–6 inch proximity), no vibrato in verse"
- ALWAYS specify: texture + playing technique + spatial position for every instrument.
- ALWAYS specify register movement for vocals (e.g. "verse: chest voice F3–A3, chorus: mixed voice up to D5")
- ALWAYS specify harmony layer timing (e.g. "1-part harmony enters at 0:52, 2 semitones above lead")
- ALWAYS specify vibrato control (e.g. "no vibrato in verse, light vibrato on held notes in chorus only")
- ALWAYS include mixing depth: frequency focus, headroom, compression ratio, stereo width per element.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROMPT A — SHORTS VERSION (30 seconds) [ENGLISH ONLY]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**[SORIM MUSIC BRIEF — SHORTS 30s]**

GENRE & MOOD CONTEXT:
- Genre: [specific subgenre]
- Acoustic mood translation: [translate emotion → specific sonic descriptors, e.g. "minor key, slow harmonic rhythm, sparse texture, wide dynamic range"]
- BPM: [range, e.g. 66–72]
- Key: [e.g. D minor]
- Time Signature: [e.g. 4/4]

INSTRUMENTATION & SPATIAL MAP (entry timeline):
- 0:00–0:04 | INTRO: [instrument] — [texture], [playing style], [spatial position], [reverb type & decay]
- 0:04–0:08 | LAYER 1: [instrument] enters — [playing technique], [dynamic level pp/mp/mf], [position L/C/R]
- 0:08–0:14 | LAYER 2: [instrument] enters — [texture detail], [articulation], [swell or fade]
- 0:14–0:24 | HOOK PEAK: [full arrangement directive], [percussion entry if any: style + dynamic]
- 0:24–0:30 | RESOLUTION: [decay or sustain instruction], [what remains in final 2s]

DYNAMIC HEADROOM MAP:
- Intro: -18 dBFS (25% intensity) — single element, maximum space
- Build: -14 dBFS (50%) — 2–3 elements, no compression
- Hook: -9 dBFS (85%) — full arrangement, 2:1 bus compression max
- Resolution: -16 dBFS (35%) — natural decay, no limiting

VOCAL PERFORMANCE DIRECTIVE:
- Voice type: [female/male/duet] — [specific range, e.g. mezzo-soprano Eb3–Bb4]
- Register: [chest voice / head voice / mixed] — [when each register is used]
- Breathiness: [level: dry/slightly breathy/breathy] — [specific bars]
- Vibrato: [none in verse / light on sustained notes only / continuous]
- Harmony: [yes/no] — if yes: [interval, entry point in seconds, layer count]
- Mic proximity feel: [close (3–6 inch) / mid (12 inch) / wide]
- Delivery directive: [specific performance instruction, e.g. "open vowel on chorus peak note, no consonant rush"]

PRODUCTION & MIX DEPTH:
- Piano/guitar: [frequency focus, e.g. "low-mids rolled off below 200Hz, presence boost at 3kHz"]
- Vocals: [EQ: high-pass at 120Hz, air shelf +2dB at 12kHz / compression: 3:1 ratio, 10ms attack]
- Strings/pads: [reverb send: hall 2.0s, predelay 20ms / stereo width: 80%]
- Master bus: [warm saturation, soft limiting at -1dBFS, target -14 LUFS integrated]
- Percussion: [none / brush snare: center, -18dBFS / cinematic boom: side-wide, one-shot at hook]

SAFETY: Do NOT imitate any specific artist or copyrighted material. Use general genre aesthetics only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROMPT B — FULL TRACK (2–4 minutes) [ENGLISH ONLY]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**[SORIM MUSIC BRIEF — FULL TRACK]**

GENRE & MOOD CONTEXT:
- Genre: [specific subgenre]
- Acoustic translation: [concrete sonic descriptors only — no vague emotional words]
- BPM: [range — may vary per section, e.g. "68–74, rubato feel in bridge"]
- Key: [primary key] → [modulation key at timestamp]
- Time Signature: [e.g. 4/4 throughout / or shifts]
- Target Duration: [e.g. 3:20–3:40]

FULL SONG STRUCTURE & ARRANGEMENT:
| Timestamp  | Section      | Lead Instrument        | Support Layer              | Intensity | dBFS  |
|------------|--------------|------------------------|----------------------------|-----------|-------|
| 0:00–0:12  | Intro        | [instrument + texture] | [pad or silence]           | 20%       | -20   |
| 0:12–0:40  | Verse 1      | [instrument + style]   | [bass + light perc]        | 38%       | -16   |
| 0:40–0:52  | Pre-Chorus   | [build element]        | [string swell entry]       | 58%       | -13   |
| 0:52–1:20  | Chorus 1     | [full arrangement]     | [all layers + harmony]     | 82%       | -9    |
| 1:20–1:48  | Verse 2      | [richer than V1]       | [added texture]            | 42%       | -15   |
| 1:48–2:00  | Pre-Chorus 2 | [same + extra layer]   | [wider stereo]             | 62%       | -12   |
| 2:00–2:28  | Chorus 2     | [+ 1 harmony layer]    | [wider, fuller]            | 88%       | -8    |
| 2:28–2:48  | Bridge       | [stripped: 1–2 instru] | [silence or breath pad]    | 28%       | -18   |
| 2:48–3:20  | Final Chorus | [key modulation +full] | [orchestral swell]         | 95%       | -6    |
| 3:20–3:40  | Outro        | [single instrument]    | [long tail reverb decay]   | 12%       | -22   |

INSTRUMENTATION DETAIL (texture + technique + position):
- [Instrument 1]: [e.g. "felt piano — weighted keys, single-note RH melody at pp, left-hand sparse block chords, center-panned, 1.2s room reverb"]
- [Instrument 2]: [e.g. "fingerstyle acoustic guitar — thumb-pluck bass strings, finger-roll upper strings, no pick, panned 30% left, 0.8s plate reverb"]
- [Instrument 3]: [e.g. "cello x2 — bowed legato, sul tasto (near fingerboard) for darker tone, whole-note sustained harmony, panned 20% right"]
- [Instrument 4]: [e.g. "ambient string pad — bowed tremolo, filtered above 4kHz, hall reverb 100% wet, stereo width 90%"]
- [Percussion]: [e.g. "none in verse / brush snare on 2&4 from Pre-Chorus / orchestral kick one-shot at Final Chorus bar 1 only"]

KEY MODULATION DIRECTIVE:
- Modulation point: [timestamp, e.g. "2:48 — abrupt half-step modulation from D minor to Eb minor for emotional lift"]
  OR: "No modulation — maintain consistent key throughout for cohesive resolution"

VOCAL PERFORMANCE DIRECTIVE (full track):
- Voice type: [e.g. "female alto, range C3–G4"]
- Verse register: [e.g. "chest voice C3–E3, conversational delivery, no vibrato, dry with room reverb only"]
- Chorus register: [e.g. "mixed voice F3–G4, open vowel on peak notes, light vibrato on held notes >1.5s"]
- Harmony entry: [e.g. "1-part harmony (interval: major 3rd above) enters at Chorus 2 bar 1, fades at Chorus 2 bar 8"]
- Bridge delivery: [e.g. "near-whisper, head voice only, extremely close mic, no effects except subtle reverb"]
- Breath sounds: [keep / edit out] — [rationale]
- Vibrato control: [no vibrato verse → light vibrato chorus → sustained vibrato final note only]

PRODUCTION & MIX DEPTH:
- Piano: high-pass 80Hz, low-mid cut -3dB at 320Hz, presence +2dB at 3.5kHz, gentle compression 2:1
- Acoustic guitar: high-pass 100Hz, air boost +1.5dB at 10kHz, parallel compression 4:1 at 30% blend
- Cello/strings: hall reverb (2.2s decay, predelay 18ms), stereo width 70–80%, no direct signal
- Vocals: high-pass 120Hz, de-esser at 6–8kHz, bus compression 3:1 (8ms attack, 80ms release), -14 LUFS
- Master bus: soft saturation (0.5–1%), transparent limiter ceiling -1dBFS, final target -14 LUFS integrated
- Stereo imaging: piano/vocals center, guitars 30% L&R, strings 60% L&R, pads full wide

SAFETY: Do NOT imitate any specific artist or copyrighted material. Use genre aesthetic references only.

[STEP 5 - MONETIZATION] Korean
Output between ###STRATEGY_START### and ###STRATEGY_END###
2-4 channels + concrete reasoning + Metadata (Title KR+EN, Tags, Description) + Packaging + Pricing

[STEP 6 - SUMMARY] Korean
Output between ###SUMMARY_START### and ###SUMMARY_END###
Clean final summary + next action for user.

FAST MODE: "빠르게" → STEP1(1Q) → STEP3 → STEP4A only
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
