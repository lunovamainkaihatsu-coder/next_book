import os
import json
import random
from typing import List, Dict

import streamlit as st

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


# =========================
# 基本設定
# =========================
st.set_page_config(
    page_title="次の一冊 β",
    page_icon="📚",
    layout="centered",
)

APP_TITLE = "次の一冊"


# =========================
# CSS
# =========================
st.markdown(
    """
    <style>
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
        font-weight: 800;
        color: #3f3a4a;
        margin-bottom: 8px;
        letter-spacing: 0.03em;
    }

    .sub-text {
        font-size: 1rem;
        color: #756b80;
        line-height: 1.85;
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
        font-weight: 800;
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
    }

    .stButton > button {
        border-radius: 999px;
        border: none;
        background: linear-gradient(90deg, #f6a9c8, #8fb7ff);
        color: white;
        font-weight: 700;
        padding: 0.72rem 1rem;
        box-shadow: 0 5px 14px rgba(120, 120, 180, 0.16);
    }

    .stButton > button:hover {
        opacity: 0.92;
        color: white;
        border: none;
    }

    .result-title {
        font-size: 1.38rem;
        font-weight: 800;
        color: #3f3a4a;
        margin-top: 26px;
        margin-bottom: 8px;
    }

    .book-card {
        background: rgba(255,255,255,0.94);
        padding: 22px 24px;
        border-radius: 26px;
        border: 1px solid #f0dce7;
        box-shadow: 0 10px 24px rgba(120, 90, 130, 0.075);
        margin-bottom: 18px;
    }

    .book-title {
        font-size: 1.25rem;
        font-weight: 800;
        color: #3f3a4a;
        margin-bottom: 6px;
    }

    .book-meta {
        font-size: 0.9rem;
        color: #8a8190;
        margin-bottom: 12px;
    }

    .book-section {
        margin-top: 12px;
        color: #554f5d;
        line-height: 1.78;
        font-size: 0.96rem;
    }

    .book-label {
        font-weight: 800;
        color: #6b5c78;
    }

    .pill {
        display: inline-block;
        padding: 5px 11px;
        border-radius: 999px;
        background: #fff0f6;
        color: #8d5570;
        font-size: 0.82rem;
        font-weight: 700;
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
    }

    .small-note {
        font-size: 0.85rem;
        color: #9a92a0;
        text-align: center;
        margin-top: 28px;
        line-height: 1.8;
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
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
        "本棚を歩き回っています... 📚",
        "ぴったりの一冊を探しています... ✨",
        "ページをめくっています... 📖",
        "物語の世界を探索中です... 🌙",
        "今の気分に合う本を選んでいます... ☕",
        "静かな本屋さんを巡っています... 🕯️",
    ])


def set_mood_text(text: str):
    st.session_state.main_input = text


def build_prompt(user_input: str, extra_condition: str = "") -> str:
    condition_text = f"\n追加条件: {extra_condition}" if extra_condition else ""

    return f"""
あなたは本の推薦アシスタントです。
ユーザーの自然文を読み取り、実在する日本語書籍を優先して、おすすめの本を3冊提案してください。

ルール:
- 対象は「実用書」または「小説」のみ
- 漫画、イラスト集、雑誌、成人向けは除外
- なるべく実在する有名・流通している本を選ぶ
- 日本語の読者が読みやすい本を優先
- ユーザーの気分や状況を読み取り、それに寄り添う
- 「なぜ今この本なのか」を説明する
- 同じ理由の使い回しを避ける
- 1冊は読みやすい本、1冊は少し深い本、1冊は意外性のある本を混ぜる
- 押し付けず、やさしく提案する
- 静かな本屋やカフェで相談しているような、落ち着いた文体にする
- 出力はJSONのみ
- JSONのキーは以下に厳密に合わせること:
  title, author, genre, difficulty, mood, reading_time, after_feeling, reason, for_who, comment
- difficulty は「やさしい」「ふつう」「深い」のいずれか
- genre は「実用書」または「小説」
- mood は「どんな気分の時に合う本か」を短く書く
- reading_time は「どんなタイミングで読みたいか」を短く書く
- after_feeling は「読後感」を短く書く

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
    with st.spinner(get_loading_message()):
        st.session_state.books = get_books_from_openai(query, extra_condition=extra)
        st.session_state.last_query = query
        st.session_state.last_message = message


def render_book_card(book: Dict):
    title = book.get("title", "タイトル不明")
    author = book.get("author", "著者不明")
    genre = book.get("genre", "不明")
    difficulty = book.get("difficulty", "不明")
    mood = book.get("mood", "今の気分に合いそう")
    reading_time = book.get("reading_time", "ゆっくり読める時に")
    after_feeling = book.get("after_feeling", "余韻が残る")
    reason = book.get("reason", "")
    for_who = book.get("for_who", "")
    comment = book.get("comment", "")
    icon = difficulty_icon(difficulty)

    st.markdown(
        f"""
        <div class="book-card">
            <div class="book-title">📗 {title}</div>
            <div class="book-meta">著者：{author}</div>
            <div>
                <span class="pill">{genre}</span>
                <span class="pill">{icon} {difficulty}</span>
                <span class="pill">☕ {mood}</span>
                <span class="pill">🕯️ {reading_time}</span>
                <span class="pill">🌙 {after_feeling}</span>
            </div>
            <div class="book-section">
                <span class="book-label">📚 今のあなたに合いそうな理由</span><br>
                {reason}
            </div>
            <div class="book-section">
                <span class="book-label">🌱 向いている人</span><br>
                {for_who}
            </div>
            <div class="book-section">
                <span class="book-label">💬 ひとこと</span><br>
                {comment}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# UI
# =========================
st.markdown(
    f"""
    <div class="hero">
        <div class="beta-badge">β版開発中 ✨</div>
        <div class="main-title">📚 {APP_TITLE}</div>
        <div class="sub-text">
            いま読みたい気分をそのまま書くだけ。<br>
            静かな本屋さんのように、AIがあなたに合いそうな本を探します。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.books:
    st.markdown(
        """
        <div class="scene-card">
            <div class="scene-title">今日はどんな本を探してみる？📚</div>
            ふわっとした気分でも大丈夫。<br>
            「元気が出る本」「夜に読みたい小説」「未来にワクワクする本」みたいに、
            今の気持ちをそのまま書いてください。
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div class="mood-card">
        <div class="scene-title">気分から選ぶ</div>
        ボタンを押すと、入力欄におすすめの言葉が入ります。
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2 = st.columns(2)
m3, m4 = st.columns(2)

with m1:
    st.button("🌱 癒されたい", use_container_width=True, on_click=set_mood_text, args=("最近少し疲れているので、心が軽くなる本が読みたい",))
with m2:
    st.button("🔥 やる気がほしい", use_container_width=True, on_click=set_mood_text, args=("前向きになれて、行動したくなる本が読みたい",))
with m3:
    st.button("🌙 物語に浸りたい", use_container_width=True, on_click=set_mood_text, args=("静かに物語の世界に浸れる小説が読みたい",))
with m4:
    st.button("🧠 学びたい", use_container_width=True, on_click=set_mood_text, args=("新しい知識や考え方を、難しすぎず学べる本が読みたい",))

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

user_input = st.text_area(
    "読みたい本のイメージ",
    placeholder="今の気分や、読みたいテーマを自由に書いてください。",
    height=145,
    key="main_input",
    label_visibility="collapsed",
)

col1, col2 = st.columns([2, 1])

with col1:
    search_clicked = st.button("本を探す 📖", use_container_width=True)

with col2:
    clear_clicked = st.button("クリア", use_container_width=True)


if clear_clicked:
    st.session_state.books = []
    st.session_state.last_query = ""
    st.session_state.last_message = ""
    st.session_state.main_input = ""
    st.session_state.extra_input = ""
    st.rerun()


if search_clicked:
    if not user_input.strip():
        st.warning("読みたい本のイメージを入力してください。")
    else:
        search_books(user_input.strip())


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

    st.caption(f"入力内容：{st.session_state.last_query}")

    for book in st.session_state.books:
        render_book_card(book)

    st.markdown("#### 条件を少し変えて探す")

    extra_input = st.text_input(
        "追加で希望があれば入力してください",
        placeholder="例：もっと最近の本 / 暗すぎない小説 / もっと読みやすい本",
        key="extra_input",
    )

    if st.button("追加条件で探し直す ✨", use_container_width=True):
        if not extra_input.strip():
            st.warning("追加したい条件を入力してください。")
        else:
            search_books(
                st.session_state.last_query,
                extra=extra_input.strip(),
                message=f"「{extra_input.strip()}」の条件で探し直しました✨",
            )
            st.rerun()

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    if c1.button("🌱 もっとやさしい本", use_container_width=True):
        search_books(
            st.session_state.last_query,
            extra="もっとやさしい本を優先してください",
            message="少しやさしめの本を探し直しました🌱",
        )
        st.rerun()

    if c2.button("🌙 小説寄りにする", use_container_width=True):
        search_books(
            st.session_state.last_query,
            extra="小説を優先してください",
            message="物語に寄せて探し直しました🌙",
        )
        st.rerun()

    if c3.button("🧠 実用書だけにする", use_container_width=True):
        search_books(
            st.session_state.last_query,
            extra="実用書のみを提案してください",
            message="実用書を中心に探し直しました🧠",
        )
        st.rerun()

    if c4.button("🔥 もう少し深い内容", use_container_width=True):
        search_books(
            st.session_state.last_query,
            extra="より深く考えられる本を優先してください",
            message="少し深めの本を探し直しました🔥",
        )
        st.rerun()


st.markdown(
    """
    <div class="small-note">
    このアプリは現在β版です📚 少しずつ改善・アップデートを行っています。<br>
    ※ 表紙画像・発行日・価格・Amazonリンク・実在チェックは今後追加予定です。<br>
    ※ AIの提案には誤りが含まれる可能性があります。購入前に販売サイト等で最新情報をご確認ください。
    </div>
    """,
    unsafe_allow_html=True,
)
