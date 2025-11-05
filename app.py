import streamlit as st
import tempfile
import os
import base64
from datetime import datetime
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="AI Video Generator (VEO 3)",
    page_icon="🎬",
    layout="wide"
)

# Title and description
st.title("🎬 AI Video Generator (VEO 3)")
st.markdown(
    "Upload your base video, choose whether to keep its audio, and let AI enhance it with cinematic style and smart captions."
)

def setup_sidebar():
    with st.sidebar:
        st.header("🔧 Configuration")

        api_key = st.text_input("Google AI Studio API Key:", type="password")
        st.markdown("[Get your API key](https://aistudio.google.com/)")

        st.subheader("🎥 Video Settings")
        video_style = st.selectbox(
            "Style",
            ["Realistic", "Cinematic", "Animated", "Artistic", "Documentary", "Fantasy"]
        )
        creativity = st.slider("Creativity", 0.1, 1.0, 0.7)

        st.subheader("🎧 Audio")
        keep_audio = st.radio(
            "Audio preference",
            ["Keep original audio", "Replace with AI-generated soundscape"],
            index=0
        )

        st.subheader("💬 Subtitles")
        add_captions = st.checkbox("Generate AI captions from description", value=True)

        return api_key, {
            "style": video_style,
            "creativity": creativity,
            "keep_audio": keep_audio == "Keep original audio",
            "add_captions": add_captions,
        }

def generate_video_with_options(video_file, user_prompt, settings, api_key):
    """Generate an enhanced video using Gemini VEO 3 with optional audio & captions."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("veo-3")

        # Save the uploaded video temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(video_file.getvalue())
            video_path = tmp.name

        prompt = f"""
        Enhance or recreate this video using the VEO 3 model.

        USER DESCRIPTION: {user_prompt}
        STYLE: {settings['style']}
        CREATIVITY: {settings['creativity']}

        Requirements:
        - Maintain coherence and cinematic flow.
        - {"Keep the original audio track." if settings['keep_audio'] else "Replace original audio with AI-generated soundscape aligned to the mood."}
        - {"Add clear English subtitles summarising or matching the narration and visuals." if settings['add_captions'] else "No subtitles required."}
        """

        with open(video_path, "rb") as f:
            response = model.generate_content(
                [prompt, {"mime_type": "video/mp4", "data": f.read()}],
                request_options={"timeout": 600},
            )

        video_data = response.candidates[0].content.parts[0].inline_data.data
        video_bytes = base64.b64decode(video_data)

        os.remove(video_path)
        return video_bytes

    except Exception as e:
        st.error(f"Gemini VEO 3 API error: {str(e)}")
        return None

def main():
    api_key, settings = setup_sidebar()

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🎬 Upload Base Video")
        video_file = st.file_uploader(
            "Choose a video file",
            type=["mp4", "mov", "avi", "mkv"],
            help="Upload the base video for enhancement"
        )
        if video_file:
            st.video(video_file)
            file_size = len(video_file.getvalue()) / 1024
            st.info(f"File size: {file_size:.1f} KB")

        st.subheader("📝 Video Description")
        video_prompt = st.text_area(
            "Describe how you want the video transformed or styled:",
            placeholder="Describe the look, mood, camera motion, or narrative elements...",
            height=120,
        )

    with col2:
        st.subheader("✨ AI Video Output")

        if video_file and video_prompt:
            if not api_key:
                st.error("🔑 Enter your Google AI Studio API key.")
                return

            if st.button("🚀 Generate Enhanced Video", use_container_width=True):
                with st.spinner("Generating AI-enhanced video..."):
                    output_video = generate_video_with_options(
                        video_file, video_prompt, settings, api_key
                    )
                    if output_video:
                        st.success("✅ Video generated successfully!")
                        st.video(output_video)
                        st.download_button(
                            "📥 Download Generated Video",
                            output_video,
                            file_name=f"generated_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                            mime="video/mp4",
                            use_container_width=True,
                        )
                    else:
                        st.error("❌ Failed to generate video. Try again.")
        else:
            st.info(
                """
                ## 🎯 How to use:
                1. **Upload** a base video.
                2. **Describe** your desired transformation.
                3. **Choose** whether to keep original audio or replace it.
                4. **Optionally add** AI-generated captions.
                5. **Generate** your cinematic video!
                """
            )

if __name__ == "__main__":
    main()
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Powered by Google Gemini VEO 3 • Audio retention & caption overlay supported</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
