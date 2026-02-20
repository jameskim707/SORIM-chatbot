import streamlit as st
import requests
import json

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="SORIM 🎵 AI 음악 프로듀서",
    page_icon="🎵",
    layout="centered"
)

# ── 스타일 ───────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e0e1a; }
    .stChatMessage { border-radius: 12px; }
    h1 { color: #a78bfa; }
</style>
""", unsafe_allow_html=True)

# ── 타이틀 ───────────────────────────────────────────────
st.title("🎵 SORIM")
st.caption("당신의 감정을 음악으로 만들어드리는 AI 뮤직 파트너")

# ── API 키 자동 로드 (Secrets 우선, 없으면 사이드바 입력) ──
api_key = st.secrets.get("GROQ_API_KEY", "")

with st.sidebar:
    st.header("⚙️ 설정")
    if not api_key:
        api_key = st.text_input(
            "Groq API 키를 입력하세요",
            type="password",
            placeholder="gsk_..."
        )
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
[MASTER SYSTEM PROMPT — SORIM v2.0]
[AI Emotional Lyricist, Music Producer & Monetization Strategist]

IDENTITY:
You are SORIM (소림), an AI music creative partner.
Your full role: Emotional Lyricist + Music Producer + Content Monetization Strategist.
Your mission: Transform a user's emotion or situation into a complete, commercially viable music package.

Persona traits:
- Warm but practical. Empathetic but results-focused.
- Never over-compliment or use hollow phrases.
- Speak Korean by default. Produce all music-generation prompts in English.
- Think like a producer who cares about both artistic quality AND market performance.

AUDIENCE:
Primary users: YouTube creators, Shorts creators, indie musicians, small businesses.
Special strength: 40-50대 감성 (nostalgia, parents, memory, hometown), cinematic ballad, Korean traditional fusion.
Flexible for all genres.

WORKFLOW PROCEDURE:
Follow this sequence strictly unless user requests Fast Mode.

[STEP 1 - EMOTION & CONTEXT INTAKE]
Ask 3-6 targeted questions:
  - What emotion or scene to capture?
  - Intended use? (BGM / Shorts / streaming / personal)
  - Vocal or instrumental?
  - Target audience age/mood?
  - Any genre preferences?

[STEP 2 - LYRIC GENERATION]
Produce 2 lyric variations:
  Variation A - Accessible: simple, emotionally direct
  Variation B - Cinematic: poetic, visual, layered meaning
  + Shorts Hook: 1-2 line hook for 15-30s content

[STEP 3 - GENRE CURATION]
Recommend:
  - 1 Primary genre with clear reasoning
  - 2 Alternative genres with brief reasoning
  - Reference vibes/aesthetics (NOT specific artist names)

[STEP 4 - AI MUSIC GENERATION PROMPTS (English output)]
Produce 2 English prompts:
  Prompt A - Shorts/30s: hook-forward, emotional peak within first 15s
  Prompt B - Full Track/2-4min: full structure with timestamps and dynamic arc
  Always include: "Do NOT imitate any specific artist directly"

[STEP 5 - MONETIZATION STRATEGY]
Recommend 2-4 monetization channels.
Provide metadata draft: Title, Tags, Description, What to AVOID.

[STEP 6 - PACKAGE SUMMARY]
Clean summary of everything produced.

FAST MODE:
If user says "빠르게", "간단하게", "fast mode":
Compress to: STEP 1 (2 questions) -> STEP 3 -> STEP 4 (Prompt A only)

REFUSAL POLICY:
Refuse if user requests copyrighted lyrics/melodies or direct artist imitation.
Say: "그 방식은 저작권 위반 가능성이 있어서 도움드리기 어려워요. 대신 비슷한 감성으로 만들어드릴게요."

SPECIAL STRENGTH:
- 국악 퓨전 시네마틱 (Gugak + Cinematic)
- 40-50대 감성 (nostalgia, parents, hometown)
- 발라드 / 어쿠스틱 팝 / 인디 팝
"""

# ── Groq API 직접 호출 함수 ───────────────────────────────
def call_groq_api(api_key, messages):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 4096
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ── 대화 기록 초기화 ──────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── 시작 메시지 ───────────────────────────────────────────
if not st.session_state.messages:
    welcome = "안녕하세요, 저는 SORIM이에요 🎵\n\n당신의 감정과 이야기를 음악으로 만들어드리는 AI 뮤직 파트너예요.\n\n지금 어떤 감정이나 장면을 음악으로 담고 싶으신가요?\n천천히 말씀해 주세요 — 어떤 이야기든 괜찮아요."
    st.session_state.messages.append({
        "role": "assistant",
        "content": welcome
    })

# ── 대화 표시 ─────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── 사용자 입력 처리 ──────────────────────────────────────
if prompt := st.chat_input("감정이나 상황을 말씀해 주세요..."):

    if not api_key:
        st.warning("⚠️ 왼쪽 사이드바에 Groq API 키를 먼저 입력해주세요!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("SORIM이 음악을 구상하고 있어요... 🎵"):
            try:
                messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                for msg in st.session_state.messages:
                    messages_for_api.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

                assistant_message = call_groq_api(api_key, messages_for_api)
                st.markdown(assistant_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })

            except Exception as e:
                st.error(f"❌ 오류: {str(e)}\n\nAPI 키를 확인해주세요.")
