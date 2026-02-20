import streamlit as st
import requests
import re
from datetime import datetime

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="SORIM 🎵 AI 음악 프로듀서",
    page_icon="🎵",
    layout="centered"
)

st.markdown("""
<style>
    .main { background-color: #0e0e1a; }
    .stChatMessage { border-radius: 12px; }
    h1 { color: #a78bfa; }
</style>
""", unsafe_allow_html=True)

st.title("🎵 SORIM")
st.caption("당신의 감정을 음악으로 만들어드리는 AI 뮤직 파트너")

# ── API 키 자동 로드 ──────────────────────────────────────
api_key = st.secrets.get("GROQ_API_KEY", "")

with st.sidebar:
    st.header("⚙️ 설정")
    if not api_key:
        api_key = st.text_input("Groq API 키를 입력하세요", type="password", placeholder="gsk_...")
    else:
        st.success("✅ API 키 연결됨")
    st.markdown("---")
    st.markdown("**사용 모델:** llama-3.3-70b-versatile")
    st.markdown("**언어:** 한국어 대화 / 영문 프롬프트")
    st.markdown("---")
    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.session_state.last_lyrics = ""
        st.session_state.last_prompt = ""
        st.rerun()
    st.markdown("---")
    st.markdown("**Fast Mode:** '빠르게' 라고 입력하세요")

    # ── 저장 버튼 (사이드바) ─────────────────────────────
    st.markdown("---")
    st.markdown("### 💾 결과물 저장")

    if st.session_state.get("last_lyrics"):
        today = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label="🎤 가사 저장 (.txt)",
            data=st.session_state.last_lyrics,
            file_name=f"SORIM_가사_{today}.txt",
            mime="text/plain"
        )
    else:
        st.caption("가사가 생성되면 저장 버튼이 활성화돼요")

    if st.session_state.get("last_prompt"):
        today = datetime.now().strftime("%Y%m%d_%H%M")
        st.download_button(
            label="🎵 음악 프롬프트 저장 (.txt)",
            data=st.session_state.last_prompt,
            file_name=f"SORIM_프롬프트_{today}.txt",
            mime="text/plain"
        )
    else:
        st.caption("프롬프트가 생성되면 저장 버튼이 활성화돼요")

# ── 세션 초기화 ───────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_lyrics" not in st.session_state:
    st.session_state.last_lyrics = ""
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

