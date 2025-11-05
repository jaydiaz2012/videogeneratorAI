import streamlit as st
import tempfile
import os
import base64
import json
from datetime import datetime
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Title and description
st.title("🎬 AI Video Generator (VEO 3)")
st.markdown("Upload your base video and generate an enhanced AI video using Google’s VEO 3 model.")

def setup_sidebar():
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key
        api_key = st.text_input("Google AI Studio API Key:", type="password")
        st.markdown("[Get your API key](https://aistudio.google.com/)")
        
        # Video settings
        st.subheader("🎥 Video Settings")
        video_style = st.selectbox(
            "Style",
            ["Realistic", "Cinematic", "Animated", "Artistic", "Documentary", "Fantasy"]
        )
        
        st.subheader("🎨 Advanced")
        creativity = st.slider("Creativity", 0.1, 1.0, 0.7)
        
        return api_key, {
            "style": video_style,
            "creativity": creativity
        }

def generate_video_from_uploaded(video_file, user_prompt, settings, api_key):
    """Generate a new video using Gemini VEO 3 model based on the uploaded video and prompt"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("veo-3")  # Updated model for video generation
        
        # Save uploaded video temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(video_file.getvalue())
            video_path = tmp.name

        # Generate AI-enhanced video using the uploaded one as reference
        prompt = f"""
        Enhance or recreate this video based on the description below.
        
        USER DESCRIPTION: {user_prompt}
        STYLE: {settings['style']}
        CREATIVITY: {settings['creativity']}
        
        Make it visually compelling and cohesive with cinematic flow.
        """

        with open(video_path, "rb") as f:
            response = model.generate_content(
                [prompt, {"mime_type": "video/mp4", "data": f.read()}],
                request_options={"timeout": 600}
            )

        # Get generated video data
        video_data = response.candidates[0].content.parts[0].inline_data.data
        video_bytes = base64.b64decode(video_data)
        
        # Clean up
        os.remove(video_path)

        return video_bytes

    except Exception as e:
        st.error(f"Gemini VEO 3 API error: {str(e)}")
        return None

def main():
    # Setup sidebar
    api_key, settings = setup_sidebar()
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🎬 Upload Base Video")
        video_file = st.file_uploader(
            "Choose a video file",
            type=['mp4', 'mov', 'avi', 'mkv'],
            help="Upload the base video to enhance or transform"
        )
        
        if video_file:
            st.video(video_file)
            file_size = len(video_file.getvalue()) / 1024  # KB
            st.info(f"File size: {file_size:.1f} KB")
        
        st.subheader("📝 Video Description")
        video_prompt = st.text_area(
            "Describe how you want to transform or enhance the video:",
            placeholder="Describe the desired look, mood, pacing, or transformation...",
            height=120,
            help="This guides how the AI modifies or enhances your uploaded video."
        )

    with col2:
        st.subheader("✨ AI Video Output")
        
        if video_file and video_prompt:
            if not api_key:
                st.error("🔑 Please enter your Google AI Studio API key")
                return
                
            if st.button("🚀 Generate Enhanced Video", use_container_width=True):
                with st.spinner("Generating AI-enhanced video..."):
                    generated_video = generate_video_from_uploaded(
                        video_file,
                        video_prompt,
                        settings,
                        api_key
                    )
                    
                    if generated_video:
                        st.success("✅ Video generated successfully!")
                        
                        # Display the generated video
                        st.video(generated_video)
                        
                        # Download button
                        st.download_button(
                            "📥 Download Generated Video",
                            generated_video,
                            file_name=f"generated_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                            mime="video/mp4",
                            use_container_width=True
                        )
                    else:
                        st.error("❌ Failed to generate video. Please try again.")
        
        elif not video_file:
            st.info("""
            ## 🎯 How to use:
            1. **Upload** your base video (MP4, MOV, etc.)
            2. **Describe** how you want it transformed or styled
            3. **Enter** your Google AI Studio API key
            4. **Generate** your enhanced video!
            
            ### Example ideas:
            - Add cinematic colour grading  
            - Turn real footage into animation  
            - Stylise as documentary or fantasy
            """)

# Run
if __name__ == "__main__":
    main()
    
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>Powered by Google Gemini VEO 3 • Generates enhanced videos from uploaded clips</p>
        </div>
        """,
        unsafe_allow_html=True
    )
