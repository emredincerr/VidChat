import streamlit as st
import raghelper
import videohelper

if "current_video_url" not in st.session_state:
    st.session_state.current_video_url = None
    st.session_state.current_transcript_docs = []
    st.session_state.videos = []
    
st.set_page_config(page_title="VidChat Youtube ile Sohbet", layout="centered")
st.image(image="./img/app_banner.png")
st.header("VidChat: Youtube ile Sohbet!")
st.divider()

tab_urls, tab_search = st.tabs(["URL Girerek", "Arama Yaparak"])

with tab_urls:
    
    video_url = st.text_input(label="YouTube Video Adresini Giriniz:", key="url_video_url")
    prompt = st.text_input(label="Sorunuzu Giriniz:", key="url_prompt")
    submit_btn = st.button(label="Sor", key="url_btn")
    
    if submit_btn:
        st.video(data=video_url)
        st.divider()
        if st.session_state.current_video_url != video_url:
            with st.spinner(text="AŞAMA-1: Video metni hazırlanıyor..."):
                transcript_docs = videohelper.get_video_transkript(url=video_url)
                st.session_state.current_transcript_docs = transcript_docs
        st.success("Video transkripti ön belleğe kaydedildi!")
        st.divider()
        st.session_state.current_video_url = video_url
        
        with st.spinner("AŞAMA-2: Sorunuz yanıtlanıyor..."):
            AI_Response, relevant_documents = raghelper.rag_with_video_transcript(transcript_docs=transcript_docs, prompt=prompt)
        st.info("YANIT:")
        st.markdown(AI_Response)
        st.divider()
        
        for doc in relevant_documents:
            st.warning("REFERANS:")
            st.caption(doc.page_content)
            st.markdown(f"Kaynak: {doc.metadata}")
            st.divider()
        

with tab_search:
    
    col_left, col_center, col_right = st.columns([20,1,10])

    with col_left:

        st.subheader("Video Arama İşlemleri")
        st.divider()
        search_term = st.text_input(label="Aramak İstediğiniz Sözcükleri Giriniz:", key="search_term")
        video_count = st.slider(label="Sonuç Sayısı", min_value=1, max_value=5, value=5, key="search_video_count")
        sorting_options = ["En İlgili", "Tarihe Göre", "İzlenme Sayısı", "Beğeni Sayısı"]
        sorting_criteria = st.selectbox(label="Sıralama Ölçütü", options=sorting_options)
        search_btn = st.button(label="Video Ara", key="search_button")
        st.divider()

        if search_btn:
            st.session_state.videos = []
            videolist = videohelper.get_videos_for_search_term(search_term=search_term, video_count=video_count, sorting_criteria=sorting_criteria)
            
            for video in videolist:
                st.session_state.videos.append(video)
            
        video_urls = []
        video_titles = {}
        for video in st.session_state.videos:
            video_urls.append(video.video_url)
            video_titles.update({video.video_url:video.video_title})

        selected_video = st.selectbox(
            label="Sohbet Etmek İstediğiniz Videoyu Seçiniz:",
            options=video_urls,
            format_func=lambda url: video_titles[url],
            key="search_selectbox"
        )
            
        if selected_video:
            search_prompt = st.text_input(label="Sorunuzu Giriniz:", key="search_prompt")
            search_ask_btn = st.button(label="Sor", key="search_ask_button")

            if search_ask_btn:
                st.caption("Seçtiğiniz Video")
                st.video(data=selected_video)
                st.divider()
                    
                if st.session_state.current_video_url != selected_video:
                    with st.spinner("AŞAMA-1: Video metni hazırlanıyor..."):
                        video_transcript_docs = videohelper.get_video_transcript(url=selected_video)
                        st.session_state.current_transcript_docs = video_transcript_docs
                    st.success("Video transkripti ön belleğe kaydedildi!")
                    st.divider()
                    st.session_state.current_video_url = selected_video
            

                with st.spinner("AŞAMA-2: Sorunuz yanıtlanıyor..."):
                    AI_Response, relevant_documents = raghelper.rag_with_video_transcript(transcript_docs=st.session_state.current_transcript_docs, prompt=search_prompt)
                st.info("YANIT:")
                st.markdown(AI_Response)
                st.divider()

                for doc in relevant_documents:
                    st.warning("REFERANS:")
                    st.caption(doc.page_content)
                    st.markdown(f"Kaynak: {doc.metadata}")
                    st.divider()

    with col_center:
        st.empty()

    with col_right:

        st.subheader("İlgili Videolar")
        st.divider()

        for i, video in enumerate(st.session_state.videos):
            st.info(f"Video No: {i+1}")
            st.video(data=video.video_url)
            st.caption(f"Video Başlığı: {video.video_title}")
            st.caption(f"Kanal: {video.channel_name}")
            st.caption(f"Video Süresi: {video.duration}")
            st.divider()  