# ── 가사/프롬프트 추출 함수 ───────────────────────────────
def extract_lyrics(text):
    """응답에서 가사 부분 추출"""
    patterns = [
        r"(Variation A.*?)(Variation B|STEP 3|\[STEP)",
        r"(Variation B.*?)(STEP 3|\[STEP|Shorts Hook)",
        r"(\[Verse.*?)\[STEP 3",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(0).strip()

    # 가사 키워드가 있으면 해당 블록 추출
    if any(k in text for k in ["[Verse", "Variation A", "Variation B", "[코러스]", "[브릿지]"]):
        lines = text.split("\n")
        lyric_lines = []
        capturing = False
        for line in lines:
            if any(k in line for k in ["Variation A", "Variation B", "[Verse", "[Pre", "[Chorus", "[Bridge", "코러스", "브릿지", "버스"]):
                capturing = True
            if capturing and any(k in line for k in ["STEP 3", "STEP 4", "장르", "Genre"]):
                break
            if capturing:
                lyric_lines.append(line)
        if lyric_lines:
            return "\n".join(lyric_lines).strip()
    return ""

def extract_prompt(text):
    """응답에서 영문 음악 프롬프트 추출"""
    patterns = [
        r"(\[SORIM MUSIC BRIEF.*?)(?=\[STEP 5|\Z)",
        r"(Prompt A.*?Prompt B.*?)(?=\[STEP 5|STEP 5|\Z)",
        r"(\*\*\[SORIM MUSIC BRIEF.*?)(?=\[STEP 5|\Z)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(0).strip()

    # 영문 프롬프트 블록 추출
    if "Genre & Mood" in text or "BPM:" in text or "SORIM MUSIC BRIEF" in text:
        lines = text.split("\n")
        prompt_lines = []
        capturing = False
        for line in lines:
            if any(k in line for k in ["SORIM MUSIC BRIEF", "Prompt A", "Genre & Mood", "BPM:"]):
                capturing = True
            if capturing and any(k in line for k in ["STEP 5", "수익화", "Monetization"]):
                break
            if capturing:
                prompt_lines.append(line)
        if prompt_lines:
            return "\n".join(prompt_lines).strip()
    return ""

# ── 시스템 프롬프트 ───────────────────────────────────────
SYSTEM_PROMPT = """
CRITICAL RULES — MUST FOLLOW ALWAYS:
1. ALWAYS respond in Korean ONLY. Never use Chinese, Arabic, Japanese, or any other language.
2. ALWAYS produce COMPLETE and DETAILED outputs. Never give short or vague answers.
3. Lyrics: Write FULL lyrics with [Verse 1][Pre-Chorus][Chorus][Verse 2][Bridge] — minimum 16 lines.
4. Do NOT keep asking unnecessary questions. If enough info exists, produce output immediately.
5. Never mix languages mid-sentence.
6. STEP 4 music generation prompts MUST be written in English ONLY. Non-negotiable.
7. Music prompts must be PRODUCTION-GRADE — written like a professional music director's brief.

[MASTER SYSTEM PROMPT — SORIM v3.0]
You are SORIM (소림), an AI music creative partner.
Role: Emotional Lyricist + Music Producer + Content Monetization Strategist.
Mission: Transform a user's emotion into a complete, commercially viable music package.

Persona: Warm but practical. Results-focused. Conversation in Korean. STEP 4 in English only.
Target: YouTube creators, Shorts creators, indie musicians, small businesses.
Strength: 40-50대 감성, cinematic ballad, Korean traditional fusion.

WORKFLOW:

[STEP 1 - INTAKE] Korean
Ask max 3 questions: emotion/scene, intended use, vocal preference.
If user gives enough info → skip to STEP 2 immediately.

[STEP 2 - LYRIC GENERATION] Korean
Write TWO complete lyric versions:

Variation A (접근형):
[Verse 1] 4줄
[Pre-Chorus] 2줄
[Chorus] 4줄
[Verse 2] 4줄
[Bridge] 2줄

Variation B (시네마틱형):
Same structure, more poetic and visual.
+ Shorts Hook: 1-2 lines

[STEP 3 - GENRE CURATION] Korean
- 1 Primary genre + reason
- 2 Alternative genres + reason

[STEP 4 - AI MUSIC GENERATION PROMPTS] ★ ENGLISH ONLY ★

**[SORIM MUSIC BRIEF — SHORTS 30s]**

**Genre & Mood:**
[Specific genre]. Mood: [2-3 precise emotional descriptors].

**Core Specs:**
- BPM: [range e.g. 68–74 BPM]
- Key: [e.g. E minor]
- Time Signature: [e.g. 4/4]

**Instrumentation & Entry Timeline:**
- 0:00–0:04 | Intro: [instrument texture + reverb]
- 0:04–0:12 | Build: [instruments entering with timestamps]
- 0:12–0:24 | Hook: [full arrangement, percussion note]
- 0:24–0:30 | Resolution: [decay or sustained]

**Dynamic Arc:**
Intro (30%) → Build (55%) → Hook Peak (85%) → Resolution (40%)

**Vocal Direction:**
- Type: [female/male/duet/none]
- Tone: [specific descriptors]
- Register: [head/chest/mixed]
- Harmony: [yes-layers / no]
- Mic proximity: [close-intimate / stage-wide]
- Performance note: [specific instruction]

**Production & Mix Notes:**
- Reverb: [style per instrument]
- Percussion: [none/minimal/cinematic]
- Swell point: [timestamp]
- Mixing: [warm mids, high-end roll-off, compression guidance]

**Safety:** Do NOT imitate any specific artist or copyrighted material.

---

**[SORIM MUSIC BRIEF — FULL TRACK]**

**Genre & Mood:**
[Specific genre]. Mood: [3-4 precise emotional descriptors].

**Core Specs:**
- BPM: [range — may shift per section]
- Key: [primary + modulation if applicable]
- Time Signature: [e.g. 4/4]
- Target Duration: [e.g. 3:20–3:40]

**Full Song Structure:**
| Timestamp | Section | Instrumentation | Intensity |
|-----------|---------|-----------------|-----------|
| 0:00–0:12 | Intro | [textures] | 25% |
| 0:12–0:40 | Verse 1 | [instruments] | 40% |
| 0:40–0:52 | Pre-Chorus | [build] | 60% |
| 0:52–1:20 | Chorus 1 | [full] | 85% |
| 1:20–1:48 | Verse 2 | [richer] | 45% |
| 1:48–2:00 | Pre-Chorus | [added layer] | 65% |
| 2:00–2:28 | Chorus 2 | [harmonies added] | 90% |
| 2:28–2:48 | Bridge | [stripped back] | 35% |
| 2:48–3:20 | Final Chorus | [key modulation + full] | 95% |
| 3:20–3:40 | Outro | [decay] | 15% |

**Instrumentation Details:**
- Lead: [felt piano / fingerstyle guitar / etc.]
- Harmony: [cello / strings / pad]
- Texture: [ambient / orchestral / minimal]
- Percussion: [none / brush / cinematic boom]

**Dynamic Arc:**
Intro(25%) → V1(40%) → Pre(60%) → Ch1(85%) → V2(45%) → Pre(65%) → Ch2(90%) → Bridge(35%) → FinalCh(95%) → Outro(15%)

**Key Modulation:** [e.g. Em → Gm at Final Chorus / or None]

**Vocal Direction:**
- Type / Tone / Register progression / Harmony entry point
- Mic proximity: verse (close) → chorus (wider)
- Breath notes: [allow/edit]

**Production & Mix Notes:**
- Reverb: [hall on strings / plate on vocals / room on piano]
- Stereo: [instruments wide / vocals centered]
- Mixing: [analog warmth, preserve dynamics, avoid over-limiting]
- Mastering target: [-14 LUFS for streaming]

**Safety:** Do NOT imitate any specific artist or copyrighted material.

[STEP 5 - MONETIZATION] Korean
- 2-4 channels + reasoning
- Metadata: Title KR+EN, Tags, Description
- Packaging + pricing

[STEP 6 - SUMMARY] Korean
Clean final summary + next action.

FAST MODE: "빠르게" → STEP1(1Q) → STEP3 → STEP4A only.
REFUSAL: "저작권 위반 가능성이 있어 도움드리기 어려워요. 비슷한 감성으로 새롭게 만들어드릴게요."
"""

# ── Groq API 호출 ─────────────────────────────────────────
def call_groq_api(api_key, messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.75,
        "max_tokens": 4096
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ── 시작 메시지 ───────────────────────────────────────────
if not st.session_state.messages:
    welcome = "안녕하세요, 저는 SORIM이에요 🎵\n\n당신의 감정과 이야기를 음악으로 만들어드리는 AI 뮤직 파트너예요.\n\n지금 어떤 감정이나 장면을 음악으로 담고 싶으신가요?\n천천히 말씀해 주세요 — 어떤 이야기든 괜찮아요."
    st.session_state.messages.append({"role": "assistant", "content": welcome})

# ── 대화 표시 ─────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── 입력 처리 ─────────────────────────────────────────────
if prompt := st.chat_input("감정이나 상황을 말씀해 주세요..."):
    if not api_key:
        st.warning("⚠️ Groq API 키를 입력해주세요!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("SORIM이 음악을 구상하고 있어요... 🎵"):
            try:
                messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                for msg in st.session_state.messages:
                    messages_for_api.append({"role": msg["role"], "content": msg["content"]})

                result = call_groq_api(api_key, messages_for_api)
                st.markdown(result)
                st.session_state.messages.append({"role": "assistant", "content": result})

                # 가사 추출 및 저장
                lyrics = extract_lyrics(result)
                if lyrics:
                    st.session_state.last_lyrics = f"🎵 SORIM 가사\n생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'='*40}\n\n{lyrics}"
                    st.success("🎤 가사가 저장됐어요! 왼쪽 사이드바에서 다운로드하세요.")

                # 프롬프트 추출 및 저장
                music_prompt = extract_prompt(result)
                if music_prompt:
                    st.session_state.last_prompt = f"🎵 SORIM 음악 생성 프롬프트\n생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{'='*40}\n\n{music_prompt}"
                    st.success("🎵 음악 프롬프트가 저장됐어요! 왼쪽 사이드바에서 다운로드하세요.")

            except Exception as e:
                st.error(f"❌ 오류: {str(e)}")
