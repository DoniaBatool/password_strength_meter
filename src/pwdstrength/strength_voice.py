import streamlit as st
from password_strength import PasswordStats
from streamlit_js_eval import streamlit_js_eval
from gtts import gTTS
import os
import re
import tempfile
from pydub import AudioSegment
import random
import string
import pyperclip

# Set FFmpeg path manually
AudioSegment.converter = r"C:\ffmpeg-7.1-full_build\bin\ffmpeg.exe"

# Function to generate voice feedback file
def generate_voice_feedback(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name  # Return the generated audio file path

def generate_strong_password():
    length = random.randint(12, 16)  # Random password length between 12-16 chars
    characters = (
        string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*"
    )
    return "".join(random.choices(characters, k=length))

# Function to count special characters
def count_special_chars(password):
    return len(re.findall(r'[^A-Za-z0-9]', password))

# **Initialize session state variables**
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

# **Password Input Field with Auto-Update**
password = st.text_input("Enter your password:", type="password", key="password_input")

# **Session update when password changes**
if password and password != st.session_state.password:
    st.session_state.password = password
    stats = PasswordStats(password)
    st.session_state.strength_score = stats.strength()

    # Determine strength level
    if st.session_state.strength_score < 0.3:
        st.session_state.strength_text = "❌ Weak"
        st.session_state.bar_color = "#FF4B4B"  # Red
        st.session_state.suggestion = "Your password is weak. Try adding uppercase letters, numbers, and special symbols."
    elif st.session_state.strength_score < 0.7:
        st.session_state.strength_text = "⚠️ Medium"
        st.session_state.bar_color = "#FFA500"  # Orange
        st.session_state.suggestion = "Your password is medium. Increase length and add special characters."
    else:
        st.session_state.strength_text = "✅ Strong"
        st.session_state.bar_color = "#32CD32"  # Green
        st.session_state.suggestion = "Your password is strong. Keep using secure passwords like this!"

    # **Generate voice feedback file when password changes**
    voice_message = f"{st.session_state.strength_text}. {st.session_state.suggestion}"
    st.session_state.audio_file = generate_voice_feedback(voice_message)

if st.session_state.password:
    # **Display password strength**
    st.markdown(f"**Strength: <span style='color:{st.session_state.bar_color};'>{st.session_state.strength_text}</span>**", unsafe_allow_html=True)

    # **Display password properties**
    stats = PasswordStats(st.session_state.password)
    st.write(f"🛡️ Length: {stats.length}")
    st.write(f"🔑 Contains Letters: {stats.letters > 0}")
    st.write(f"🔢 Contains Numbers: {stats.numbers > 0}")
    special_count = count_special_chars(st.session_state.password)
    st.write(f"🔣 Contains Special Characters: {special_count > 0}")

    # **Improved Progress Bar UI with Solid Colors**
    progress_html = f"""
    <div style="width: 100%; background-color: #ddd; border-radius: 10px; margin-top:10px;">
        <div style="width: {st.session_state.strength_score * 100}%; height: 20px; background-color: {st.session_state.bar_color}; border-radius: 10px;"></div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

    # **Text Feedback**
    st.subheader("📝 Feedback")
    st.write(st.session_state.suggestion)

    # **AI-Suggested Strong Password**
    suggested_password = generate_strong_password()
    st.subheader("🔑 AI-Suggested Strong Password")
    st.code(suggested_password, language="plaintext")

    # **Manual Copy**
    if st.button("📋 Copy to Clipboard"):
        streamlit_js_eval(js_expressions="navigator.clipboard.writeText(`{}`)".format(suggested_password))
        st.success("Copied to clipboard!")
        
    # **Auto-Play Voice Feedback**
    if st.session_state.audio_file:
        st.subheader("🎙️ Voice Feedback")
        st.audio(st.session_state.audio_file, format="audio/mp3", autoplay=True)  # Auto-updates voice feedback

        # **Provide download link**
        with open(st.session_state.audio_file, "rb") as file:
            st.download_button(label="🔊 Download Voice Feedback", data=file, file_name="password_feedback.mp3", mime="audio/mpeg")

else:
    st.info("Enter a password to check its strength.")

