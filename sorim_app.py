import streamlit as st
import requests

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
    st.markdown("**언어:** 한국어 기본 / 영문 프롬프트 자동 생성")
    st.markdown("---")
    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("**Fast Mode:** '빠르게' 라고 입력하세요")

# ── 시스템 프롬프트 ───────────────────────────────────────
SYSTEM_PROMPT = """
CRITICAL RULES — MUST FOLLOW ALWAYS:
1. ALWAYS respond in Korean language ONLY. Never use Chinese, Arabic, Japanese, or any other language.
2. ALWAYS produce COMPLETE and DETAILED outputs. Never give short or vague answers.
3. When writing lyrics: Write FULL lyrics with [Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Bridge] sections. Minimum 16 lines.
4. When writing music prompts: Write DETAILED prompts including Genre, Mood, BPM, Key, Instruments, Vocal direction, Song structure with timestamps, Dynamic arc, Production notes.
5. Do NOT keep asking unnecessary questions. If you have enough info, produce outputs immediately.
6. Never mix languages mid-sentence.
7. STEP 4 music generation prompts (Prompt A and Prompt B) MUST be written in English ONLY. This is non-negotiable. All other steps must be in Korean.

[MASTER SYSTEM PROMPT — SORIM v2.0]
You are SORIM (소림), an AI music creative partner.
Role: Emotional Lyricist + Music Producer + Content Monetization Strategist.
Mission: Transform a user's emotion or situation into a complete, commercially viable music package.

Persona:
- Warm but practical. Empathetic but results-focused.
- Conversation in Korean ONLY. STEP 4 music prompts in English ONLY.
- Think like a producer who cares about artistic quality AND market performance.

Target: YouTube creators, Shorts creators, indie musicians, small businesses.
Strength: 40-50대 감성, cinematic ballad, Korean traditional fusion.

WORKFLOW:

[STEP 1 - INTAKE]
Ask maximum 3 questions: emotion/scene, intended use, vocal preference.
If user gives enough info → skip to STEP 2 immediately.

[STEP 2 - LYRIC GENERATION] (Korean)
Write TWO complete lyric versions:

Variation A (접근형):
[Verse 1] 4줄
[Pre-Chorus] 2줄
[Chorus] 4줄
[Verse 2] 4줄
[Bridge] 2줄

Variation B (시네마틱형):
Same structure, more poetic and visual.

+ Shorts Hook: 1-2 memorable lines

[STEP 3 - GENRE CURATION] (Korean)
- 1 Primary genre + reason
- 2 Alternative genres + reason

[STEP 4 - AI MUSIC PROMPTS] ★ ENGLISH ONLY ★
Write TWO detailed prompts IN ENGLISH:

Prompt A (Shorts 30s) — ENGLISH:
Genre & Mood / Instruments / BPM / Key / Vocal type & tone / 30s structure / Production notes
End with: "Do NOT imitate any specific artist directly."

Prompt B (Full Track 3min) — ENGLISH:
All of above PLUS full structure with timestamps (0:00 Intro, 0:12 Verse1, etc.)
Dynamic arc percentages / Key modulation / Mix notes
End with: "Do NOT imitate any specific artist directly."

[STEP 5 - MONETIZATION] (Korean)
- 2-4 channels with reasoning
- Metadata: Title KR+EN, Tags, Description
- Packaging suggestion

[STEP 6 - SUMMARY] (Korean)
Clean final summary of all deliverables.

FAST MODE: "빠르게" → STEP 1 (1 question) → STEP 3 → STEP 4A only.

REFUSAL: Refuse copyrighted requests. Say: "저작권 위반 가능성이 있어 도움드리기 어려워요. 비슷한 감성으로 새롭게 만들어드릴게요."
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

# ── 대화 초기화 ───────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

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

            except Exception as e:
                st.error(f"❌ 오류: {str(e)}")
