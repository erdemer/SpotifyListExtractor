import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import urllib.parse  # WhatsApp linki için gerekli

# --- AYARLAR ---
CLIENT_ID = st.secrets["SPOTIPY_CLIENT_ID"] if "SPOTIPY_CLIENT_ID" in st.secrets else 'SENIN_CLIENT_ID_BURAYA'
CLIENT_SECRET = st.secrets[
    "SPOTIPY_CLIENT_SECRET"] if "SPOTIPY_CLIENT_SECRET" in st.secrets else 'SENIN_CLIENT_SECRET_BURAYA'
REDIRECT_URI = st.secrets["SPOTIPY_REDIRECT_URI"] if "SPOTIPY_REDIRECT_URI" in st.secrets else 'http://localhost:8501'

st.set_page_config(page_title="Spotify Playlist Yöneticisi", page_icon="🎵", layout="wide")
st.title("🎵 Spotify Playlist Paylaş & İndir")

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
        st.info("Playlistlerini yönetmek için giriş yapmalısın.")
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
    all_playlists = []
    # İlk 50'yi çek
    results = sp.current_user_playlists(limit=50)
    all_playlists.extend(results['items'])

    # Devamı var mı diye bak (Next varsa dönmeye devam et)
    while results['next']:
        results = sp.next(results)
        all_playlists.extend(results['items'])

    return all_playlists


# --- ARAYÜZ (TABS) ---
tab1, tab2 = st.tabs(["📂 Kütüphanem (Tümü)", "🔗 Link Yapıştır"])

selected_playlist_id = None

# SEKME 1: Kendi Listelerin
with tab1:
    st.write("Kütüphanendeki Playlistler (Oluşturdukların & Takip Ettiklerin):")
    try:
        my_playlists = get_user_playlists()

        playlist_options = {}
        for pl in my_playlists:
            if pl:
                display_name = f"{pl['name']} (Sahibi: {pl['owner']['display_name']})"
                playlist_options[display_name] = pl['id']

        # SÖZLÜĞÜ ALFABETİK SIRALA (Bunu ekle)
        sorted_keys = sorted(playlist_options.keys(), key=str.lower)

        # options kısmına sorted_keys veriyoruz
        selected_name = st.selectbox("Bir playlist seç:", options=sorted_keys)

    except Exception as e:
        st.error(f"Listeler yüklenirken hata: {e}")

# SEKME 2: Link Yapıştırma
with tab2:
    link_input = st.text_input("Dışarıdan bir Spotify Playlist Linki:", placeholder="http://...")
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
        results = sp.playlist(selected_playlist_id)
        tracks = results['tracks']['items']

        # Üst Bilgi Alanı
        col1, col2 = st.columns([1, 5])
        with col1:
            if results['images']:
                st.image(results['images'][0]['url'])
        with col2:
            st.header(results['name'])
            st.write(f"Sahibi: **{results['owner']['display_name']}**")
            st.write(f"Toplam Şarkı: **{results['tracks']['total']}**")
            st.caption(results['description'])

        st.divider()

        # İki Kolon: Sol taraf Liste, Sağ taraf Paylaşım Butonları
        col_list, col_actions = st.columns([2, 1])

        # Paylaşılacak Metin İçeriğini Hazırla
        share_list_text = []
        track_data_csv = []  # CSV için veri

        for item in tracks:
            if item['track']:
                t_name = item['track']['name']
                t_artist = item['track']['artists'][0]['name']

                # Paylaşım listesi için metin
                share_list_text.append(f"{t_name} - {t_artist}")

                # CSV için veri
                track_data_csv.append({
                    "Şarkı": t_name,
                    "Sanatçı": t_artist,
                    "Albüm": item['track']['album']['name'],
                    "Süre (ms)": item['track']['duration_ms']
                })

        # --- SOL KOLON: LİSTE ---
        with col_list:
            st.subheader("🎧 Şarkı Listesi")
            for idx, txt in enumerate(share_list_text):
                st.text(f"{idx + 1}. {txt}")

                # --- SAĞ KOLON: AKSİYONLAR (PAYLAŞ & İNDİR) ---
                # --- SAĞ KOLON: AKSİYONLAR (LINK & PAYLAŞ) ---
                with col_actions:
                    st.subheader("🔗 Direkt Link")

                    # 1. Spotify Linkini Al
                    spotify_url = results['external_urls']['spotify']

                    # Linki kopyalanabilir alan olarak göster
                    st.text_input("Spotify Linki:", value=spotify_url)

                    # 2. WhatsApp Butonu (Sadece Linki Paylaşır)
                    # Arkadaşın buna tıklayınca direkt Spotify uygulaması açılır.
                    wa_text = f"Şu listeye bir bak: {results['name']}\n{spotify_url}"
                    encoded_wa_text = urllib.parse.quote(wa_text)

                    st.link_button(
                        "📲 WhatsApp ile Linki Gönder",
                        f"https://wa.me/?text={encoded_wa_text}",
                        type="primary"  # Butonu vurgulu yapar
                    )

                    st.divider()

                    # 3. İstersen yine CSV İndirme butonu durabilir
                    st.subheader("💾 Arşivle")
                    df = pd.DataFrame(track_data_csv)
                    csv = df.to_csv(index=False).encode('utf-8')

                    st.download_button(
                        label="📥 Excel/CSV Olarak İndir",
                        data=csv,
                        file_name=f"{results['name']}.csv",
                        mime="text/csv",
                    )

    except Exception as e:
        st.error(f"Playlist detayları alınamadı. Hata: {e}")
