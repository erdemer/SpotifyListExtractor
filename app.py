import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# --- AYARLAR ---
# Streamlit Cloud'da secrets, lokalde string
CLIENT_ID = st.secrets["SPOTIPY_CLIENT_ID"] if "SPOTIPY_CLIENT_ID" in st.secrets else 'SENIN_CLIENT_ID_BURAYA'
CLIENT_SECRET = st.secrets[
    "SPOTIPY_CLIENT_SECRET"] if "SPOTIPY_CLIENT_SECRET" in st.secrets else 'SENIN_CLIENT_SECRET_BURAYA'
REDIRECT_URI = st.secrets["SPOTIPY_REDIRECT_URI"] if "SPOTIPY_REDIRECT_URI" in st.secrets else 'http://localhost:8501'

st.set_page_config(page_title="Spotify Exportify Clone", page_icon="🎵")
st.title("🎵 Spotify Playlist Yöneticisi")

# --- LOGIN & AUTH ---
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="playlist-read-private playlist-read-collaborative user-library-read"
)

if 'token_info' not in st.session_state:
    query_params = st.query_params
    code = query_params.get("code")
    if code:
        token_info = sp_oauth.get_access_token(code)
        st.session_state['token_info'] = token_info
        st.query_params.clear()
        st.rerun()
    else:
        auth_url = sp_oauth.get_authorize_url()
        st.info("Playlistlerini görmek için giriş yapmalısın.")
        st.link_button("Spotify ile Giriş Yap", auth_url)
        st.stop()

token = st.session_state['token_info']['access_token']
sp = spotipy.Spotify(auth=token)


# --- FONKSİYONLAR ---
def get_playlist_id_from_link(url):
    if "playlist/" in url:
        part1 = url.split("playlist/")[1]
        return part1.split("?")[0]
    return None


def get_user_playlists():
    # Kullanıcının ilk 50 playlistini çeker
    results = sp.current_user_playlists(limit=50)
    return results['items']


# --- ARAYÜZ (TABS) ---
tab1, tab2 = st.tabs(["📂 Listelerimden Seç", "🔗 Link Yapıştır"])

selected_playlist_id = None

# SEKME 1: Kendi Listelerin
with tab1:
    st.write("Hesabındaki playlistler (İlk 50):")
    try:
        my_playlists = get_user_playlists()

        # Selectbox için sözlük oluşturuyoruz: {Playlist Adı : ID}
        # Not: Aynı isimde iki playlist varsa sonuncusunu alır, basitlik için böyle bıraktım.
        playlist_options = {pl['name']: pl['id'] for pl in my_playlists}

        selected_name = st.selectbox("Bir playlist seç:", options=playlist_options.keys())

        if selected_name:
            selected_playlist_id = playlist_options[selected_name]
            st.caption(f"Seçilen ID: {selected_playlist_id}")

    except Exception as e:
        st.error(f"Listeler yüklenirken hata oluştu: {e}")

# SEKME 2: Link Yapıştırma
with tab2:
    link_input = st.text_input("Spotify Playlist Linki:", placeholder="http://...")
    if link_input:
        parsed_id = get_playlist_id_from_link(link_input)
        if parsed_id:
            selected_playlist_id = parsed_id
        else:
            st.warning("Geçersiz Link Formatı")

# --- SONUÇLARI GÖSTERME ALANI ---
st.divider()

if selected_playlist_id:
    try:
        # Seçilen ID ne olursa olsun (Tab1 veya Tab2'den gelen) burada işlenir
        results = sp.playlist(selected_playlist_id)
        tracks = results['tracks']['items']

        col_h1, col_h2 = st.columns([1, 4])
        with col_h1:
            if results['images']:
                st.image(results['images'][0]['url'])
        with col_h2:
            st.header(results['name'])
            st.write(f"Sahibi: **{results['owner']['display_name']}** | Toplam Şarkı: **{results['tracks']['total']}**")

        # Tablo veya Liste Gösterimi
        st.subheader("🎵 Şarkı Listesi")

        # Basit liste görünümü
        for idx, item in enumerate(tracks):
            track = item['track']
            if track:
                st.text(f"{idx + 1}. {track['name']} - {track['artists'][0]['name']}")

        # CSV İndirme Butonu (Exportify Özelliği)
        import pandas as pd

        # Veriyi DataFrame'e çevir
        track_data = []
        for item in tracks:
            if item['track']:
                track_data.append({
                    "Track Name": item['track']['name'],
                    "Artist": item['track']['artists'][0]['name'],
                    "Album": item['track']['album']['name'],
                    "Duration (ms)": item['track']['duration_ms']
                })

        df = pd.DataFrame(track_data)
        csv = df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="📥 Bu Listeyi CSV (Excel) Olarak İndir",
            data=csv,
            file_name=f"{results['name']}.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Playlist yüklenemedi: {e}")