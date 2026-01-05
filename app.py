import streamlit as st
import os

# --- ページ設定 ---
st.set_page_config(page_title="花札（花合わせ）得点計算ツール", page_icon="🎴", layout="wide")

# --- CSSでの見た目調整 ---
st.markdown("""
<style>
    /* カードコンテナの調整 */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        padding: 10px !important;
    }
    /* st.pillsの調整（少し小さくして並びやすくする） */
    div[data-testid="stPills"] button {
        padding: 4px 8px !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- セッション状態の初期化 ---
if 'page' not in st.session_state:
    st.session_state.page = 'start_screen'
if 'player_names' not in st.session_state:
    st.session_state.player_names = ["Aさん", "Bさん", "Cさん"]
if 'selections' not in st.session_state:
    st.session_state.selections = {}

# --- 1. カードデータの定義 ---
# (月, 種類, 点数, 表示名, ID, ソート用種類ID)
# 種類ID: 0=光, 1=タネ, 2=短冊, 3=カス
card_data = [
    # 1月 マツ
    ("1月", "光", 20, "松に鶴", "matsu_hikari", 0),
    ("1月", "短冊", 5, "松に赤短", "matsu_tan", 2),
    ("1月", "カス", 1, "松のカス1", "matsu_kasu_1", 3),
    ("1月", "カス", 1, "松のカス2", "matsu_kasu_2", 3),
    # 2月 ウメ
    ("2月", "タネ", 10, "梅に鶯", "ume_tane", 1),
    ("2月", "短冊", 5, "梅に赤短", "ume_tan", 2),
    ("2月", "カス", 1, "梅のカス1", "ume_kasu_1", 3),
    ("2月", "カス", 1, "梅のカス2", "ume_kasu_2", 3),
    # 3月 サクラ
    ("3月", "光", 20, "桜に幕", "sakura_hikari", 0),
    ("3月", "短冊", 5, "桜に赤短", "sakura_tan", 2),
    ("3月", "カス", 1, "桜のカス1", "sakura_kasu_1", 3),
    ("3月", "カス", 1, "桜のカス2", "sakura_kasu_2", 3),
    # 4月 フジ
    ("4月", "タネ", 10, "藤にホトトギス", "fuji_tane", 1),
    ("4月", "短冊", 5, "藤の短冊", "fuji_tan", 2),
    ("4月", "カス", 1, "藤のカス1", "fuji_kasu_1", 3),
    ("4月", "カス", 1, "藤のカス2", "fuji_kasu_2", 3),
    # 5月 アヤメ
    ("5月", "タネ", 10, "菖蒲に八橋", "ayame_tane", 1),
    ("5月", "短冊", 5, "菖蒲の青短", "ayame_tan", 2),
    ("5月", "カス", 1, "菖蒲のカス1", "ayame_kasu_1", 3),
    ("5月", "カス", 1, "菖蒲のカス2", "ayame_kasu_2", 3),
    # 6月 ボタン
    ("6月", "タネ", 10, "牡丹に蝶", "botan_tane", 1),
    ("6月", "短冊", 5, "牡丹の青短", "botan_tan", 2),
    ("6月", "カス", 1, "牡丹のカス1", "botan_kasu_1", 3),
    ("6月", "カス", 1, "牡丹のカス2", "botan_kasu_2", 3),
    # 7月 ハギ
    ("7月", "タネ", 10, "萩に猪", "hagi_tane", 1),
    ("7月", "短冊", 5, "萩の短冊", "hagi_tan", 2),
    ("7月", "カス", 1, "萩のカス1", "hagi_kasu_1", 3),
    ("7月", "カス", 1, "萩のカス2", "hagi_kasu_2", 3),
    # 8月 ススキ
    ("8月", "光", 20, "ススキに月", "susuki_hikari", 0),
    ("8月", "タネ", 10, "ススキに雁", "susuki_tane", 1),
    ("8月", "カス", 1, "ススキのカス1", "susuki_kasu_1", 3),
    ("8月", "カス", 1, "ススキのカス2", "susuki_kasu_2", 3),
    # 9月 キク
    ("9月", "タネ", 10, "菊に盃", "kiku_tane", 1),
    ("9月", "短冊", 5, "菊の青短", "kiku_tan", 2),
    ("9月", "カス", 1, "菊のカス1", "kiku_kasu_1", 3),
    ("9月", "カス", 1, "菊のカス2", "kiku_kasu_2", 3),
    # 10月 モミジ
    ("10月", "タネ", 10, "紅葉に鹿", "momiji_tane", 1),
    ("10月", "短冊", 5, "紅葉の青短", "momiji_tan", 2),
    ("10月", "カス", 1, "紅葉のカス1", "momiji_kasu_1", 3),
    ("10月", "カス", 1, "紅葉のカス2", "momiji_kasu_2", 3),
    # 11月 ヤナギ
    ("11月", "光", 20, "柳に小野道風", "yanagi_hikari", 0),
    ("11月", "タネ", 10, "柳に燕", "yanagi_tane", 1),
    ("11月", "短冊", 5, "柳の短冊", "yanagi_tan", 2),
    ("11月", "カス", 1, "柳のカス(雷)", "yanagi_kasu", 3),
    # 12月 キリ
    ("12月", "光", 20, "桐に鳳凰", "kiri_hikari", 0),
    ("12月", "カス", 1, "桐のカス1", "kiri_kasu_1", 3),
    ("12月", "カス", 1, "桐のカス2", "kiri_kasu_2", 3),
    ("12月", "カス", 1, "桐のカス3", "kiri_kasu_3", 3),
]

# --- 2. 役判定ロジック ---
def calculate_score(cards):
    points = sum(c[2] for c in cards)
    card_ids = set(c[4] for c in cards)
    yaku_list = []
    yaku_score = 0
    
    hikari_ids = {c[4] for c in cards if c[1] == "光"}
    
    # 五光, 四光, 雨四光, 三光
    if len(hikari_ids) == 5:
        yaku_list.append("五光 (200貫)")
        yaku_score += 200
    elif len(hikari_ids) == 4 and "yanagi_hikari" not in hikari_ids:
        yaku_list.append("四光 (60貫)")
        yaku_score += 60
    elif len(hikari_ids) == 4 and "yanagi_hikari" in hikari_ids:
        yaku_list.append("雨四光 (40貫)")
        yaku_score += 40
    elif len(hikari_ids) == 3 and "yanagi_hikari" not in hikari_ids:
        yaku_list.append("三光 (30貫)")
        yaku_score += 30
    
    # 猪鹿蝶
    if {"hagi_tane", "momiji_tane", "botan_tane"}.issubset(card_ids):
        yaku_list.append("猪鹿蝶 (20貫)")
        yaku_score += 20
        
    # 赤短, 青短, 草短
    if {"matsu_tan", "ume_tan", "sakura_tan"}.issubset(card_ids):
        yaku_list.append("赤短 (40貫)")
        yaku_score += 40
    if {"botan_tan", "kiku_tan", "momiji_tan"}.issubset(card_ids):
        yaku_list.append("青短 (40貫)")
        yaku_score += 40
    if {"fuji_tan", "ayame_tan", "hagi_tan"}.issubset(card_ids):
        yaku_list.append("草短 (20貫)")
        yaku_score += 20

    # 飲み
    if {"sakura_hikari", "susuki_hikari", "kiku_tane"}.issubset(card_ids):
         yaku_list.append("飲み (30貫)")
         yaku_score += 30
    else:
        if {"sakura_hikari", "kiku_tane"}.issubset(card_ids):
            yaku_list.append("花見で一杯 (20貫)")
            yaku_score += 20
        if {"susuki_hikari", "kiku_tane"}.issubset(card_ids):
            yaku_list.append("月見で一杯 (20貫)")
            yaku_score += 20

    return points, yaku_score, yaku_list

# --- 画面関数: ルール確認 ---
def show_rules_screen():
    st.title("📖 ルールと役の確認")
    st.markdown("""
    本ツールは、以下の任天堂公式サイトのルールを参考に作成しています。  
    [任天堂「花合わせ」ルール](https://www.nintendo.com/jp/others/hanafuda_kabufuda/howtoplay/hanaawase/index.html)
    """)
    
    st.header("🎴 点数（カードの種類）")
    c1, c2, c3, c4 = st.columns(4)
    c1.info("**光 (20点)**\n\n鶴・幕・月・道風・鳳凰")
    c2.success("**タネ (10点)**\n\n鶯・杜鵑・八橋・蝶・猪・雁・盃・鹿・燕")
    c3.warning("**短冊 (5点)**\n\n赤短・青短・その他")
    c4.error("**カス (1点)**\n\n上記以外の札")

    st.header("🀄 出来役一覧")
    yaku_data = [
        ("五光 (200貫)", "光札5枚すべて"),
        ("四光 (60貫)", "光札4枚 (小野道風を含まない)"),
        ("雨四光 (40貫)", "光札4枚 (小野道風を含む)"),
        ("三光 (30貫)", "光札3枚 (小野道風を含まない)"),
        ("猪鹿蝶 (20貫)", "萩に猪・紅葉に鹿・牡丹に蝶"),
        ("赤短 (40貫)", "松・梅・桜の短冊3枚"),
        ("青短 (40貫)", "牡丹・菊・紅葉の短冊3枚"),
        ("草短 (20貫)", "藤・菖蒲・萩の短冊3枚"),
        ("飲み (30貫)", "桜に幕・ススキに月・菊に盃の3枚"),
    ]
    for name, cond in yaku_data:
        with st.container():
            st.markdown(f"**{name}** | {cond}")
            st.divider()

    if st.button("タイトル画面に戻る", type="primary"):
        st.session_state.page = 'start_screen'
        st.rerun()

# --- 画面関数: スタート画面 ---
def show_start_screen():
    st.title("🎴 花合わせ計算ツール")
    st.markdown("""
    <div style="font-size: 14px; color: gray; margin-bottom: 20px;">
    ルール参照： <a href="https://www.nintendo.com/jp/others/hanafuda_kabufuda/howtoplay/hanaawase/index.html" target="_blank">任天堂「花合わせ」公式サイト</a>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("プレイヤー設定")
    with st.form("name_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            name1 = st.text_input("1人目", value=st.session_state.player_names[0])
        with col2:
            name2 = st.text_input("2人目", value=st.session_state.player_names[1])
        with col3:
            name3 = st.text_input("3人目", value=st.session_state.player_names[2])
        
        c1, c2 = st.columns([1, 1])
        with c1:
            submitted = st.form_submit_button("計算を始める", type="primary", use_container_width=True)
        
    if st.button("📖 ルールの確認", use_container_width=True):
        st.session_state.page = 'rules_screen'
        st.rerun()
        
    if submitted:
        st.session_state.player_names = [name1, name2, name3]
        st.session_state.page = 'game_screen'
        st.rerun()

    st.divider()
    # 免責事項（タイトル画面）
    st.caption("※免責事項：本ツールの計算結果において万が一誤りがあった場合でも、製作者は一切の責任を負いません。最終的な判断はプレイヤー間で行ってください。")

# --- 画面関数: 計算画面 ---
def show_game_screen():
    st.title("🎴 獲得札の選択")
    p_names = st.session_state.player_names
    options = ["未"] + p_names
    
    categories = {
        "光 (20点)": [c for c in card_data if c[5] == 0],
        "タネ (10点)": [c for c in card_data if c[5] == 1],
        "短冊 (5点)": [c for c in card_data if c[5] == 2],
        "カス (1点)": [c for c in card_data if c[5] == 3],
    }

    tabs = st.tabs(categories.keys())

    for tab, (cat_name, cards) in zip(tabs, categories.items()):
        with tab:
            cols = st.columns(4)
            for i, (month, type_, point, name, id_, sort_id) in enumerate(cards):
                with cols[i % 4]:
                    with st.container(border=True):
                        # 画像の幅を適切に固定 (70px)
                        image_path = f"images/{id_}.png"
                        if os.path.exists(image_path):
                            st.image(image_path, width=70)
                        else:
                            st.markdown(f"**{name}**")
                        
                        # デフォルト選択状態の復元
                        default_idx = 0
                        if id_ in st.session_state.selections:
                             current_sel = st.session_state.selections[id_]
                             if current_sel in options:
                                default_idx = options.index(current_sel)
                        
                      # st.radio に戻す（古いバージョン対応）
                        selection = st.radio(
                            f"{name}の所有者",
                            options,
                            index=default_idx,
                            key=f"radio_{id_}", # キーを一応変更
                            label_visibility="collapsed",
                            horizontal=True # 横並びにする
                        )
                        st.session_state.selections[id_] = selection

    st.divider()

    col_calc, col_reset = st.columns([3, 1])
    with col_calc:
        if st.button("🧮 結果を計算する", type="primary", use_container_width=True):
            p_cards = {name: [] for name in p_names}
            for card in card_data:
                id_ = card[4]
                owner = st.session_state.selections.get(id_, "未")
                if owner in p_names:
                    p_cards[owner].append(card)
            
            st.header("🏆 集計結果")
            
            total_yaku_points_all = 0
            temp_results = {}
            for p_name in p_names:
                fuda, yaku, yakus = calculate_score(p_cards[p_name])
                temp_results[p_name] = {'fuda': fuda, 'yaku': yaku, 'yakus': yakus}
                total_yaku_points_all += yaku

            r_cols = st.columns(3)
            grand_total = 0
            
            for i, p_name in enumerate(p_names):
                r = temp_results[p_name]
                # 簡易計算式: (札点 - 88) + (自分の役点 * 2) - (他人の役点合計)
                others_yaku = total_yaku_points_all - r['yaku']
                final_score = (r['fuda'] - 88) + (r['yaku'] * 2) - others_yaku
                grand_total += final_score
                
                with r_cols[i]:
                    with st.container(border=True):
                        st.subheader(f"{p_name}")
                        st.metric("最終得点", f"{final_score} 点")
                        st.markdown(f"""
                        <small>札点: {r['fuda']} / 役点: {r['yaku']}</small>
                        """, unsafe_allow_html=True)
                        if r['yakus']:
                            st.markdown("---")
                            for y in r['yakus']:
                                st.success(y, icon="🀄")
                        else:
                            st.caption("役なし")

            if grand_total == 0:
                st.success("計算整合性 OK (合計0点)")
            else:
                st.warning(f"合計が {grand_total} 点です。選択漏れがないか確認してください。")
            
            # 免責事項（計算結果画面）
            st.caption("※免責事項：計算結果において万が一誤りがあった場合でも、製作者は一切の責任を負いません。")

    with col_reset:
        if st.button("タイトルへ戻る", use_container_width=True):
            st.session_state.page = 'start_screen'
            st.rerun()

# --- メイン実行部 ---
if st.session_state.page == 'start_screen':
    show_start_screen()
elif st.session_state.page == 'rules_screen':
    show_rules_screen()
elif st.session_state.page == 'game_screen':
    show_game_screen()



