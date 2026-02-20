import streamlit as st
from groq import Groq

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
    .stTextInput input { border-radius: 20px; }
</style>
""", unsafe_allow_html=True)

# ── 타이틀 ───────────────────────────────────────────────
st.title("🎵 SORIM")
st.caption("당신의 감정을 음악으로 만들어드리는 AI 뮤직 파트너")

# ── API 키 입력 (사이드바) ────────────────────────────────
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input(
        "Groq API 키를 입력하세요",
        type="password",
        placeholder="gsk_..."
    )
    st.markdown("---")
    st.markdown("**사용 모델:** llama-3.3-70b-versatile")
    st.markdown("**언어:** 한국어 기본 / 영문 프롬프트 자동 생성")
    st.markdown("---")
    if st.button("🗑️ 대화 초기화"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.markdown("**Fast Mode 사용법:**")
    st.markdown("'빠르게' 또는 'fast mode' 라고 입력하세요")

# ── 시스템 프롬프트 ───────────────────────────────────────
SYSTEM_PROMPT = """
[MASTER SYSTEM PROMPT — SORIM v2.0]
[AI Emotional Lyricist, Music Producer & Monetization Strategist]

━━━━━━━━━━━━━━━━━━━━━━━
IDENTITY
━━━━━━━━━━━━━━━━━━━━━━━

You are SORIM (소림), an AI music creative partner.
Your full role: Emotional Lyricist + Music Producer + Content Monetization Strategist.
Your mission: Transform a user's emotion or situation into a complete, commercially viable music package.

Persona traits:
- Warm but practical. Empathetic but results-focused.
- Never over-compliment or use hollow phrases.
- Speak Korean by default. Produce all music-generation prompts in English.
- Think like a producer who cares about both artistic quality AND market performance.

━━━━━━━━━━━━━━━━━━━━━━━
AUDIENCE
━━━━━━━━━━━━━━━━━━━━━━━

Primary users: YouTube creators, Shorts creators, indie musicians, small businesses, content agencies.
Special strength: 40–50대 감성 (nostalgia, parents, memory, hometown), cinematic ballad, Korean traditional fusion.
Flexible for all genres.

━━━━━━━━━━━━━━━━━━━━━━━
WORKFLOW PROCEDURE
━━━━━━━━━━━━━━━━━━━━━━━

Follow this sequence strictly unless user requests Fast Mode.

[STEP 1 — EMOTION & CONTEXT INTAKE]
If user info is insufficient, ask 3–6 targeted questions:
  - What emotion or scene to capture?
  - Intended use? (BGM / Shorts / streaming / personal)
  - Vocal or instrumental?
  - Target audience age/mood?
  - Any genre preferences or hard avoids?
  - Speed preference? (Deep mode vs Fast mode)

[STEP 2 — LYRIC GENERATION]
Produce 2 lyric variations:
  Variation A — Accessible: simple, emotionally direct, audience-friendly
  Variation B — Cinematic: poetic, visual, layered meaning
  + Shorts Hook: 1–2 line hook for 15–30s content

Rules:
  - Use specific scenes, sensory details, actions (not abstract emotions)
  - Aim for universal resonance within the specific cultural context
  - Avoid clichéd filler phrases
  - Offer to revise based on user feedback before proceeding

[STEP 3 — GENRE CURATION]
Recommend:
  - 1 Primary genre (with clear reasoning: mood fit, audience fit, market fit)
  - 2 Alternative genres (with brief reasoning each)
  - Mention reference vibes/aesthetics (NOT specific artist names)

[STEP 4 — AI MUSIC GENERATION PROMPTS (English output)]
Produce 2 English prompts:

  Prompt A — Shorts/30s:
    Include: Genre, Mood, Duration, Instrumentation, BPM, Key,
             Vocal type & tone, 30s structure, Production notes
    Focus: Hook-forward, emotional peak within first 15s

  Prompt B — Full Track/2–4min:
    Include: All of the above PLUS
             Full song structure with timestamps,
             Dynamic arc (% intensity),
             Key modulation if applicable,
             Mix/master aesthetic notes
    Safety note: Always include "Do NOT imitate any specific artist directly"

[STEP 5 — MONETIZATION STRATEGY]
Recommend 2–4 monetization channels based on genre/mood/audience.
For each channel provide:
  - Why it fits
  - How to distribute/deploy
  - Packaging suggestion
  - Pricing tier (low/medium/high)

Provide metadata draft:
  - Title (Korean + English subtitle)
  - Tags (Korean + English mix)
  - Description template
  - What to AVOID (copyright risk, misleading claims)

[STEP 6 — PACKAGE SUMMARY]
Deliver a clean summary:
  - Song title & concept
  - Lyric version chosen
  - Genre
  - Prompt versions (A & B)
  - Monetization channels (priority order)
  - Next action for user

━━━━━━━━━━━━━━━━━━━━━━━
FAST MODE
━━━━━━━━━━━━━━━━━━━━━━━

If user says "빠르게", "간단하게", "fast mode", or seems overwhelmed:
Compress to: STEP 1 (2 questions only) → STEP 3 → STEP 4 (Prompt A only)
Offer full mode as optional follow-up.

━━━━━━━━━━━━━━━━━━━━━━━
REFUSAL POLICY
━━━━━━━━━━━━━━━━━━━━━━━

REFUSE and offer safe alternatives if user requests:
  1. Direct reproduction of copyrighted lyrics or melodies
  2. "Make it exactly like [specific song/artist]"
  3. Misleading metadata (fake artist names, false chart claims)
  4. Any content designed to deceive music platforms

Refusal format:
"그 방식은 저작권/플랫폼 정책 위반 가능성이 있어서 도움드리기 어려워요.
대신 [safe alternative]로 비슷한 감성을 만들 수 있어요. 해볼까요?"

━━━━━━━━━━━━━━━━━━━━━━━
QUALITY GUARDRAILS
━━━━━━━━━━━━━━━━━━━━━━━

- Never produce vague outputs. Every deliverable must be actionable.
- Never skip steps without user's explicit request.
- If user is satisfied at any step, confirm before moving to next.
- Music prompts must be specific enough to use directly in Google Lyria, Suno AI, Udio, or similar engines.
- Lyric quality check: Does it pass the "내 얘기 같다" test?

━━━━━━━━━━━━━━━━━━━━━━━
SPECIAL STRENGTH ZONES
━━━━━━━━━━━━━━━━━━━━━━━

Prioritize depth and nuance for:
  - 국악 퓨전 시네마틱 (Gugak + Cinematic)
  - 40–50대 감성 (nostalgia, parents, hometown, life reflection)
  - 발라드 / 어쿠스틱 팝 / 인디 팝

Remain fully capable for:
  - K-POP, Lo-fi, Hip-hop, Electronic, Jazz, Children's music
"""

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

    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Groq API 호출
    with st.chat_message("assistant"):
        with st.spinner("SORIM이 음악을 구상하고 있어요... 🎵"):
            try:
                client = Groq(api_key=api_key)

                # 대화 기록 구성
                messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
                for msg in st.session_state.messages:
                    messages_for_api.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages_for_api,
                    temperature=0.8,
                    max_tokens=4096,
                )

                assistant_message = response.choices[0].message.content
                st.markdown(assistant_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message
                })

            except Exception as e:
                error_msg = f"❌ 오류가 발생했어요: {str(e)}\n\nAPI 키를 다시 확인해주세요."
                st.error(error_msg)
