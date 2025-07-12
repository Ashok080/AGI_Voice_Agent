import streamlit as st
import os
import openai
import requests

# Optional: ElevenLabs (for voice) + D-ID (for video)
from elevenlabs import generate, set_api_key, stream

# --- Load API keys from Streamlit Secrets ---
openai.api_key = st.secrets["OPENAI_API_KEY"]
set_api_key(st.secrets["ELEVENLABS_API_KEY"])
D_ID_API_KEY = st.secrets.get("D_ID_API_KEY", None)

# --- Streamlit UI ---
st.set_page_config(page_title="🤖 AGI Voice Agent Suite", layout="wide")
st.title("🤖 AGI Voice Agent Suite")
st.markdown("Preview, run, and talk to your AGI notebooks.")

# --- List AGI notebooks in repo ---
notebooks = [f for f in os.listdir() if f.endswith(".ipynb") and f.startswith("agi")]

selected_nb = st.selectbox("📘 Select AGI Notebook", sorted(notebooks))

if selected_nb:
    st.subheader(f"📖 Preview: `{selected_nb}`")
    with open(selected_nb, "r", encoding="utf-8") as f:
        code = f.read()
    st.code(code[:2000] + "\n...", language="json")

    colab_link = f"https://colab.research.google.com/github/YOUR_USERNAME/AGI_Voice_Agent/blob/main/{selected_nb}"
    st.markdown(f"🔗 [Open in Google Colab]({colab_link})")

# --- GPT AGI Prompt Input ---
st.divider()
st.subheader("💬 Ask AGI a Question")
user_input = st.text_input("🗣️ Type your question to AGI", placeholder="e.g. What does AGI1 notebook do?")

if st.button("🔮 Run AGI Prompt"):
    with st.spinner("Thinking..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_input}],
        )
        answer = response.choices[0].message.content
        st.success("✅ AGI Answer:")
        st.write(answer)

        # --- Convert to Voice with ElevenLabs ---
        st.audio(generate(text=answer, voice="Rachel"), format="audio/mp3")

        # --- Generate D-ID Video (optional) ---
        if D_ID_API_KEY:
            st.info("📽️ Generating D-ID talking face video...")

            payload = {
                "script": {"type": "text", "input": answer},
                "source_url": "https://create-images-results.d-id.com/default-character.png"
            }
            headers = {
                "Authorization": f"Bearer {D_ID_API_KEY}",
                "Content-Type": "application/json"
            }

            res = requests.post("https://api.d-id.com/talks", json=payload, headers=headers)
            if res.ok:
                talk_id = res.json().get("id")
                video_url = f"https://talks.d-id.com/{talk_id}.mp4"
                st.video(video_url)
            else:
                st.error("D-ID video failed.")
