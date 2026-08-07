import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="LingoAI Tutor", page_icon="🗣️", layout="wide")
st.title("🗣️ LingoAI Tutor")
st.caption("Your interactive AI language conversation & grammar partner")

# Load API Key securely from secrets or sidebar fallback
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Enter Gemini API Key:", type="password")

with st.sidebar:
    st.header("⚙️ Configuration")
    
    target_lang = st.selectbox(
        "Target Language:",
        ["Spanish", "French", "German", "Japanese", "Mandarin", "Tamil", "Hindi", "Italian"]
    )
    
    proficiency = st.select_slider(
        "Proficiency Level:",
        options=["Beginner (A1/A2)", "Intermediate (B1/B2)", "Advanced (C1/C2)"]
    )
    
    mode = st.radio(
        "Practice Mode:",
        ["Free Conversation", "Grammar & Vocabulary Feedback", "Roleplay Scenario"]
    )

SYSTEM_INSTRUCTION = f"""
You are LingoAI, an expert, encouraging, and highly interactive language tutor.
The user wants to practice {target_lang} at a {proficiency} level.
Current practice mode: {mode}.

Guidelines:
1. Respond primarily in {target_lang}, matched to the user's proficiency level.
2. Provide a brief English translation in brackets or underneath when helpful.
3. If the user makes a grammar or vocabulary mistake, gently offer a correction in an accordion or separate line.
4. End your responses with a follow-up question in {target_lang} to keep the conversation going smoothly.
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Say something in your target language..."):
    if not api_key:
        st.error("Missing Gemini API Key! Please configure secrets.toml or enter it in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        client = genai.Client(api_key=api_key)
        
        contents = [
            types.Content(
                role=msg["role"],
                parts=[types.Part.from_text(text=msg["content"])]
            )
            for msg in st.session_state.messages
        ]

        with st.chat_message("assistant"):
            with st.spinner("LingoAI is thinking..."):
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.7
                    )
                )
                
                bot_reply = response.text
                st.markdown(bot_reply)

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    except Exception as e:
        st.error(f"Error connecting to Gemini API: {str(e)}")
