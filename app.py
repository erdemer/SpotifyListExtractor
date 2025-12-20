import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import urllib.parse

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Spotify Playlist Manager",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS (THEME & ANIMATIONS) ---
st.markdown("""
<style>
    /* MAIN BACKGROUND */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    
    /* TEXT COLORS & FONTS */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, [data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .stCaption {
        color: #B3B3B3 !important;
    }

    /* INPUT FIELDS */
    .stTextInput input {
        background-color: #282828 !important;
        color: white !important;
        border: 1px solid #282828 !important;
        border-radius: 20px !important;
        padding: 10px 15px !important;
    }
    .stTextInput input:focus {
        border-color: #1DB954 !important;
        box-shadow: none !important;
    }
    .stTextInput label {
        color: #B3B3B3 !important;
    }
    
    /* SELECT BOX */
    .stSelectbox > div > div {
        background-color: #282828 !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
    }
    
    /* STANDARD BUTTONS */
    .stButton > button {
        background-color: #1DB954 !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        padding: 0.5rem 2rem !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        background-color: #1ED760 !important;
        transform: scale(1.05);
        color: white !important;
    }
    
    /* DOWNLOAD BUTTON SPECIAL STYLE */
    [data-testid="stDownloadButton"] > button {
        background-color: #282828 !important;
        color: #FFFFFF !important;
        border: 1px solid #B3B3B3 !important;
        border-radius: 50px !important;
        width: 100%;
        transition: all 0.3s ease !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        border-color: #1DB954 !important;
        color: #1DB954 !important;
        background-color: #121212 !important;
    }

    /* LINKS (WhatsApp etc) */
    a {
        color: #1DB954 !important;
        text-decoration: none;
    }

    /* PRIMARY CUSTOM LINKS (Like WhatsApp Button) */
    a[kind="primary"] {
        background-color: #282828 !important;
        border: 1px solid #1DB954 !important;
        color: #1DB954 !important;
        border-radius: 50px !important;
        transition: all 0.3s ease !important;
        text-decoration: none !important;
        padding: 10px 20px !important;
        display: inline-block !important;
    }
    a[kind="primary"]:hover {
        background-color: #1DB954 !important;
        color: black !important;
        transform: translateY(-2px);
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        color: #B3B3B3;
        font-weight: bold;
        padding-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #1DB954;
        border-bottom: 3px solid #1DB954;
    }

    /* DIVIDER */
    hr {
        border-color: #282828;
    }

    /* CARDS / CONTAINERS */
    .css-1r6slb0, .stExpander {
        background-color: #181818;
        border-radius: 8px;
        border: none;
    }
    
    /* CUSTOM TRACK ROW STYLE */
    .track-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px;
        background-color: #181818;
        border-radius: 4px;
        margin-bottom: 5px;
        transition: background-color 0.2s;
    }
    .track-row:hover {
        background-color: #282828;
    }
    .track-info {
        display: flex;
        flex-direction: column;
    }
    .track-name {
        font-weight: bold;
        color: white;
        font-size: 1rem;
    }
    .track-artist {
        font-size: 0.85rem;
        color: #B3B3B3;
    }

</style>
""", unsafe_allow_html=True)


# --- CONFIG & SECRETS ---
try:
    CLIENT_ID = st.secrets.get("SPOTIPY_CLIENT_ID", 'SENIN_CLIENT_ID_BURAYA')
    CLIENT_SECRET = st.secrets.get("SPOTIPY_CLIENT_SECRET", 'SENIN_CLIENT_SECRET_BURAYA')
    REDIRECT_URI = st.secrets.get("SPOTIPY_REDIRECT_URI", 'http://localhost:8501')
except Exception:
    st.error("Secrets bulunamadı. Lütfen .streamlit/secrets.toml dosyasını kontrol et.")
    st.stop()

