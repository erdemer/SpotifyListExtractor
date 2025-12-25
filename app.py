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
    /* MAIN BACKGROUND WITH GRADIENT */
    .stApp {
        background: linear-gradient(to bottom right, #121212, #000000);
        color: #FFFFFF;
    }
    
    /* TEXT COLORS & FONTS */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stText, [data-testid="stMarkdownContainer"] {
        color: #FFFFFF !important;
        font-family: 'Circular', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    .stCaption {
        color: #B3B3B3 !important;
    }

    /* CARDS FOR SEARCH RESULTS */
    .playlist-card {
        background-color: #181818;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        transition: transform 0.2s, background-color 0.2s;
        cursor: pointer;
        height: 100%;
        border: 1px solid #282828;
    }
    .playlist-card:hover {
        background-color: #282828;
        transform: translateY(-5px);
        border-color: #1DB954;
    }
    .playlist-card img {
        border-radius: 4px;
        margin-bottom: 10px;
        width: 100%;
        object-fit: cover;
        aspect-ratio: 1/1;
    }
    .playlist-title {
        font-weight: bold;
        font-size: 0.9rem;
        margin-bottom: 5px;
        white-space: nowrap; 
        overflow: hidden;
        text-overflow: ellipsis; 
        display: block;
    }
    .playlist-owner {
        font-size: 0.8rem;
        color: #B3B3B3;
    }

    /* INPUT FIELDS */
    .stTextInput input {
        color: white !important;
    }
    div[data-baseweb="input"] {
        background-color: #282828 !important;
        border: 1px solid #282828 !important;
        border-radius: 50px !important;
        padding: 5px 10px !important;
    }
    div[data-baseweb="base-input"] {
        background-color: transparent !important;
    }
    .stTextInput input:focus {
        box-shadow: none !important;
    }
    div[data-baseweb="input"]:focus-within {
        border-color: #1DB954 !important;
        box-shadow: 0 0 0 1px #1DB954 !important;
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
    
    /* BUTTONS */
    .stButton > button {
        background-color: #1DB954 !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 2rem !important;
        transition: all 0.2s ease !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        background-color: #1ED760 !important;
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(29, 185, 84, 0.3);
    }
    .stButton > button:active {
        transform: scale(0.98);
    }

    /* DOWNLOAD BUTTON */
    [data-testid="stDownloadButton"] > button {
        background-color: transparent !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        border-radius: 50px !important;
        width: 100%;
        transition: all 0.3s ease !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        border-color: #1DB954 !important;
        color: #1DB954 !important;
        background-color: rgba(29, 185, 84, 0.1) !important;
    }

    /* TAB STYLING */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        color: #B3B3B3;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #1DB954;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
        border-right: 1px solid #282828;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    /* EXPANDER STYLING */
    [data-testid="stExpander"] {
        background-color: #181818 !important;
        border: 1px solid #282828 !important;
        border-radius: 8px !important;
        color: white !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: #1DB954 !important;
    }
    [data-testid="stExpander"] summary svg {
        fill: white !important;
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


# --- LOGIN & AUTH ---
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    # Scopes: playlist access (read/write), user library, follow status, etc.
    scope="playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private user-library-read user-read-private user-follow-read"
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
            st.error(f"SignIn Error: {e}")
            st.stop()
    else:
        auth_url = sp_oauth.get_authorize_url()
        # Fancy Login Page
        st.markdown(
            f"""
            <div style="height: 80vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg" width="100" style="margin-bottom: 20px;">
                <h1 style="font-size: 3rem; margin-bottom: 10px;">Spotify Manager</h1>
                <p style="color:#B3B3B3; font-size: 1.2rem; margin-bottom: 40px;">Manage, Export, and Share your playlists with style.</p>
                <a href="{auth_url}" target="_blank" style="background-color: #1DB954; color: white; padding: 15px 40px; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.2rem; transition: 0.3s; box-shadow: 0 4px 15px rgba(29, 185, 84, 0.4);">
                    Login with Spotify
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.stop()

token = st.session_state['token_info']['access_token']
sp = spotipy.Spotify(auth=token)

# --- DUAL TOKEN SUTUP ---
# User requested: Use main token for WRITING (sp), but allow an external token (Exportify) for READING (sp_read).
external_token = st.session_state.get('external_token')
if external_token:
    sp_read = spotipy.Spotify(auth=external_token)
    st.toast("Using External Token for Fetching Data", icon="🔓")
else:
    sp_read = sp


# --- FUNCTIONS ---
def get_playlist_id_from_link(url):
    if "playlist/" in url:
        try:
            part1 = url.split("playlist/")[1]
            return part1.split("?")[0]
        except:
            return None
    return None

def get_user_playlists():
    """Fetch all playlists from the user's library.
    
    Note: "Made For You" playlists (Discover Weekly, Release Radar, etc.) 
    will only appear if the user has followed/liked them in Spotify.
    """
    all_playlists = []
    fetch_log = []  # Debug log
    
    try:
        # First request
        results = sp_read.current_user_playlists(limit=50)
        total_from_api = results.get('total', 0)
        all_playlists.extend(results['items'])
        fetch_log.append(f"First fetch: Got {len(results['items'])} items, API says total={total_from_api}")
        
        # Pagination
        page_num = 1
        while results['next']:
            results = sp_read.next(results)
            page_num += 1
            all_playlists.extend(results['items'])
            fetch_log.append(f"Page {page_num}: Got {len(results['items'])} more items")
        
        fetch_log.append(f"Final count: {len(all_playlists)} playlists fetched (API said {total_from_api})")
        
        # Store log in session state for display
        st.session_state['fetch_log'] = fetch_log
        st.session_state['api_total'] = total_from_api
        
    except Exception as e:
        st.error(f"Error fetching library: {e}")
        import traceback
        st.session_state['fetch_log'] = [f"ERROR: {str(e)}", traceback.format_exc()]
            
    return all_playlists


# --- APP HEADER (Small) ---
with st.sidebar:
    st.image("https://storage.googleapis.com/pr-newsroom-wp/1/2018/11/Spotify_Logo_RGB_Green.png", width=150)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("Made by **Erdem Er**")
    
    st.markdown("---")
    if st.button("Refresh Playlists", use_container_width=True):
        # Clear any cached data
        if 'fetch_log' in st.session_state:
            del st.session_state['fetch_log']
        if 'api_total' in st.session_state:
            del st.session_state['api_total']
        st.rerun()
    
    if st.button("🚪 Logout / Reset", use_container_width=True):
        if 'token_info' in st.session_state:
            del st.session_state['token_info']
        if 'selected_search_id' in st.session_state:
            del st.session_state['selected_search_id']
        if 'external_token' in st.session_state:
            del st.session_state['external_token']
        st.rerun()

    st.markdown("---")
    with st.expander("🔓 Token Hack (Reader Mode)"):
        st.info("Paste a 'Read-Only' token (e.g. from Exportify) here. We will use it to **FETCH** playlists, but use your main login to **CREATE** them.")
        external_token_input = st.text_input("External Access Token", type="password", help="Paste Exportify token here.")
        
        if st.button("Inject Read Token", use_container_width=True, type="primary"):
            if external_token_input:
                st.session_state['external_token'] = external_token_input
                st.success("Read token injected! Reloading...")
                import time
                time.sleep(1)
                st.rerun()
        
        if st.button("Clear External Token", use_container_width=True):
            if 'external_token' in st.session_state:
                del st.session_state['external_token']
                st.rerun()


# --- MAIN INTERFACE ---
tab1, tab2, tab3 = st.tabs(["📂 Library", "🔍 Search", "🔗 Paste Link"])
selected_playlist_id = None

# TAB 1: LIBRARY
with tab1:
    try:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Info banner for "Made For You" playlists
        st.info(
            "💡 **Can't find 'Discover Weekly' or other personalized playlists?**\n\n"
            "Due to Spotify API limitations, personalized playlists only appear here if you've followed them. "
            "To access them:\n"
            "1. Open the playlist in Spotify\n"
            "2. Click the ♡ (heart) or 'Follow' button\n"
            "3. Refresh this page"
        )
        
        my_playlists = get_user_playlists()
        
        # Debug information
        spotify_owned = [pl for pl in my_playlists if pl and pl['owner']['id'] == 'spotify']
        user_owned = [pl for pl in my_playlists if pl and pl['owner']['id'] != 'spotify']
        
        # Debug information (Internal only, not displayed)
        spotify_owned = [pl for pl in my_playlists if pl and pl['owner']['id'] == 'spotify']
        user_owned = [pl for pl in my_playlists if pl and pl['owner']['id'] != 'spotify']

        
        # Build playlist options
        playlist_options = {}
        for pl in my_playlists:
            if pl:
                display_name = f"{pl['name']} • {pl['owner']['display_name']}"
                playlist_options[display_name] = pl['id']

        sorted_keys = sorted(playlist_options.keys(), key=str.lower)
        
        st.markdown("### Your Library")
        contact_selected = st.selectbox("Select a playlist", options=sorted_keys, label_visibility="collapsed")
        
        if contact_selected:
            selected_playlist_id = playlist_options[contact_selected]

    except Exception as e:
        st.error(f"Error loading library: {e}")

# TAB 2: SEARCH (Visual Grid)
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Search Spotify")
    
    col_search, col_btn = st.columns([5, 1])
    with col_search:
        search_query = st.text_input("Search", placeholder="Playlists, Moods, Genres...", label_visibility="collapsed")
    with col_btn:
        search_clicked = st.button("GO", use_container_width=True)

    # Quick Access Buttons
    st.markdown("<p style='font-size:0.9rem; color:#B3B3B3; margin-top:20px;'>Quick Access (Official):</p>", unsafe_allow_html=True)
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    
    auto_search_term = None
    if col_q1.button("Discover Weekly"): auto_search_term = "Discover Weekly owner:spotify"
    if col_q2.button("Release Radar"): auto_search_term = "Release Radar owner:spotify"
    if col_q3.button("On Repeat"): auto_search_term = "On Repeat owner:spotify"
    if col_q4.button("Time Capsule"): auto_search_term = "Time Capsule owner:spotify"

    final_query = auto_search_term if auto_search_term else (search_query if search_clicked else None)

    if final_query:
        try:
            results_search = sp_read.search(q=final_query, type='playlist', limit=8)
            playlists_found = results_search['playlists']['items']
            
            if playlists_found:
                st.markdown("<br>", unsafe_allow_html=True)
                st.success(f"Found {len(playlists_found)} results for '{final_query.replace('owner:spotify', '').strip()}'")
                
                # GRID DISPLAY
                cols = st.columns(4)
                for i, pl in enumerate(playlists_found):
                    if pl:
                        with cols[i % 4]:
                            # Card HTML
                            img_url = pl['images'][0]['url'] if pl['images'] else "https://via.placeholder.com/300"
                            if st.button(f"Select:\n{pl['name'][:20]}...", key=pl['id']): # Hack to make card clickable-ish
                                st.session_state['selected_search_id'] = pl['id']
                                st.rerun()
                                
                            st.markdown(f"""
                            <div style="margin-top:-10px; margin-bottom:20px;">
                                <img src="{img_url}" style="width:100%; border-radius:8px;">
                                <div style="font-weight:bold; font-size:0.9em; margin-top:5px;">{pl['name']}</div>
                                <div style="font-size:0.8em; color:#B3B3B3;">{pl['owner']['display_name']}</div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.warning("No playlists found.")
                
        except Exception as e:
            st.error(f"Search failed: {e}")

    # Check for session state selection
    if 'selected_search_id' in st.session_state:
        selected_playlist_id = st.session_state['selected_search_id']


# TAB 3: PASTE LINK
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Import via Link")
    link_input = st.text_input("Paste URL", placeholder="https://open.spotify.com/playlist/...")
    if link_input:
        parsed_id = get_playlist_id_from_link(link_input)
        if parsed_id:
            selected_playlist_id = parsed_id
        else:
            st.error("Invalid Spotify Link")


# --- DISPLAY RESULTS ---
if selected_playlist_id:
    results = None
    fetch_errors = []
    
    # Strategy 1: Market = from_token (Requires scope user-read-private)
    if not results:
        try:
            results = sp_read.playlist(selected_playlist_id, market='from_token')
        except Exception as e:
            fetch_errors.append(f"Strategy 1 (from_token): {e}")

    # Strategy 2: No Market (Generic)
    if not results:
        try:
            results = sp_read.playlist(selected_playlist_id)
        except Exception as e:
            fetch_errors.append(f"Strategy 2 (No Market): {e}")

    # Strategy 3: Market = US (Fallback)
    if not results:
        try:
            results = sp_read.playlist(selected_playlist_id, market='US')
        except Exception as e:
            fetch_errors.append(f"Strategy 3 (US): {e}")
            
    # Strategy 4: Raw (No additional types)
    if not results:
        try:
            results = sp_read.playlist(selected_playlist_id, additional_types=None)
        except Exception as e:
            fetch_errors.append(f"Strategy 4 (No additional_types): {e}")
            
    if results:
        try:
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
            track_uris = [] # For cloning
            
            for item in tracks:
                if item.get('track'):
                    track = item['track']
                    t_name = track['name']
                    track_uris.append(track['uri']) # Collect URI
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
                        else:
                            # Handle empty/local tracks
                            st.caption(f"{idx + 1}. Unknown Track (Local? or Unplayable)")

            # --- RIGHT: ACTIONS ---
            with col_actions:
                st.container()
                with st.container():
                    st.subheader("Share EXACT List")
                    st.info("ℹ️ Spotify links often change songs. Use these tools to share your **exact** tracklist.")
                    
                    # 1. Text Copy (Best for Chat)
                    st.markdown("**1. Copy to WhatsApp/Discord**")
                    text_content = "\n".join(share_list_text)
                    
                    # WhatsApp Button
                    encoded_text = urllib.parse.quote(text_content)
                    whatsapp_url = f"https://wa.me/?text={encoded_text}"
                    st.markdown(f"""
                    <a href="{whatsapp_url}" target="_blank" style="
                        display: inline-block;
                        background-color: #25D366;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 20px;
                        text-decoration: none;
                        font-weight: bold;
                        margin-bottom: 10px;
                    ">
                        📱 Share on WhatsApp
                    </a>
                    """, unsafe_allow_html=True)

                    # Code Block for Copy
                    st.code(text_content, language="text")
                    st.caption("Click the copy button 📄 in the top right of the box above.")
                    
                    st.markdown("<br>", unsafe_allow_html=True)

                    # 2. CSV Export (Best for Backup)
                    st.markdown("**2. Download File**")
                    df = pd.DataFrame(track_data_csv)
                    csv = df.to_csv(index=False).encode('utf-8')
                    
                    st.download_button(
                        label="⬇️ Download as CSV",
                        data=csv,
                        file_name=f"{results['name']}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # 3. Direct Link (Fallback)
                    st.markdown("**3. Original Link (May Change Songs)**")
                    spotify_url = results['external_urls']['spotify']
                    st.text_input("Spotify URL", value=spotify_url, label_visibility="collapsed")
                    
                    st.markdown("<br>", unsafe_allow_html=True)

                    # 4. Clone Feature
                    st.markdown("**4. Clone & Share (Static Link)**")
                    st.caption("Creates a new playlist in YOUR library with these exact songs.")
                    
                    if st.button("✨ Create Copy of Playlist", use_container_width=True):
                        try:
                            with st.spinner("Creating playlist..."):
                                # 1. Create Playlist
                                user_id = sp.current_user()['id']
                                new_pl_name = f"Copy of {results['name']}"
                                desc = f"Static copy of {results['name']} created on {pd.Timestamp.now().strftime('%Y-%m-%d')}"
                                new_pl = sp.user_playlist_create(user_id, new_pl_name, public=False, description=desc)
                                
                                # 2. Add Tracks (Chunked 100)
                                if track_uris:
                                    for i in range(0, len(track_uris), 100):
                                        chunk = track_uris[i:i+100]
                                        sp.playlist_add_items(new_pl['id'], chunk)
                                
                                st.success(f"✅ Created!")
                                st.text_input("New Shareable Link", value=new_pl['external_urls']['spotify'])
                        except Exception as e:
                            st.error(f"Failed: {e}")
                            if "403" in str(e):
                                st.warning("⚠️ Permission Denied: Your current token (e.g. Exportify) might be Read-Only. You cannot create playlists with it.")
        except Exception as e:
            st.error(f"Error processing playlist display: {e}")
            
    else:
        st.error(f"Could not load playlist.")
        with st.expander("Debug Details (Show this to Developer)"):
            for err in fetch_errors:
                st.write(err)
            
            st.warning("⚠️ Try clicking 'Logout / Reset' in the sidebar to refresh permissions!")
