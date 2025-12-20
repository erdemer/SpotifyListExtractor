import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# --- AYARLAR ---
# Güvenlik notu: Gerçek projede bunları environment variable'dan (.env) çekmelisin.
CLIENT_ID = 'f2a3c3e646bb4a6994ab78e6ebbca954'
CLIENT_SECRET = 'd3a67fcddc3041bab7bb6d4804f821f3'
REDIRECT_URI = 'http://localhost:8501'

# Sayfa Yapılandırması
st.set_page_config(page_title="Spotify Playlist Paylaş", page_icon="🎵")

st.title("🎵 Playlist Önizleyici & Paylaş")

# --- LOGIN & AUTH AKIŞI ---
# SpotifyOAuth, token yönetimini ve refresh işlemlerini otomatik yapar.
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-library-read"  # Kullanıcı verisi okumak için gerekli izin
)

# Login kontrolü
if 'token_info' not in st.session_state:
    # URL'deki parametreleri kontrol et (Spotify'dan dönerken code getirir)
    query_params = st.query_params
    code = query_params.get("code")

    if code:
        # Kod varsa token al
        token_info = sp_oauth.get_access_token(code)
        st.session_state['token_info'] = token_info
        # URL'i temizle (tekrar login döngüsüne girmesin)
        st.query_params.clear()
        st.rerun()
    else:
        # Token yoksa Login butonu göster
        auth_url = sp_oauth.get_authorize_url()
        st.link_button("Spotify ile Giriş Yap", auth_url)
        st.stop()  # Login olmadan aşağıyı çalıştırma

# Giriş yapıldıysa Spotify objesini oluştur
token = st.session_state['token_info']['access_token']
sp = spotipy.Spotify(auth=token)

st.success("Giriş Başarılı! ✅")

# --- ANA AKIŞ ---

# 1. Playlist Linki Al
playlist_url = st.text_input("Spotify Playlist Linkini Yapıştır:", placeholder="https://open.spotify.com/playlist/...")

if playlist_url:
    try:
        # Playlist verilerini çek
        results = sp.playlist(playlist_url)
        tracks = results['tracks']['items']

        st.divider()
        st.subheader(f"🎶 {results['name']}")
        st.write(f"Tarafından: {results['owner']['display_name']} | Toplam {results['tracks']['total']} şarkı")

        # Paylaşılabilir Metin Oluşturma Listesi
        share_list = []

        # Şarkıları Listele
        for item in tracks:
            track = item['track']
            if track:
                col1, col2, col3 = st.columns([1, 4, 2])

                with col1:
                    # Albüm Kapağı
                    if track['album']['images']:
                        st.image(track['album']['images'][0]['url'], width=60)

                with col2:
                    st.write(f"**{track['name']}**")
                    st.caption(f"{track['artists'][0]['name']}")

                with col3:
                    # Önizleme (Preview)
                    # NOT: Spotify çoğu şarkı için preview_url desteğini kesti.
                    if track['preview_url']:
                        st.audio(track['preview_url'], format="audio/mp3")
                    else:
                        st.caption("Önizleme Yok")

                share_list.append(f"{track['name']} - {track['artists'][0]['name']}")

        st.divider()

        # --- PAYLAŞMA BÖLÜMÜ ---
        st.subheader("📤 Arkadaşınla Paylaş")

        # Basit metin formatında liste oluştur
        share_text = f"Bu playliste bir bak: {results['name']}\n\n" + "\n".join(
            share_list[:10]) + "\n...\nVe daha fazlası!"

        st.text_area("Kopyalanabilir Liste:", value=share_text, height=150)

        # WhatsApp Paylaş Butonu (Web Link)
        import urllib.parse

        encoded_text = urllib.parse.quote(share_text)
        st.link_button("WhatsApp ile Gönder", f"https://wa.me/?text={encoded_text}")

    except Exception as e:
        st.error(f"Hata oluştu. Linki kontrol et. Hata: {e}")