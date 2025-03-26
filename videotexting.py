import streamlit as st
import moviepy as mp
import speech_recognition as sr
import tempfile
import os
import soundfile as sf
from textblob import TextBlob
import sys

print("Using Python version:", sys.version)


st.set_page_config(page_title="Video to Text Converter", page_icon="🎮")

st.title("🎮 Video to Text Converter")
st.write("Upload a video file and get its transcription")

# File uploader
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov", "mkv"])

if uploaded_file is not None:
    # Create a temporary file
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    video_path = tfile.name
    tfile.close()
    
    # Display video
    st.video(uploaded_file)
    
    # Process button
    if st.button("Transcribe Video"):
        with st.spinner('Processing video...'):
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Extract audio from video
            status_text.text("Extracting audio from video...")
            video = mp.VideoFileClip(video_path)
            
            # Create temp audio file
            temp_audio_path = os.path.join(tempfile.gettempdir(), "temp_audio.wav")
            video.audio.write_audiofile(temp_audio_path, codec='pcm_s16le', fps=16000, logger=None)
            progress_bar.progress(40)
            
            # Close video file before deletion
            video.close()
            
            # Verify audio file format
            try:
                data, samplerate = sf.read(temp_audio_path, dtype='int16')
                if len(data) == 0:
                    st.error("Extracted audio is empty. Please use a video with clear audio.")
                else:
                    # Transcribe audio
                    status_text.text("Transcribing audio to text...")
                    recognizer = sr.Recognizer()
                    
                    with sr.AudioFile(temp_audio_path) as source:
                        audio_data = recognizer.record(source)
                        try:
                            progress_bar.progress(70)
                            status_text.text("Finalizing transcription...")
                            text = recognizer.recognize_google(audio_data, language='en-GB')
                            progress_bar.progress(100)
                            status_text.text("Transcription complete!")
                            
                            # Improve grammar and punctuation
                            text = TextBlob(text).correct()
                            
                            # Display transcription
                            st.subheader("Transcription")
                            st.write(text)
                            
                            # Download option
                            st.download_button(
                                label="Download Transcription",
                                data=str(text),
                                file_name="transcription.txt",
                                mime="text/plain"
                            )
                            
                        except sr.UnknownValueError:
                            st.error("Speech Recognition could not understand the audio")
                        except sr.RequestError as e:
                            st.error(f"Could not request results from Speech Recognition service; {e}")
            except Exception as e:
                st.error(f"Error reading audio file: {e}")
            
            # Clean up temp files
            os.unlink(video_path)
            os.unlink(temp_audio_path)
    
    st.info("Note: For longer videos, the transcription process may take some time. The free Google Speech Recognition API works best with clear audio and English language.")

else:
    st.info("Please upload a video file to get started")

# Add some usage instructions
with st.expander("How to use"):
    st.write("""
    1. Upload a video file using the file uploader above
    2. Click the 'Transcribe Video' button
    3. Wait for the processing to complete
    4. View the transcription and download if needed
    
    For best results:
    - Use videos with clear audio
    - Shorter videos process faster
    - The default transcription works best with English language
    """)