# --- HEADER ---
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg", width=60)
with col_title:
    st.title("Spotify Playlist Manager")
    st.caption("Playlists, made fancy.")

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
        try:
            token_info = sp_oauth.get_access_token(code)
            st.session_state['token_info'] = token_info
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Giriş hatası: {e}")
            st.stop()
    else:
        auth_url = sp_oauth.get_authorize_url()
        st.markdown(
            f"""
            <div style="text-align: center; margin-top: 50px; padding: 40px; background: #181818; border-radius: 10px;">
                <h3>Hoş Geldin! 👋</h3>
                <p style="color:#B3B3B3;">Playlistlerini yönetmek, indirmek ve paylaşmak için giriş yapmalısın.</p>
                <br>
                <a href="{auth_url}" target="_self" style="background-color: #1DB954; color: white; padding: 12px 30px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.1em; transition: 0.3s;">
                    Spotify ile Giriş Yap
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.stop()

token = st.session_state['token_info']['access_token']
sp = spotipy.Spotify(auth=token)


# --- FUNCTIONS ---
def get_playlist_id_from_link(url):
    if "playlist/" in url:
        try:
            part1 = url.split("playlist/")[1]
            return part1.split("?")[0]
        except:
            return None
    return None

@st.cache_data(ttl=300)
def get_user_playlists():
    all_playlists = []
    results = sp.current_user_playlists(limit=50)
    all_playlists.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        all_playlists.extend(results['items'])
    return all_playlists


# --- MAIN INTERFACE ---
tab1, tab2 = st.tabs(["📂 Library", "🔗 Paste Link"])
selected_playlist_id = None

with tab1:
    try:
        my_playlists = get_user_playlists()
        playlist_options = {}
        for pl in my_playlists:
            if pl:
                display_name = f"{pl['name']} • {pl['owner']['display_name']}"
                playlist_options[display_name] = pl['id']

        sorted_keys = sorted(playlist_options.keys(), key=str.lower)
        
        st.markdown("##### 🎧 Select a Playlist")
        contact_selected = st.selectbox("Search your library...", options=sorted_keys, label_visibility="collapsed")
        
        if contact_selected:
            selected_playlist_id = playlist_options[contact_selected]

    except Exception as e:
        st.error(f"Error loading library: {e}")

with tab2:
    st.markdown("##### 🔗 Import from Link")
    link_input = st.text_input("Paste Spotify Playlist URL", placeholder="https://open.spotify.com/playlist/...")
    if link_input:
        parsed_id = get_playlist_id_from_link(link_input)
        if parsed_id:
            selected_playlist_id = parsed_id
        else:
            st.error("Invalid Spotify Link")


# --- DISPLAY RESULTS ---
if selected_playlist_id:
    try:
        results = sp.playlist(selected_playlist_id)
        tracks = results['tracks']['items']

        st.markdown("<br>", unsafe_allow_html=True)
        
        # HERO SECTION
        with st.container():
            col_img, col_data = st.columns([1.5, 4])
            with col_img:
                if results['images']:
                    st.image(results['images'][0]['url'], use_container_width=True)
            with col_data:
                st.markdown(f"<h1 style='margin-bottom:0;'>{results['name']}</h1>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#B3B3B3; font-size:1.1em;'>By {results['owner']['display_name']}</p>", unsafe_allow_html=True)
                st.markdown(f"**{results['tracks']['total']} tracks**")
                if results['description']:
                    st.caption(results['description'])

        st.divider()

        # CONTENT AREA
        col_list, col_actions = st.columns([2, 1.2])

        # PREPARE DATA
        share_list_text = []
        track_data_csv = []
        
        for item in tracks:
            if item.get('track'):
                track = item['track']
                t_name = track['name']
                t_artist = track['artists'][0]['name']
                t_album = track['album']['name'] if 'album' in track else ""
                
                share_list_text.append(f"{t_name} - {t_artist}")
                track_data_csv.append({
                    "Title": t_name,
                    "Artist": t_artist,
                    "Album": t_album,
                    "Duration (ms)": track['duration_ms']
                })

        # --- LEFT: TRACK LIST ---
        with col_list:
            st.subheader("🎵 Tracks")
            with st.container(height=500):
                for idx, item in enumerate(tracks):
                    if item.get('track'):
                        tr = item['track']
                        # Custom HTML Row for better look
                        st.markdown(
                            f"""
                            <div class="track-row">
                                <div class="track-info">
                                    <span class="track-name">{idx + 1}. {tr['name']}</span>
                                    <span class="track-artist">{tr['artists'][0]['name']}</span>
                                </div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )

        # --- RIGHT: ACTIONS ---
        with col_actions:
            st.container()
            with st.container():
                st.subheader("🚀 Actions")
                
                # Link Section
                spotify_url = results['external_urls']['spotify']
                st.text_input("Direct Spotify Link", value=spotify_url)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # ZIP / Share
                wa_text = f"Check out this playlist: {results['name']}\n{spotify_url}"
                encoded_wa_text = urllib.parse.quote(wa_text)
                
                st.markdown(f"""
                <a href="https://wa.me/?text={encoded_wa_text}" target="_blank" kind="primary" style="text-align:center; width:100%;">
                   📲 Share on WhatsApp
                </a>
                """, unsafe_allow_html=True)
                
                st.markdown("<br><br>", unsafe_allow_html=True)

                # Export Section
                st.write("**Archives**")
                df = pd.DataFrame(track_data_csv)
                csv = df.to_csv(index=False).encode('utf-8')
                
                st.download_button(
                    label="⬇️ Download as CSV",
                    data=csv,
                    file_name=f"{results['name']}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    except Exception as e:
        st.error(f"Could not load playlist details. Error: {e}")
