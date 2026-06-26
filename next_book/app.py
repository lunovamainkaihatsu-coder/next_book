import os
import json
import time
from datetime import datetime

def load_reading_log():

    if os.path.exists(READING_LOG_PATH):

        try:

            with open(
                READING_LOG_PATH,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except:
            return []

    return []


def save_reading_log(data):

    with open(
        READING_LOG_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


import random
import time
import urllib.parse
import requests
from typing import List, Dict

import streamlit as st

READING_LOG_PATH = "reading_log.json"

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# =========================
# 基本設定
# =========================
st.set_page_config(
    page_title="次の一冊",
    page_icon="icon.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

APP_TITLE = "次の一冊"


# =========================
# CSS
# =========================
st.markdown(
    """
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#f6a9c8">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="次の一冊">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
""",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Zen+Maru+Gothic:wght@400;500;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Zen Maru Gothic', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 220, 235, 0.75), transparent 34%),
            radial-gradient(circle at top right, rgba(210, 230, 255, 0.75), transparent 30%),
            linear-gradient(180deg, #fff7fb 0%, #f7fbff 100%);
    }

    .beta-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 999px;
        background: #fff0f6;
        color: #9a5575;
        font-size: 0.85rem;
        font-weight: 800;
        margin-bottom: 12px;
    }

    .hero {
        background: rgba(255,255,255,0.88);
        padding: 32px 24px;
        border-radius: 30px;
        border: 1px solid #f3dce8;
        box-shadow: 0 10px 28px rgba(120, 90, 130, 0.09);
        margin-bottom: 22px;
        text-align: center;
    }

    .main-title {
        font-size: 2.55rem;
        font-weight: 900;
        color: #3f3a4a;
        margin-bottom: 8px;
        letter-spacing: 0.04em;
    }

    .sub-text {
        font-size: 1rem;
        color: #756b80;
        line-height: 1.9;
        font-weight: 500;
    }

    .scene-card, .mood-card {
        background: rgba(255,255,255,0.78);
        border: 1px solid #f2dfea;
        border-radius: 24px;
        padding: 18px 18px;
        margin-bottom: 18px;
        color: #665d70;
        line-height: 1.8;
        box-shadow: 0 6px 18px rgba(120, 90, 130, 0.055);
    }

    .scene-title {
        font-weight: 900;
        color: #4b4458;
        margin-bottom: 5px;
    }

    .hint-box {
        background: #ffffffcc;
        border: 1px dashed #e7bfd0;
        border-radius: 20px;
        padding: 15px 18px;
        color: #6f6578;
        font-size: 0.93rem;
        line-height: 1.8;
        margin-bottom: 16px;
    }

    textarea {
        border-radius: 20px !important;
        border: 1px solid #ead7e2 !important;
        background-color: #ffffff !important;
        font-family: 'Zen Maru Gothic', sans-serif !important;
    }

    input {
        font-family: 'Zen Maru Gothic', sans-serif !important;
    }

    .stButton > button {
        border-radius: 999px;
        border: none;
        background: linear-gradient(90deg, #f6a9c8, #8fb7ff);
        color: white;
        font-weight: 800;
        padding: 0.72rem 1rem;
        box-shadow: 0 5px 14px rgba(120, 120, 180, 0.16);
        font-family: 'Zen Maru Gothic', sans-serif;
    }

    .stButton > button:hover {
        opacity: 0.92;
        color: white;
        border: none;
    }

    .loading-box {
        background: rgba(255,255,255,0.86);
        border: 1px solid #f2dfea;
        border-radius: 24px;
        padding: 20px;
        margin: 18px 0;
        text-align: center;
        color: #655c70;
        box-shadow: 0 8px 22px rgba(120, 90, 130, 0.07);
    }

    .loading-books {
        font-size: 2rem;
        letter-spacing: 0.4rem;
        animation: floatBooks 1.8s ease-in-out infinite;
    }

    @keyframes floatBooks {
        0% { transform: translateY(0px); opacity: 0.75; }
        50% { transform: translateY(-7px); opacity: 1; }
        100% { transform: translateY(0px); opacity: 0.75; }
    }

    .loading-text {
        margin-top: 8px;
        font-weight: 800;
    }

    .result-title {
        font-size: 1.38rem;
        font-weight: 900;
        color: #3f3a4a;
        margin-top: 26px;
        margin-bottom: 8px;
    }

    .book-cover {
        width: 72px;
        min-width: 72px;
        height: 108px;
        border-radius: 12px;
        background: linear-gradient(160deg, #f6a9c8, #8fb7ff);
        box-shadow: 0 8px 16px rgba(120, 90, 130, 0.14);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.8rem;
        font-weight: 900;
        position: relative;
        overflow: hidden;
        margin-bottom: 8px;
    }

    .book-cover::before {
        content: "";
        position: absolute;
        left: 10px;
        top: 0;
        width: 4px;
        height: 100%;
        background: rgba(255,255,255,0.35);
    }

    .book-cover::after {
        content: "BOOK";
        position: absolute;
        bottom: 12px;
        font-size: 0.62rem;
        letter-spacing: 0.12em;
        opacity: 0.9;
    }

    .pill {
        display: inline-block;
        padding: 5px 11px;
        border-radius: 999px;
        background: #fff0f6;
        color: #8d5570;
        font-size: 0.82rem;
        font-weight: 800;
        margin-right: 6px;
        margin-bottom: 4px;
    }

    .mini-message {
        background: #ffffffcc;
        border-left: 5px solid #f6a9c8;
        border-radius: 16px;
        padding: 13px 16px;
        color: #655c70;
        margin: 16px 0;
        line-height: 1.7;
        font-weight: 500;
    }

    .small-note {
        font-size: 0.85rem;
        color: #9a92a0;
        text-align: center;
        margin-top: 28px;
        line-height: 1.8;
    }

    /* =========================
       スマホ表示調整
       ========================= */
    @media screen and (max-width: 640px) {

        .hero {
            padding: 22px 16px;
            border-radius: 22px;
            margin-bottom: 16px;
        }

        .main-title {
            font-size: 2rem;
        }

        .sub-text {
            font-size: 0.92rem;
            line-height: 1.7;
        }

        .scene-card,
        .mood-card {
            padding: 14px 14px;
            border-radius: 18px;
            margin-bottom: 14px;
            line-height: 1.7;
        }

        .scene-title {
            font-size: 1rem;
        }

        .stButton > button {
            width: 100%;
            min-height: 56px;
            border-radius: 16px;
            font-size: 1rem;
            font-weight: 600;
        }

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .scene-card {
            font-size: 0.95rem;
        }

        .scene-card b {
            font-size: 1.05rem;
        }

        .stProgress > div > div > div {
            height: 10px;
            border-radius: 999px;
        }
        div[style*="border-left: 10px solid #c89f68"] {
            padding: 14px !important;
            border-radius: 16px !important;
            margin-bottom: 12px !important;
        }

        div[style*="font-size: 1.15rem"] {
            font-size: 1rem !important;
        }

        div[style*="line-height:1.9"] {
            font-size: 0.92rem !important;
            line-height: 1.7 !important;
        }
     }
     /* =========================
       Streamlit Cloud 文字色対策
       ========================= */
    .stApp,
    .stApp p,
    .stApp div,
    .stApp span,
    .stApp label {
            color: #3f3a4a;
    }

    .stMarkdown,
    .stMarkdown p,
    .stMarkdown div {
        color: #3f3a4a;
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebar"] * {
        color: #2f2a38;
    }

    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stSlider label {
        color: #3f3a4a !important;
    }

    .stCaption,
    .caption {
        color: #756b80 !important;
    }
    /* =========================
       入力欄文字色対策
       ========================= */

    .stTextInput input,
    .stTextArea textarea {
        color: #2f2a38 !important;
        background-color: #ffffff !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #888888 !important;
    }
    /* =========================
       サイドバー文字色改善
       ========================= */

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        color: white !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: white !important;
    }
    /* =========================
           サイドバー背景
       ========================= */
    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #2f2a38 0%,
            #4d3f63 100%
        ) !important;
    }
    /* =========================
       Android WebView 上部余白対策
       ========================= */

    .block-container {
        padding-top: 4rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================
# ダミーデータ
# =========================
DUMMY_BOOKS = [
    {
        "title": "夢をかなえるゾウ",
        "author": "水野敬也",
        "genre": "実用書",
        "difficulty": "やさしい",
        "mood": "背中を押されたい時",
        "reading_time": "気軽に読み進めたい夜に",
        "after_feeling": "少し前向きになる",
        "published_year": "2007年ごろ",
        "match_level": "高め",
        "reason": "物語形式で読みやすく、行動のきっかけをもらいやすい本です。",
        "for_who": "最近少し停滞していて、軽く背中を押してほしい人",
        "comment": "最初の一歩を出したい時にぴったりです。",
    },
    {
        "title": "アルジャーノンに花束を",
        "author": "ダニエル・キイス",
        "genre": "小説",
        "difficulty": "ふつう",
        "mood": "心を静かに動かしたい時",
        "reading_time": "落ち着いて読める休日に",
        "after_feeling": "静かな余韻が残る",
        "published_year": "1959年ごろ",
        "match_level": "じっくり向き",
        "reason": "知性や優しさ、人間らしさについて深く考えさせてくれる物語です。",
        "for_who": "心を動かされる小説を読みたい人",
        "comment": "読み終えたあと、静かに余韻が残る一冊です。",
    },
    {
        "title": "嫌われる勇気",
        "author": "岸見一郎, 古賀史健",
        "genre": "実用書",
        "difficulty": "ふつう",
        "mood": "自分の軸を取り戻したい時",
        "reading_time": "考えを整理したい時に",
        "after_feeling": "少し視界が開ける",
        "published_year": "2013年ごろ",
        "match_level": "かなり高い",
        "reason": "他人の評価に振り回されず、自分の軸を取り戻すヒントが得られます。",
        "for_who": "人間関係や自己肯定感で悩んでいる人",
        "comment": "自分を立て直したい時に相性がいい本です。",
    },
]


# =========================
# セッション
# =========================
defaults = {
    "books": [],
    "last_query": "",
    "last_message": "",
    "main_input": "",
    "extra_input": "",
    "search_history": [],
    "reading_log": load_reading_log(),
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================
# ページ切り替え
# =========================
st.sidebar.markdown(
    """
# 📚 次の一冊

小さな読書アプリ
🐰 うさぎ司書と本棚づくり
"""
)

page = st.sidebar.radio(
    "",
    [
        "🏠 メイン",
        "🔍 本を探す",
        "📚 本棚",
        "📊 記録",
        "ℹ️ このアプリについて"
    ]
)

# =========================
# 補助関数
# =========================
def difficulty_icon(difficulty: str) -> str:
    if difficulty == "やさしい":
        return "🌱"
    if difficulty == "深い":
        return "🔥"
    return "📘"


def get_loading_message() -> str:
    return random.choice([
        "本棚を歩き回っています...",
        "ぴったりの一冊を探しています...",
        "ページをめくっています...",
        "物語の世界を探索中です...",
        "今の気分に合う本を選んでいます...",
        "静かな本屋さんを巡っています...",
    ])


def render_loading_box(message: str):
    st.markdown(
        f"""
        <div class="loading-box">
            <div class="loading-books">📚 📖 📘</div>
            <div class="loading-text">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def set_mood_text(text: str):
    st.session_state.main_input = text


def get_cover_icon(genre: str, difficulty: str) -> str:
    if genre == "小説":
        return "🌙"
    if difficulty == "深い":
        return "🔥"
    if difficulty == "やさしい":
        return "🌱"
    return "📚"


def get_match_icon(match_level: str) -> str:
    if match_level == "かなり高い":
        return "🌟🌟🌟"
    if match_level == "じっくり向き":
        return "📘"
    return "🌟🌟"


def make_search_links(title: str, author: str):
    query = urllib.parse.quote(f"{title} {author}")
    amazon_url = f"https://www.amazon.co.jp/s?k={query}&i=stripbooks"
    rakuten_url = f"https://books.rakuten.co.jp/search?sitem={query}"
    return amazon_url, rakuten_url
def get_cover_url(title, author):
    try:
        query = urllib.parse.quote(f"{title} {author}")

        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"

        r = requests.get(url, timeout=5)
        data = r.json()

        items = data.get("items", [])

        if items:
            info = items[0].get("volumeInfo", {})
            images = info.get("imageLinks", {})

            cover_url = (
                images.get("thumbnail")
                or images.get("smallThumbnail")
            )

            if cover_url:
                return cover_url.replace("http://", "https://")

    except Exception:
        pass

    return None

def get_book_info_from_google(title, author):
    def search_google_books(query_text):
        query = urllib.parse.quote(query_text)
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=1"

        r = requests.get(url, timeout=5)
        data = r.json()

        return data.get("items", [])

    try:
        search_patterns = [
            f'intitle:"{title}" inauthor:"{author}"',
            f"{title} {author}",
            f'intitle:"{title}"',
            title,
        ]

        for pattern in search_patterns:

            items = search_google_books(pattern)

            if items:
                info = items[0].get("volumeInfo", {})

                return {
                    "found": True,
                    "title": info.get("title", title),
                    "author": ", ".join(info.get("authors", [author])),
                    "description": info.get("description", ""),
                    "published_date": info.get("publishedDate", ""),
                    "thumbnail": (
                        info.get("imageLinks", {}).get("thumbnail")
                        or info.get("imageLinks", {}).get("smallThumbnail")
                        or ""
                    ),
                }

    except Exception:
        pass

    return {
        "found": False,
        "title": title,
        "author": author,
        "description": "",
        "published_date": "",
        "thumbnail": "",
    }

def build_prompt(user_input: str, extra_condition: str = "") -> str:
    condition_text = f"\n追加条件: {extra_condition}" if extra_condition else ""

    return f"""
あなたは本の推薦アシスタントです。
ユーザーの自然文を読み取り、実在する日本語書籍を優先して、おすすめの本を3冊提案してください。

ルール:
- 対象は「実用書」または「小説」のみ
- 漫画、イラスト集、雑誌、成人向けは除外
- 実在が曖昧な本は避け、知名度や流通量が比較的高い本を優先する
- 情報に自信がない場合は、無理に珍しい本を出さない
- 日本国内で比較的入手しやすい本を優先する
- 日本語の読者が読みやすい本を優先
- ユーザーの気分や状況を読み取り、それに寄り添う
- 「なぜ今この本なのか」を説明する
- 同じ理由の使い回しを避ける
- 1冊は読みやすい本、1冊は少し深い本、1冊は意外性のある本を混ぜる
- 押し付けず、やさしく提案する
- 静かな本屋やカフェで相談しているような、落ち着いた文体にする
- 成人向け・過激な内容の本は避ける
- 出力はJSONのみ
- JSONのキーは以下に厳密に合わせること:
  title, author, genre, difficulty, mood, reading_time, after_feeling, published_year, match_level, reason, for_who, comment
- difficulty は「やさしい」「ふつう」「深い」のいずれか
- genre は「実用書」または「小説」
- mood は「どんな気分の時に合う本か」を短く書く
- reading_time は「どんなタイミングで読みたいか」を短く書く
- after_feeling は「読後感」を短く書く
- published_year は「2013年ごろ」のように、わかる範囲で書く。不明なら「不明」
- match_level は「かなり高い」「高め」「じっくり向き」のいずれか

ユーザー入力:
{user_input}
{condition_text}

出力形式:
[
  {{
    "title": "本のタイトル",
    "author": "著者名",
    "genre": "実用書 or 小説",
    "difficulty": "やさしい / ふつう / 深い",
    "mood": "どんな気分の時に合うか",
    "reading_time": "読むタイミング",
    "after_feeling": "読後感",
    "published_year": "発行年",
    "match_level": "かなり高い / 高め / じっくり向き",
    "reason": "おすすめ理由",
    "for_who": "どんな人向けか",
    "comment": "ひとことコメント"
  }}
]
""".strip()


def get_books_from_openai(user_input: str, extra_condition: str = "") -> List[Dict]:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or OpenAI is None:
        return DUMMY_BOOKS

    client = OpenAI(api_key=api_key)
    prompt = build_prompt(user_input, extra_condition)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.85,
        messages=[
            {"role": "system", "content": "あなたは優秀でやさしい書籍推薦アシスタントです。"},
            {"role": "user", "content": prompt},
        ],
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "").replace("```", "").strip()

    try:
        books = json.loads(content)
        if isinstance(books, list):
            return books
    except json.JSONDecodeError:
        return DUMMY_BOOKS

    return DUMMY_BOOKS


def search_books(query: str, extra: str = "", message: str = "今のあなたに合いそうな本を見つけました📚"):
    loading_message = get_loading_message()
    loading_area = st.empty()

    with loading_area.container():
        render_loading_box(loading_message)

    time.sleep(0.7)

    st.session_state.books = get_books_from_openai(query, extra_condition=extra)
    st.session_state.last_query = query
    st.session_state.last_message = message

    loading_area.empty()


# =========================
# 安定版カード表示
# =========================
def render_book_card(book, card_index):
    title = book.get("title", "タイトル不明")
    author = book.get("author", "著者不明")
    google_info = get_book_info_from_google(
        title,
        author
    )
    genre = book.get("genre", "不明")
    difficulty = book.get("difficulty", "不明")
    mood = book.get("mood", "今の気分に合いそう")
    reading_time = book.get("reading_time", "ゆっくり読める時に")
    after_feeling = book.get("after_feeling", "余韻が残る")
    published_year = book.get("published_year", "不明")
    match_level = book.get("match_level", "高め")

    reason = book.get("reason", "")
    for_who = book.get("for_who", "")
    comment = book.get("comment", "")
    icon = difficulty_icon(difficulty)
    cover_icon = get_cover_icon(genre, difficulty)
    match_icon = get_match_icon(match_level)

    amazon_url, rakuten_url = make_search_links(title, author)
    safe_key = f"{card_index}_{title}_{author}".replace(" ", "_").replace("　", "_")

    def add_to_log(status_name):
        exists = any(
            x.get("title") == title and x.get("author") == author
            for x in st.session_state.reading_log
        )

        if exists:
            st.warning("📚 すでに登録済みです")
            return

        st.session_state.reading_log.append(
            {
                "title": title,
                "author": author,
                "status": status_name,
                "rating": 3,
                "memo": "AI検索から追加",
                "date": datetime.now().strftime("%Y/%m/%d"),
                "favorite": False,
            }
        )

        save_reading_log(st.session_state.reading_log)
        st.success(f"{status_name}に追加しました📚")

    with st.container():
        st.markdown("---")

        col1, col2 = st.columns([1, 4])

        with col1:

            cover_url = get_cover_url(
                title,
                author
            )

            if cover_url:

                st.image(
                    cover_url,
                    use_container_width=True
                )
            else:

                st.markdown(
                    f"""
                    <div class="book-cover">
                        {cover_icon}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        with col2:
            if google_info["found"]:

                st.markdown(
                    f"### ✅ {title}"
                )

            else:

                st.markdown(
                    f"### ⚠️ {title}"
                )
            st.caption(f"著者：{author} ／ 発行年：{published_year}")

            st.markdown(
                f"""
                <span class="pill">{genre}</span>
                <span class="pill">{icon} {difficulty}</span>
                <span class="pill">☕ {mood}</span>
                <span class="pill">🕯️ {reading_time}</span>
                <span class="pill">🌙 {after_feeling}</span>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(f"**{match_icon} 相性：{match_level}**")

            st.markdown("#### 📚 今のあなたに合いそうな理由")
            st.write(reason)

            st.markdown("#### 📖 Google Books情報")

            if google_info["found"]:

                if google_info["published_date"]:
                    st.write(
                        f"📅 発行日：{google_info['published_date']}"
                    )

                if google_info["description"]:

                    desc = google_info["description"][:300]

                    st.write(desc + "...")

                else:
                    st.caption(
                        "説明文は見つかりませんでした。"
                    )

            else:

                st.caption(
                    "Google Booksでは確認できませんでした。販売サイトで確認してください。"
                )

            st.markdown("#### 🌱 向いている人")
            st.write(for_who)

            st.markdown("#### 💬 ひとこと")
            st.write(comment)

            st.markdown("#### 🔎 販売サイトで探す")

            link_col1, link_col2 = st.columns(2)

            with link_col1:
                st.link_button("Amazonで探す", amazon_url, use_container_width=True)

            with link_col2:
                st.link_button("楽天ブックスで探す", rakuten_url, use_container_width=True)

            st.caption(
                "※ AIによる提案です。リンク先の内容・価格・在庫・版などは必ず販売サイトや公式情報でご確認ください。"
            )

            st.markdown("#### 📚 読書記録に追加")

            add_col1, add_col2, add_col3 = st.columns(3)

            with add_col1:
                if st.button("🌱 気になる", key=f"add_want_{safe_key}", use_container_width=True):
                    add_to_log("気になる")

            with add_col2:
                if st.button("📖 読書中", key=f"add_reading_{safe_key}", use_container_width=True):
                    add_to_log("読書中")

            with add_col3:
                if st.button("🏆 読了", key=f"add_done_{safe_key}", use_container_width=True):
                    add_to_log("読了")
                    
# =========================
# UI
# =========================

# =========================================
# メイン
# =========================================
if page == "🏠 メイン":

    # =========================
    # スプラッシュ風カード
    # =========================
    st.markdown(
        """
<div class="hero">
<div class="beta-badge">🐰 うさぎ司書</div>
<div class="main-title">📚 次の一冊</div>
<div class="sub-text">
今日のあなたに合う本を、そっと探します。<br>
本棚と読書記録を、楽しく育てていきましょう。
</div>
</div>
""",
        unsafe_allow_html=True,
    )


    st.caption(
    "📱 スマホでは左上のメニューからページを切り替えられます"
    )

    q1, q2 = st.columns(2)

    with q1:
        if st.button(
            "🔍 本を探す",
            use_container_width=True
        ):
            st.info("左メニューから本を探せます📚")

    with q2:
        if st.button(
            "📚 本棚を見る",
            use_container_width=True
        ):
            st.info("左メニューから本棚へどうぞ📖")

    all_books = st.session_state.reading_log

    reading_books = [
        x
        for x in all_books
        if x.get("status") == "読書中"
    ]

    want_books = [
        x
        for x in all_books
        if x.get("status") == "気になる"
    ]

    finished_books = [
        x
        for x in all_books
        if x.get("status") == "読了"
    ]

    reading_count = len(reading_books)
    want_count = len(want_books)
    finished_count = len(finished_books)

    # =========================
    # メイン用カード
    # =========================
    def main_book_card(book, icon="📗"):

        st.markdown(
            f"""
<div class="scene-card">
<div class="scene-title">
{icon} {book.get("title", "タイトル不明")}
</div>
👤 {book.get("author", "著者不明")}<br>
🌱 状態：{book.get("status", "不明")}<br>
⭐ 評価：{"⭐" * int(book.get("rating", 0))}
</div>
""",
            unsafe_allow_html=True,
        )

    # =========================
    # うさぎ司書メッセージ
    # =========================

    if finished_count >= 50:

        rabbit_message = (
            "👑 たくさんの本と出会ってきましたね。"
            " うさぎ司書も誇らしいです。"
        )

    elif finished_count >= 30:

        rabbit_message = (
            "🏆 読書習慣がすっかり身についていますね！"
        )

    elif finished_count >= 10:

        rabbit_message = (
            "🌱 本棚が少しずつ育っています。"
        )

    elif reading_count > 0:

        rabbit_message = (
            f"📖 読書中の本が{reading_count}冊あります。"
            "今日は少しだけページを開いてみませんか？"
        )

    elif want_count > 0:

        rabbit_message = (
            f"📚 気になる本が{want_count}冊あります。"
            "今日はその中から一冊選んでみましょう。"
        )

    else:

        rabbit_message = (
            "🐰 まずは気になる本を一冊登録してみましょう。"
            "小さな本棚づくりの始まりです。"
        )
    extra_rabbit_messages = [
        "🏡 本棚はあなただけの小さな図書館です。",
        "🌸 読書はゆっくりでも大丈夫です。",
        "📖 たった1ページでも前進です。",
        "🐰 今日はどんな本に出会えるでしょう？",
        "✨ 読んだ分だけ世界が広がります。",
    ]
    # =========================
    # うさぎ司書レベル
    # =========================

    if finished_count >= 100:
        rabbit_level = "👑 Lv.5 伝説の司書うさぎ"
        level_message = "図書館長も驚く読書量です！"

    elif finished_count >= 50:
        rabbit_level = "🏰 Lv.4 図書館案内うさぎ"
        level_message = "かなりの読書家ですね！"

    elif finished_count >= 30:
        rabbit_level = "📖 Lv.3 読書応援うさぎ"
        level_message = "読書習慣がしっかり根付いています！"

    elif finished_count >= 10:
        rabbit_level = "🌱 Lv.2 本棚見守りうさぎ"
        level_message = "本棚が育ってきましたね！"

    else:
        rabbit_level = "🐣 Lv.1 新米司書うさぎ"
        level_message = "まずは最初の一冊を目指しましょう！"
    rabbit_message = (
        rabbit_message
        + "<br>"
        + random.choice(extra_rabbit_messages)
    )

    if finished_count < 10:
        next_rabbit_level = 10

    elif finished_count < 30:
        next_rabbit_level = 30

    elif finished_count < 50:
        next_rabbit_level = 50

    elif finished_count < 100:
        next_rabbit_level = 100

    else:
        next_rabbit_level = finished_count

    rabbit_remaining = max(
        next_rabbit_level - finished_count,
        0
    )

    # =========================
    # うさぎ経験値バー
    # =========================
    if finished_count < 10:
        rabbit_progress = finished_count / 10

    elif finished_count < 30:
        rabbit_progress = finished_count / 30

    elif finished_count < 50:
        rabbit_progress = finished_count / 50

    elif finished_count < 100:
        rabbit_progress = finished_count / 100

    else:
        rabbit_progress = 1.0

    st.markdown(
        f"""
    <div class="scene-card">
    <div class="scene-title">🐰 うさぎ司書さん</div>
    <b>{rabbit_level}</b><br>
    💬 {level_message}<br>
    🌟 次のレベルまであと {rabbit_remaining}冊<br>
    {rabbit_message}
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.progress(rabbit_progress)
    
    with st.expander("🏆 称号・バッジを見る", expanded=False):
        # =========================
        # 読了称号
        # =========================
        if finished_count >= 100:
            title_rank = "👑 本の賢者"

        elif finished_count >= 50:
            title_rank = "🏰 図書館マスター"

        elif finished_count >= 30:
            title_rank = "📖 読書家"

        elif finished_count >= 10:
            title_rank = "🌱 見習い読書家"

        elif finished_count >= 1:
            title_rank = "🐣 読書の一歩"

        else:
            title_rank = "🥚 これから読書家"

        st.markdown(
            f"""
    <div class="scene-card">
    <div class="scene-title">🏆 あなたの読了称号</div>
    <div style="font-size:1.25rem; font-weight:900;">
    {title_rank}
    </div>
    読了冊数：{finished_count}冊
    </div>
    """,
            unsafe_allow_html=True,
        )

        # =========================
        # 次の称号まで
        # =========================
        if finished_count < 1:
            next_goal = 1
            next_title = "🐣 読書の一歩"

        elif finished_count < 10:
            next_goal = 10
            next_title = "🌱 見習い読書家"

        elif finished_count < 30:
            next_goal = 30
            next_title = "📖 読書家"

        elif finished_count < 50:
            next_goal = 50
            next_title = "🏰 図書館マスター"

        elif finished_count < 100:
            next_goal = 100
            next_title = "👑 本の賢者"

        else:
            next_goal = finished_count
            next_title = "最高称号達成中"

        if finished_count < 100:

            remaining = next_goal - finished_count
            progress = finished_count / next_goal

            st.markdown(
                f"""
    <div class="scene-card">
    <div class="scene-title">🌟 次の称号まで</div>
    次の称号：{next_title}<br>
    あと <b>{remaining}冊</b> で到達します。
    </div>
    """,
                unsafe_allow_html=True,
            )

            st.progress(progress)

        else:

            st.success(
                "👑 最高称号に到達しています！すごい読書家です📚"
            )

    # =========================
    # 今日の読書ミッション
    # =========================
    st.markdown("### 🎯 今日の読書ミッション")

    mission_list = [
        "5分だけ本を開く",
        "1ページだけ読む",
        "気になる本を1冊追加する",
        "読書中の本を少し進める",
        "読み終えた本に感想を書く",
    ]

    today_mission = random.choice(
        mission_list
    )

    st.markdown(
        f"""
<div class="scene-card">
<div class="scene-title">今日のミッション</div>
🎯 {today_mission}
</div>
""",
        unsafe_allow_html=True,
    )

    # =========================
    # 読書バッジ
    # =========================
    st.markdown("### 🍎 読書バッジ")

    if finished_count >= 20:
        badge = "⭐ たくさん読めたねバッジ"

    elif finished_count >= 10:
        badge = "📖 読書だいすきバッジ"

    elif finished_count >= 5:
        badge = "🌱 すくすく読書バッジ"

    elif finished_count >= 1:
        badge = "🍎 はじめて読了バッジ"

    else:
        badge = "🥚 これから読書バッジ"

    st.markdown(
        f"""
<div class="scene-card">
<div class="scene-title">今のバッジ</div>
{badge}
</div>
""",
        unsafe_allow_html=True,
    )

    # =========================
    # 今日の一冊
    # =========================
    st.markdown("### 🐰 今日の一冊")

    candidate_books = [
        book
        for book in all_books
        if book.get("status") in ["気になる", "読書中"]
    ]

    if not candidate_books:
        candidate_books = all_books

    if candidate_books:

        today_book = random.choice(
            candidate_books
        )

        main_book_card(
            today_book,
            icon="📗"
        )

        st.caption(
            "今日はこの本を少しだけ開いてみてもいいかも📖"
        )

    else:

        st.info(
            "まずは本を登録してみよう📚"
        )

    st.markdown("---")

    # =========================
    # 今読んでいる本
    # =========================
    st.markdown("### 📖 今読んでいる本")

    if reading_books:

        for book in reading_books[:3]:
            main_book_card(
                book,
                icon="📖"
            )

    else:

        st.info(
            "読書中の本はありません📚"
        )

    st.markdown("---")

    # =========================
    # 次に読みたい本
    # =========================
    st.markdown("### 🌱 次に読みたい本")

    if want_books:

        for book in want_books[:5]:
            main_book_card(
                book,
                icon="🌱"
            )

    else:

        st.info(
            "気になる本はありません🌱"
        )
# =========================================
# ホーム
# =========================================
if page == "📊 記録":

    st.markdown("# 📚 次の一冊")
    st.caption("あなた専用の読書ダッシュボード")

    all_books = st.session_state.reading_log

    st.subheader("🎯 今月の読書目標")

    monthly_goal = st.number_input(
        "今月何冊読了したい？",
        min_value=1,
        max_value=100,
        value=5
    )
    finished_count = len(
        [
            x
            for x in st.session_state.reading_log
            if x.get("status") == "読了"
        ]
    )

    progress = min(
        finished_count / monthly_goal,
        1.0
    )

    if finished_count >= monthly_goal:

        st.success(
            "🎉 今月の目標達成です！"
        )

    else:

        remaining = monthly_goal - finished_count

        st.info(
            f"あと {remaining}冊で達成です！"
        )

    st.progress(progress)

    st.write(
        f"📚 {finished_count} / {monthly_goal}冊"
    )

    total_books = len(all_books)

    finished_books = len(
        [
            x
            for x in all_books
            if x.get("status") == "読了"
        ]
    )

    favorite_books_count = len(
        [
            x
            for x in all_books
            if x.get("favorite", False)
        ]
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("📚 登録", total_books)

    with c2:
        st.metric("🏆 読了", finished_books)

    with c3:
        st.metric("❤️ お気に入り", favorite_books_count)

    # =========================
    # 共通カード
    # =========================
    def home_book_card(book, icon="📗"):

        title = book.get("title", "タイトル不明")
        author = book.get("author", "著者不明")
        status = book.get("status", "不明")
        rating = int(book.get("rating", 0))

        st.markdown(
            f"""
<div class="scene-card">
<div class="scene-title">
{icon} {title}
</div>
👤 {author}<br>
🌱 状態：{status}<br>
⭐ 評価：{"⭐" * rating}
</div>
""",
            unsafe_allow_html=True,
        )
        
    st.markdown("---")

    # 読書レベル
    st.subheader("📚 読書レベル")

    if total_books >= 100:
        level = "👑 本の賢者"

    elif total_books >= 50:
        level = "🏰 図書館マスター"

    elif total_books >= 30:
        level = "📖 読書家"

    elif total_books >= 10:
        level = "🌱 見習い読書家"

    else:
        level = "🐣 読書ビギナー"

    st.success(level)
    st.caption(f"現在 {total_books}冊登録")

    st.markdown("---")

    # 最近読了した本
    st.subheader("🏆 最近読了した本")

    finished_books_list = [
        x
        for x in reversed(all_books)
        if x.get("status") == "読了"
    ]

    if finished_books_list:

        for book in finished_books_list[:5]:
            home_book_card(
                book,
                icon="🏆"
            )

    else:

        st.info(
            "まだ読了した本はありません📚"
        )

    st.markdown("---")

    # 読書継続記録
    st.subheader("🔥 読書継続記録")

    read_days = len(
        set(
            book.get("date", "")
            for book in all_books
            if book.get("date", "")
        )
    )

    if read_days > 0:

        st.success(
            f"📚 記録した読書日：{read_days}日"
        )

        st.caption(
            "まずは読書を記録する習慣を育てていきましょう。"
        )

    else:

        st.info(
            "読書記録をつけると、ここに継続記録が表示されます🔥"
        )

    st.markdown("---")

    st.markdown("---")

    # =========================
    # 読書カレンダー
    # =========================
    st.subheader("📅 今月の読書カレンダー")

    today = datetime.now()
    current_month = today.strftime("%Y/%m")

    read_dates = set(
        book.get("date", "")
        for book in all_books
        if book.get("date", "").startswith(current_month)
    )

    calendar_days = []

    for day in range(1, 32):

        date_key = f"{current_month}/{day:02d}"

        if date_key in read_dates:
            calendar_days.append(f"{day}📚")
        else:
            calendar_days.append(f"{day}□")

    for i in range(0, 31, 7):
        st.write(" ".join(calendar_days[i:i + 7]))

    st.caption(
        "📚 は読書記録をつけた日です。"
    )

    # 読了率
    st.subheader("🎯 読了率")

    if total_books > 0:
        finish_rate = int(
            finished_books / total_books * 100
        )

    else:
        finish_rate = 0

    st.progress(
        finish_rate / 100
    )

    st.write(
        f"現在の読了率：**{finish_rate}%**"
    )

    st.markdown("---")

    # 今読んでいる本
    st.subheader("📖 今読んでいる本")

    reading_books = [
        x
        for x in all_books
        if x.get("status") == "読書中"
    ]

    if reading_books:

        for book in reading_books[:3]:
            home_book_card(
                book,
                icon="📖"
            )

    else:

        st.info(
            "読書中の本はありません📚"
        )

    st.markdown("---")

    # 次に読みたい本
    st.subheader("🌱 次に読みたい本")

    want_books = [
        x
        for x in all_books
        if x.get("status") == "気になる"
    ]

    if want_books:

        for book in want_books[:5]:
            home_book_card(
                book,
                icon="🌱"
            )

    else:

        st.info(
            "気になる本はありません🌱"
        )

    st.markdown("---")

    # 最近追加した本
    st.subheader("🆕 最近追加した本")

    recent_books = list(
        reversed(all_books)
    )

    if recent_books:

        for book in recent_books[:5]:
            home_book_card(
                book,
                icon="🆕"
            )

    else:

        st.info(
            "まだ本が登録されていません📚"
        )

    st.markdown("---")

    # 月別読書数
    st.subheader("📊 月別読書数")

    monthly_stats = {}

    for book in all_books:

        date_str = book.get(
            "date",
            ""
        )

        if not date_str:
            continue

        month = date_str[:7]

        monthly_stats[month] = (
            monthly_stats.get(month, 0) + 1
        )

    if monthly_stats:

        for month, count in sorted(
            monthly_stats.items(),
            reverse=True
        ):

            st.write(
                f"📚 {month} ： {count}冊"
            )

    else:

        st.info(
            "まだ読書データがありません📊"
        )

    st.markdown("---")

    # お気に入り分析
    st.subheader("❤️ お気に入り分析")

    favorite_books = [
        book
        for book in all_books
        if book.get("favorite", False)
    ]

    if favorite_books:

        st.write(
            f"お気に入り登録：**{len(favorite_books)}冊**"
        )

        status_count = {}

        for book in favorite_books:

            status = book.get(
                "status",
                "不明"
            )

            status_count[status] = (
                status_count.get(status, 0) + 1
            )

        for status, count in status_count.items():

            st.write(
                f"{status}：{count}冊"
            )

        st.caption(
            "お気に入りが増えるほど、あなたの読書傾向が見えてきます。"
        )

    else:

        st.info(
            "お気に入りの本はまだありません❤️"
        )

    st.markdown("---")

    # 今日のおすすめ本
    st.subheader("🥇 今日のおすすめ本")

    candidate_books = [
        book
        for book in all_books
        if book.get("status") in ["気になる", "読書中"]
    ]

    if not candidate_books:
        candidate_books = all_books

    if candidate_books:

        today_book = random.choice(
            candidate_books
        )

        home_book_card(
            today_book,
            icon="🥇"
        )

        st.caption(
            "今日はこの一冊に少し触れてみるのもいいかもしれません📚"
        )

    else:

        st.info(
            "本を登録すると、今日のおすすめが表示されます📚"
        )

    st.markdown("---")

    st.markdown("---")

    st.subheader("🏆 実績")

    finished_count = len(
        [
            x
            for x in st.session_state.reading_log
            if x.get("status") == "読了"
        ]
    )

    achievements = []

    if finished_count >= 1:
        achievements.append("📚 初めての一冊")

    if finished_count >= 5:
        achievements.append("📖 読書ビギナー")

    if finished_count >= 10:
        achievements.append("🏆 読書家")

    if finished_count >= 30:
        achievements.append("👑 本の賢者")
    if finished_count >= 50:
        achievements.append("🌟 読書マスター")

    if finished_count >= 100:
        achievements.append("💎 伝説の読書家")

    favorite_count = len(
        [
            x
            for x in st.session_state.reading_log
            if x.get("favorite", False)
        ]
    )

    if favorite_count >= 5:
        achievements.append("⭐ 推し本コレクター")
    if favorite_count >= 10:
        achievements.append("⭐⭐ 推し本マスター")

    read_days = len(
        set(
            book.get("date", "")
            for book in st.session_state.reading_log
            if book.get("date", "")
        )
    )

    if read_days >= 3:
        achievements.append("📅 読書習慣スタート")

    if read_days >= 7:
        achievements.append("🔥 読書継続マスター")

    if achievements:

        for achievement in achievements:

            st.markdown(
                f"""
            <div class="scene-card">
            <div class="scene-title">🏆 実績解除</div>
            {achievement}
            </div>
            """,
                unsafe_allow_html=True,
            )

    else:

        st.info(
            "まだ実績はありません📚"
        )

    st.markdown("### 🔒 次の実績")

    locked_achievements = []

    if finished_count < 1:
        locked_achievements.append(
            f"📚 初めての一冊：あと {1 - finished_count}冊"
        )

    if finished_count < 5:
        locked_achievements.append(
            f"📖 読書ビギナー：あと {5 - finished_count}冊"
        )

    if finished_count < 10:
        locked_achievements.append(
            f"🏆 読書家：あと {10 - finished_count}冊"
        )

    if finished_count < 30:
        locked_achievements.append(
            f"👑 本の賢者：あと {30 - finished_count}冊"
        )

    if favorite_count < 5:
        locked_achievements.append(
            f"⭐ 推し本コレクター：あと {5 - favorite_count}冊"
        )

    if finished_count < 50:
        locked_achievements.append(
            f"🌟 読書マスター：あと {50 - finished_count}冊"
        )

    if finished_count < 100:
        locked_achievements.append(
            f"💎 伝説の読書家：あと {100 - finished_count}冊"
        )

    if favorite_count < 10:
        locked_achievements.append(
            f"⭐⭐ 推し本マスター：あと {10 - favorite_count}冊"
        )

    if read_days < 3:
        locked_achievements.append(
            f"📅 読書習慣スタート：あと {3 - read_days}日"
        )

    if read_days < 7:
        locked_achievements.append(
            f"🔥 読書継続マスター：あと {7 - read_days}日"
        )

    if locked_achievements:

        for item in locked_achievements:
            st.markdown(
                f"""
            <div class="scene-card">
            <div class="scene-title">🔒 次の実績</div>
            {item}
            </div>
            """,
    unsafe_allow_html=True,
)

    else:
        st.success("🎉 すべての実績を達成しています！")

    # 今月の読書目標
    st.subheader("🎯 今月の読書目標")

    monthly_goal = 5
    finished_count = finished_books

    progress = min(
        finished_count / monthly_goal,
        1.0
    )

    st.write(
        f"今月の目標：**{monthly_goal}冊**"
    )

    st.progress(progress)

    st.write(
        f"読了：**{finished_count}冊 / {monthly_goal}冊**"
    )

    if finished_count >= monthly_goal:
        st.success(
            "🎉 今月の読書目標を達成しました！"
        )
    else:
        st.info(
            "少しずつ読んでいこう📚"
        )

# =========================================
# 本を探すページ
# =========================================
if page == "🔍 本を探す":

    st.markdown(
        f"""
<div class="hero">
<div class="beta-badge">AI本屋さん β版 ✨</div>
<div class="main-title">📚 本を探す</div>
<div class="sub-text">
いまの気分をそのまま教えてください。<br>
小さな本屋さんのように、あなたに合いそうな一冊を一緒に探します。
</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
<div class="scene-card">
<div class="scene-title">🐰 うさぎ司書さん</div>
こんにちは。今日はどんな本を探しましょう？<br>
「元気がほしい」「ねる前に読みたい」「親子で読める本」みたいに、気軽に書いてください。
</div>
""",
        unsafe_allow_html=True,
    )

    # 初回説明
    if not st.session_state.books:
        st.markdown(
            """
<div class="scene-card">
<div class="scene-title">今日はどんな本を探してみる？📚</div>
ふわっとした気分でも大丈夫。<br>
「元気が出る本」「夜に読みたい小説」「未来にワクワクする本」みたいに、<br>
今の気持ちをそのまま書いてください。
</div>
""",
            unsafe_allow_html=True,
        )

    # 気分カード
    st.markdown(
        """
<div class="mood-card">
<div class="scene-title">🐰 気分からえらぶ</div>
今日はどんな本と出会いたい？<br>
ボタンを押すと、ぴったりの言葉が入力されます。
</div>
""",
        unsafe_allow_html=True,
    )

    # 気分ボタン
    m1, m2 = st.columns(2)
    m3, m4 = st.columns(2)

    with m1:
        st.button(
            "🌱 ほっとしたい",
            use_container_width=True,
            on_click=set_mood_text,
            args=("最近少し疲れているので、心が軽くなる本が読みたい",),
        )

    with m2:
        st.button(
            "🔥 元気がほしい",
            use_container_width=True,
            on_click=set_mood_text,
            args=("前向きになれて、行動したくなる本が読みたい",),
        )

    with m3:
        st.button(
            "🌙 物語の世界へ",
            use_container_width=True,
            on_click=set_mood_text,
            args=("静かに物語の世界に浸れる小説が読みたい",),
        )

    with m4:
        st.button(
            "🧠 学びたい",
            use_container_width=True,
            on_click=set_mood_text,
            args=("新しい知識や考え方を、難しすぎず学べる本が読みたい",),
        )

    # 入力例
    st.markdown(
        """
<div class="hint-box">
<b>入力例</b><br>

・前向きになれる本が読みたい<br>
・最近ちょっと疲れているから、心が軽くなる小説がいい<br>
・AIや未来について、難しすぎず学べる本を知りたい
</div>
""",
        unsafe_allow_html=True,
    )

    # =========================
    # 検索条件
    # =========================
    st.markdown(
        """
<div class="scene-card">
<div class="scene-title">🔍 検索条件</div>
もう少しだけ条件を選ぶと、本を探しやすくなります。
</div>
""",
        unsafe_allow_html=True,
    )

    filter_col1, filter_col2 = st.columns(2)

    with filter_col1:
        genre_filter = st.selectbox(
            "ジャンル",
            [
                "おまかせ",
                "小説",
                "実用書",
                "ビジネス",
                "自己啓発",
                "児童書",
                "学び",
            ],
            key="genre_filter"
        )

    with filter_col2:
        difficulty_filter = st.selectbox(
            "読みやすさ",
            [
                "おまかせ",
                "やさしい",
                "ふつう",
                "しっかり読みたい",
            ],
            key="difficulty_filter"
        )

    purpose_filter = st.selectbox(
        "読書目的",
        [
            "おまかせ",
            "元気になりたい",
            "癒されたい",
            "学びたい",
            "親子で読みたい",
            "行動したい",
            "物語に浸りたい",
        ],
        key="purpose_filter"
    )
    exclude_text = st.text_input(
        "除外したい条件（任意）",
        placeholder="例：難しい本、長編小説、ビジネス書",
        key="exclude_text"
    )
    if st.session_state.search_history:

        with st.expander("📜 最近の検索", expanded=False):

            for item in st.session_state.search_history:

                st.write(f"・{item}")
    # 入力欄
    user_input = st.text_area(
        "読みたい本のイメージ",
        placeholder="今の気分や、読みたいテーマを自由に書いてください。",
        height=110,
        key="main_input",
        label_visibility="collapsed",
    )

    # ボタン
    col1, col2 = st.columns([2, 1])

    with col1:
        search_clicked = st.button(
            "本を探す 📖",
            use_container_width=True,
        )

    with col2:
        clear_clicked = st.button(
            "クリア",
            use_container_width=True,
        )

    # クリア
    if clear_clicked:
        for key in [
            "books",
            "last_query",
            "last_message",
            "main_input",
            "extra_input",
        ]:
            if key in st.session_state:
                del st.session_state[key]

        st.rerun()

    # 検索
    if search_clicked:
        if not user_input.strip():
            st.warning("読みたい本のイメージを入力してください。")
        else:
            extra_condition = f"""
            ジャンル：{genre_filter}
            読みやすさ：{difficulty_filter}
            読書目的：{purpose_filter}

            除外条件：
            {exclude_text}
            """

            history_item = user_input.strip()

            if history_item not in st.session_state.search_history:
                st.session_state.search_history.insert(
                    0,
                    history_item
                )

            st.session_state.search_history = st.session_state.search_history[:5]

            search_books(
                user_input.strip(),
                extra=extra_condition
            )

    # 検索結果
    if st.session_state.books:
        st.markdown(
            f"""
<div class="mini-message">
{st.session_state.last_message or "今のあなたに合いそうな本を見つけました📚"}
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="result-title">おすすめの本</div>',
            unsafe_allow_html=True,
        )

        st.caption(
            f"入力内容：{st.session_state.last_query}"
        )

        for i, book in enumerate(st.session_state.books):
            render_book_card(book, i)

    # 更新履歴
    st.markdown("---")

    with st.expander("📚 β更新履歴"):
        st.markdown(
            """
**v0.2**
- 相性表示を追加
- 発行年の表示を追加
- Amazon / 楽天ブックスの検索リンクを追加
- AIの推薦ルールを少し調整

**v0.1**
- β版として公開
- 気分ボタンを追加
- 追加条件での再検索を追加
- やさしいUIに調整
"""
        )

    # フッター
    st.markdown(
        """
<div class="small-note">

このアプリは現在β版です📚
少しずつ改善・アップデートを行っています。<br>

※ 表紙画像・正確な発行日・価格・在庫確認・実在チェックは
今後追加予定です。<br>

※ AIの提案には誤りが含まれる可能性があります。
購入前に販売サイト等で最新情報をご確認ください。

</div>
""",
        unsafe_allow_html=True,
    )

# =========================================
# 本棚ページ
# =========================================
if page == "📚 本棚":

    st.markdown("## 📚 本棚")

    all_books = st.session_state.reading_log

    finished = [
        x for x in all_books
        if x.get("status") == "読了"
    ]

    avg = 0

    if all_books:
        avg = round(
            sum(x.get("rating", 0) for x in all_books) / len(all_books),
            1
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("📚 登録", len(all_books))

    with c2:
        st.metric("🏆 読了", len(finished))

    with c3:
        st.metric("⭐ 平均", avg)

    st.markdown("---")

    with st.expander("➕ 本を登録", expanded=False):

        st.caption("読んだ本・気になる本を記録します")

        title = st.text_input(
            "本のタイトル",
            key="log_title"
        )

        author = st.text_input(
            "著者",
            key="log_author"
        )

        status = st.selectbox(
            "読書状況",
            ["気になる", "読書中", "読了"],
            key="log_status"
        )

        rating = st.slider(
            "評価",
            1,
            5,
            3,
            key="log_rating"
        )

        memo = st.text_area(
            "感想",
            key="log_memo"
        )

        if st.button(
            "保存 📚",
            use_container_width=True
        ):

            if title:

                st.session_state.reading_log.append(
                    {
                        "title": title,
                        "author": author,
                        "status": status,
                        "rating": rating,
                        "memo": memo,
                        "date": datetime.now().strftime("%Y/%m/%d"),
                        "favorite": False,
                    }
                )

                save_reading_log(
                    st.session_state.reading_log
                )

                st.success("保存しました✨")
                st.rerun()

            else:

                st.warning(
                    "本のタイトルを入力してください。"
                )

    st.markdown("---")

    st.markdown(
        f"### 記録済み：{len(st.session_state.reading_log)}冊"
    )

    def render_book_list(status_name=None, favorite_only=False):

        if favorite_only:

            books = [
                (idx, book)
                for idx, book in enumerate(st.session_state.reading_log)
                if book.get("favorite", False)
            ]

        else:

            books = [
                (idx, book)
                for idx, book in enumerate(st.session_state.reading_log)
                if book.get("status") == status_name
            ]

        if not books:
            st.info("まだありません📚")
            return

        for idx, book in books:

            st.markdown(
                f"""
<div style="
background: #fffdf8;
border: 1px solid #eadfcf;
border-left: 10px solid #c89f68;
border-radius: 18px;
padding: 18px;
margin-bottom: 14px;
box-shadow: 0 6px 16px rgba(120, 90, 50, 0.08);
">

<div style="
font-size: 1.15rem;
font-weight: 900;
color: #4b3b2a;
margin-bottom: 8px;
">
📗 {book.get("title", "タイトル不明")}
</div>

<div style="color:#6f5c45; line-height:1.9;">
👤 著者：{book.get("author", "著者不明")}<br>
🌱 状態：{book.get("status", "不明")}<br>
⭐ 評価：{"⭐" * int(book.get("rating", 0))}<br>
📅 登録日：{book.get("date", "-")}<br>
{"❤️ お気に入り<br>" if book.get("favorite", False) else ""}
</div>

<div style="
margin-top: 12px;
padding: 12px;
background: #fff7ef;
border-radius: 12px;
color: #6f5c45;
line-height:1.8;
">
📝 感想：<br>
{book.get("memo", "")}
</div>

</div>
""",
                unsafe_allow_html=True,
            )

            # =========================
            # 操作ボタン
            # =========================
            move1, move2, move3 = st.columns(3)

            with move1:
                if st.button("🌱 気になる", key=f"move_want_{status_name}_{idx}", use_container_width=True):
                    st.session_state.reading_log[idx]["status"] = "気になる"
                    save_reading_log(st.session_state.reading_log)
                    st.rerun()

            with move2:
                if st.button("📖 読書中", key=f"move_reading_{status_name}_{idx}", use_container_width=True):
                    st.session_state.reading_log[idx]["status"] = "読書中"
                    save_reading_log(st.session_state.reading_log)
                    st.rerun()

            with move3:
                if st.button("🏆 読了", key=f"move_done_{status_name}_{idx}", use_container_width=True):
                    st.session_state.reading_log[idx]["status"] = "読了"
                    save_reading_log(st.session_state.reading_log)
                    st.balloons()
                    st.success("🎉 読了おめでとう！")
                    st.rerun()

            move4, move5 = st.columns(2)

            with move4:
                if st.button("⭐ 推し本", key=f"fav_{status_name}_{idx}", use_container_width=True):
                    current = book.get("favorite", False)
                    st.session_state.reading_log[idx]["favorite"] = not current
                    save_reading_log(st.session_state.reading_log)
                    st.rerun()

            with move5:
                if st.button("🗑 削除", key=f"delete_{status_name}_{idx}", use_container_width=True):
                    st.session_state.reading_log.pop(idx)
                    save_reading_log(st.session_state.reading_log)
                    st.rerun()

            st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "🌱 気になる",
            "📖 読書中",
            "🏆 読了",
            "❤️ お気に入り",
        ]
    )

    with tab1:
        render_book_list("気になる")

    with tab2:
        render_book_list("読書中")

    with tab3:
        render_book_list("読了")

    with tab4:
        render_book_list(favorite_only=True)
# =========================================
# このアプリについて
# =========================================
if page == "ℹ️ このアプリについて":

    st.markdown("## ℹ️ このアプリについて")

    st.markdown(
        """
        **次の一冊** は、  
        「今の気分に合う本を探したい」  
        「次に読む本を見つけたい」  
        という時に使える読書サポートアプリです。
        """
    )

    st.markdown("---")

    st.markdown("### 🤖 AIについて")

    st.markdown(
        """
        このアプリでは、AIを使って本の候補を提案しています。  
        そのため、提案内容には誤りや古い情報が含まれる場合があります。

        本を購入する前には、Amazon・楽天ブックス・出版社公式サイトなどで  
        最新情報をご確認ください。
        """
    )

    st.markdown("---")

    st.markdown("### 👪 子どもの利用について")

    st.markdown(
        """
        子どもでも使いやすい読書アプリを目指しています。  
        ただし、AIの提案や販売サイトへの移動を含むため、  
        お子さまが利用する場合は保護者の方と一緒の利用をおすすめします。
        """
    )

    st.markdown("---")

    st.markdown("### 💰 広告・有料プランについて")

    st.markdown(
        """
        AIを利用する機能には運営側に費用がかかります。  
        そのため、今後の利用状況によっては、広告表示や有料プランを導入する可能性があります。

        できるだけ使いやすく、安心して楽しめる形を目指して改善していきます。
        """
    )

    st.markdown("---")

    st.markdown("### 🚧 今後追加したい機能")

    st.markdown(
        """
        - 表紙画像の表示
        - 読書目標
        - 月別読書数
        - お気に入り傾向の分析
        - スマホアプリ化
        - 子ども向けモード
        - もっとかわいいUI
        """
    )
