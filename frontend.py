import streamlit as st
import requests
import base64

BACKEND_URL = "http://127.0.0.1:1234"


def main():

    st.set_page_config(
        page_title="AI Voice Journalist",
        page_icon="🎙️",
        layout="centered"
    )

    st.title("🎙️ Personal AI Voice Journalist")
    st.caption("Generate AI-powered audio news briefings from News and Reddit discussions")

    if "topics" not in st.session_state:
        st.session_state.topics = []

    # Initialize a default state string if it doesn't exist yet
    if "latest_summary" not in st.session_state:
        st.session_state.latest_summary = "Your generated news summary will appear here once you click the button below."

    # ======================
    # SIDEBAR
    # ======================

    with st.sidebar:

        st.header("⚙️ Settings")

        source_display = st.selectbox(
            "Data Source",
            ["Both", "News", "Reddit"]
        )

        source_type = source_display.lower()

        st.markdown("---")
        st.info("Maximum 3 topics")

    # ======================
    # TOPIC INPUT
    # ======================

    st.subheader("📰 Topics")

    col1, col2 = st.columns([4, 1])

    with col1:
        new_topic = st.text_input(
            "Enter Topic",
            placeholder="e.g. Artificial Intelligence"
        )

    with col2:

        add_disabled = (
            len(st.session_state.topics) >= 3
            or not new_topic.strip()
        )

        if st.button(
            "Add",
            disabled=add_disabled
        ):
            st.session_state.topics.append(
                new_topic.strip()
            )
            st.rerun()

    # ======================
    # SHOW TOPICS
    # ======================

    if st.session_state.topics:

        st.subheader("Selected Topics")

        for i, topic in enumerate(st.session_state.topics):

            col1, col2 = st.columns([4, 1])

            col1.write(f"✅ {topic}")

            if col2.button(
                "❌",
                key=f"remove_{i}"
            ):
                del st.session_state.topics[i]
                st.rerun()

    st.markdown("---")

    # ======================
    # SHOW SUMMARY (VISIBLE FROM THE START)
    # ======================
    st.subheader("📝 News Briefing Summary")
    
    # Create a persistent placeholder container for the text block
    summary_container = st.empty()
    
    # Render the text block inside the container so it stays permanently visible
    with summary_container:
        st.info(st.session_state.latest_summary)

    # ======================
    # GENERATE AUDIO
    # ======================
    st.subheader("🎧 Audio Generation")

    if st.button(
        "Generate News Audio",
        type="primary",
        disabled=len(st.session_state.topics) == 0
    ):

        with st.spinner(
            "Searching Exa, summarizing with Groq, generating voice..."
        ):

            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate-news-audio",
                    json={
                        "topics": st.session_state.topics,
                        "source_type": source_type
                    },
                    timeout=300
                )

                if response.status_code == 200:
                    
                    data = response.json()
                    summary_text = data.get("summary", "No summary provided.")
                    audio_b64 = data.get("audio_bytes", "")
                    
                    audio_bytes = base64.b64decode(audio_b64)

                    # Update the state and rewrite the container instantly
                    st.session_state.latest_summary = summary_text
                    summary_container.info(summary_text)

                    st.success(
                        "Audio and Summary generated successfully!"
                    )

                    st.write("### 🎵 Play Briefing")
                    st.audio(
                        audio_bytes,
                        format="audio/mpeg"
                    )

                    st.download_button(
                        label="⬇️ Download MP3",
                        data=audio_bytes,
                        file_name="news_summary.mp3",
                        mime="audio/mpeg"
                    )

                else:
                    handle_api_error(response)

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI backend."
                )

            except Exception as e:

                st.error(
                    f"Unexpected Error: {str(e)}"
                )


def handle_api_error(response):

    try:

        error_detail = response.json().get(
            "detail",
            "Unknown error"
        )

        st.error(
            f"API Error ({response.status_code}): {error_detail}"
        )

    except Exception:

        st.error(
            f"Unexpected API Response: {response.text}"
        )


if __name__ == "__main__":
    main()
