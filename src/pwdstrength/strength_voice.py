import streamlit as st
from password_strength import PasswordStats
from gtts import gTTS
import os
import re
import tempfile
from pydub import AudioSegment
import random
import string

# Set FFmpeg path manually
AudioSegment.converter = r"C:\ffmpeg-7.1-full_build\bin\ffmpeg.exe"

def generate_voice_feedback(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

def generate_strong_password():
    length = random.randint(12, 16)
    characters = (
        string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*"
    )
    return "".join(random.choices(characters, k=length))

def count_special_chars(password):
    return len(re.findall(r'[^A-Za-z0-9]', password))

# **Session State Variables**
if "password" not in st.session_state:
    st.session_state.password = ""
if "strength_score" not in st.session_state:
    st.session_state.strength_score = 0
if "strength_text" not in st.session_state:
    st.session_state.strength_text = "❌ Weak"
if "bar_color" not in st.session_state:
    st.session_state.bar_color = "#FF4B4B"
if "suggestion" not in st.session_state:
    st.session_state.suggestion = "Your password is weak. Try adding uppercase letters, numbers, and special symbols."
if "audio_file" not in st.session_state:
    st.session_state.audio_file = None

# Streamlit UI
st.title("🔒 Password Strength Meter with Auto-Play Voice Feedback")

password = st.text_input("Enter your password:", type="password", key="password_input", on_change=None)


if password:
    if password != st.session_state.password:
        st.session_state.password = password
        stats = PasswordStats(password)
        st.session_state.strength_score = stats.strength()

        if st.session_state.strength_score < 0.3:
            st.session_state.strength_text = "❌ Weak"
            st.session_state.bar_color = "#FF4B4B"
            st.session_state.suggestion = "Your password is weak. Try adding uppercase letters, numbers, and special symbols."
        elif st.session_state.strength_score < 0.7:
            st.session_state.strength_text = "⚠️ Medium"
            st.session_state.bar_color = "#FFA500"
            st.session_state.suggestion = "Your password is medium. Increase length and add special characters."
        else:
            st.session_state.strength_text = "✅ Strong"
            st.session_state.bar_color = "#32CD32"
            st.session_state.suggestion = "Your password is strong. Keep using secure passwords like this!"

        voice_message = f"{st.session_state.strength_text}. {st.session_state.suggestion}"
        st.session_state.audio_file = generate_voice_feedback(voice_message)


        

# **Display UI if password exists**
if st.session_state.password:
    st.markdown(f"**Strength: <span style='color:{st.session_state.bar_color};'>{st.session_state.strength_text}</span>**", unsafe_allow_html=True)

    stats = PasswordStats(st.session_state.password)
    st.write(f"🛡️ Length: {stats.length}")
    st.write(f"🔑 Contains Letters: {stats.letters > 0}")
    st.write(f"🔢 Contains Numbers: {stats.numbers > 0}")
    special_count = count_special_chars(st.session_state.password)
    st.write(f"🔣 Contains Special Characters: {special_count > 0}")

    progress_html = f"""
    <div style="width: 100%; background-color: #ddd; border-radius: 10px; margin-top:10px;">
        <div style="width: {st.session_state.strength_score * 100}%; height: 20px; background-color: {st.session_state.bar_color}; border-radius: 10px;"></div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

    st.subheader("📝 Feedback")
    st.write(st.session_state.suggestion)

    suggested_password = generate_strong_password()
    st.subheader("🔑 AI-Suggested Strong Password")
    st.code(suggested_password, language="plaintext")

    if st.session_state.audio_file:
        st.subheader("🎙️ Voice Feedback")
        st.audio(st.session_state.audio_file, format="audio/mp3", autoplay=True)

        with open(st.session_state.audio_file, "rb") as file:
            st.download_button(label="🔊 Download Voice Feedback", data=file, file_name="password_feedback.mp3", mime="audio/mpeg")

else:
    st.info("Enter a password to check its strength.")
    
if st.button("🔄 Refresh"):
    st.experimental_rerun()
