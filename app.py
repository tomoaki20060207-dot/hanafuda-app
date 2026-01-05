import streamlit as st
import os

# ページ設定
st.set_page_config(page_title="花合わせ計算機", page_icon="🎴")

# --- セッション状態の初期化（画面遷移用） ---
if 'page' not in st.session_state:
    st.session_state.page = 'name_input' # 最初は名前入力画面
if 'player_names' not in st.session_state:
    st.session_state.player_names = ["Aさん", "Bさん", "Cさん"]

# --- 1. カードデータの定義 ---
# (月, 種類, 点数, 表示名, ID)
# IDは画像ファイル名としても使います (例: images/matsu_hikari.png)
card_data = [
    # 1月 マツ
    ("1月", "光", 20, "マツの光札(鶴)", "matsu_hikari"),
    ("1月", "短冊", 5, "マツの赤短", "matsu_tan"),
    ("1月", "カス", 1, "マツのカス(1)", "matsu_kasu_1"),
    ("1月", "カス", 1, "マツのカス(2)", "matsu_kasu_2"),
    # 2月 ウメ
    ("2月", "タネ", 10, "ウメのタネ札(鶯)", "ume_tane"),
    ("2月", "短冊", 5, "ウメの赤短", "ume_tan"),
    ("2月", "カス", 1, "ウメのカス(1)", "ume_kasu_1"),
    ("2月", "カス", 1, "ウメのカス(2)", "ume_kasu_2"),
    # 3月 サクラ
    ("3月", "光", 20, "サクラの光札(幕)", "sakura_hikari"),
    ("3月", "短冊", 5, "サクラの赤短", "sakura_tan"),
    ("3月", "カス", 1, "サクラのカス(1)", "sakura_kasu_1"),
    ("3月", "カス", 1, "サクラのカス(2)", "sakura_kasu_2"),
    # 4月 フジ
    ("4月", "タネ", 10, "フジのタネ札(杜鵑)", "fuji_tane"),
    ("4月", "短冊", 5, "フジの短冊", "fuji_tan"),
    ("4月", "カス", 1, "フジのカス(1)", "fuji_kasu_1"),
    ("4月", "カス", 1, "フジのカス(2)", "fuji_kasu_2"),
    # 5月 アヤメ
    ("5月", "タネ", 10, "アヤメのタネ札(八橋)", "ayame_tane"),
    ("5月", "短冊", 5, "アヤメの青短", "ayame_tan"),
    ("5月", "カス", 1, "アヤメのカス(1)", "ayame_kasu_1"),
    ("5月", "カス", 1, "アヤメのカス(2)", "ayame_kasu_2"),
    # 6月 ボタン
    ("6月", "タネ", 10, "ボタンのタネ札(蝶)", "botan_tane"),
    ("6月", "短冊", 5, "ボタンの青短", "botan_tan"),
    ("6月", "カス", 1, "ボタンのカス(1)", "botan_kasu_1"),
    ("6月", "カス", 1, "ボタンのカス(2)", "botan_kasu_2"),
    # 7月 ハギ
    ("7月", "タネ", 10, "ハギのタネ札(猪)", "hagi_tane"),
    ("7月", "短冊", 5, "ハギの短冊", "hagi_tan"),
    ("7月", "カス", 1, "ハギのカス(1)", "hagi_kasu_1"),
    ("7月", "カス", 1, "ハギのカス(2)", "hagi_kasu_2"),
    # 8月 ススキ
    ("8月", "光", 20, "ススキの光札(月)", "susuki_hikari"),
    ("8月", "タネ", 10, "ススキのタネ札(雁)", "susuki_tane"),
    ("8月", "カス", 1, "ススキのカス(1)", "susuki_kasu_1"),
    ("8月", "カス", 1, "ススキのカス(2)", "susuki_kasu_2"),
    # 9月 キク
    ("9月", "タネ", 10, "キクのタネ札(盃)", "kiku_tane"),
    ("9月", "短冊", 5, "キクの青短", "kiku_tan"),
    ("9月", "カス", 1, "キクのカス(1)", "kiku_kasu_1"),
    ("9月", "カス", 1, "キクのカス(2)", "kiku_kasu_2"),
    # 10月 モミジ
    ("10月", "タネ", 10, "モミジのタネ札(鹿)", "momiji_tane"),
    ("10月", "短冊", 5, "モミジの青短", "momiji_tan"),
    ("10月", "カス", 1, "モミジのカス(1)", "momiji_kasu_1"),
    ("10月", "カス", 1, "モミジのカス(2)", "momiji_kasu_2"),
    # 11月 ヤナギ
    ("11月", "光", 20, "ヤナギの光札(道風)", "yanagi_hikari"),
    ("11月", "タネ", 10, "ヤナギのタネ札(燕)", "yanagi_tane"),
    ("11月", "短冊", 5, "ヤナギの短冊", "yanagi_tan"),
    ("11月", "カス", 1, "ヤナギのカス(雷)", "yanagi_kasu"),
    # 12月 キリ
    ("12月", "光", 20, "キリの光札(鳳凰)", "kiri_hikari"),
    ("12月", "カス", 1, "キリのカス(1)", "kiri_kasu_1"),
    ("12月", "カス", 1, "キリのカス(2)", "kiri_kasu_2"),
    ("12月", "カス", 1, "キリのカス(3)", "kiri_kasu_3"),
]

# --- 2. 役判定ロジック ---
def calculate_score(cards):
    points = sum(c[2] for c in cards)
    card_ids = set(c[4] for c in cards)
    yaku_list = []
    yaku_score = 0
    
    # 判定用セット
    hikari_ids = {c[4] for c in cards if c[1] == "光"}
    tan_ids = {c[4] for c in cards if c[1] == "短冊"}
    
    # 五光 (200点)
    if len(hikari_ids) == 5:
        yaku_list.append("五光(200)")
        yaku_score += 200
    elif len(hikari_ids) == 4:
        yaku_list.append("四光(60)")
        yaku_score += 60
    
    # 七短 (40点)
    if len(tan_ids) >= 7:
        yaku_list.append("七短(40)")
        yaku_score += 40
    elif len(tan_ids) == 6:
        yaku_list.append("六短(30)")
        yaku_score += 30

    # 赤短・青短
    if {"matsu_tan", "ume_tan", "sakura_tan"}.issubset(card_ids):
        yaku_list.append("赤短(40)")
        yaku_score += 40
    if {"botan_tan", "kiku_tan", "momiji_tan"}.issubset(card_ids):
        yaku_list.append("青短(40)")
        yaku_score += 40
        
    # 猪鹿蝶
    if {"hagi_tane", "momiji_tane", "botan_tane"}.issubset(card_ids):
        yaku_list.append("猪鹿蝶(20)")
        yaku_score += 20
        
    # 月見・花見
    if {"sakura_hikari", "kiku_tane"}.issubset(card_ids):
        yaku_list.append("花見で一杯(20)")
        yaku_score += 20
    if {"susuki_hikari", "kiku_tane"}.issubset(card_ids):
        yaku_list.append("月見で一杯(20)")
        yaku_score += 20

    return points, yaku_score, yaku_list


# --- 画面A: 名前入力画面 ---
if st.session_state.page == 'name_input':
    st.title("🎴 花合わせ計算機")
    st.subheader("プレイヤーの名前を入力してください")
    
    with st.form("name_form"):
        name1 = st.text_input("1人目の名前", value="Aさん")
        name2 = st.text_input("2人目の名前", value="Bさん")
        name3 = st.text_input("3人目の名前", value="Cさん")
        
        submitted = st.form_submit_button("ゲームを始める")
        if submitted:
            # 名前を保存して画面を切り替え
            st.session_state.player_names = [name1, name2, name3]
            st.session_state.page = 'main_game'
            st.rerun()

# --- 画面B: 札選択画面 ---
elif st.session_state.page == 'main_game':
    st.title("🎴 持ち札の選択")
    
    # プレイヤー名を取得
    p_names = st.session_state.player_names
    # 選択肢: ["未", "〇〇", "△△", "××"]
    options = ["未"] + p_names
    
    # 入力データの保持用
    user_selections = {}

    current_month = ""
    for month, type_, point, name, id_ in card_data:
        if month != current_month:
            st.markdown(f"### {month}")
            current_month = month
        
        # 2列レイアウト（左：画像、右：ボタン）
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # 画像ファイルパス (例: images/matsu_hikari.png)
            # 拡張子は png や jpg に合わせて変更してください
            image_path = f"images/{id_}.png"
            
            # 画像があれば表示、なければプレースホルダー
            if os.path.exists(image_path):
                st.image(image_path, width=80)
            else:
                # 画像がない場合のダミー表示
                st.info("画像なし")

        with col2:
            user_selections[id_] = st.radio(
                label=f"{name}",
                options=options,
                horizontal=True,
                key=id_
            )
        st.divider()

    # 計算ボタン
    if st.button("計算する", type="primary"):
        # 1. 選択情報の収集
        p_cards = {p_names[0]: [], p_names[1]: [], p_names[2]: []}
        
        for month, type_, point, name, id_ in card_data:
            owner = user_selections[id_]
            if owner in p_cards:
                p_cards[owner].append((month, type_, point, name, id_))
        
        # 2. 計算
        results = {}
        total_yaku_score = 0
        
        for p_name in p_names:
            cards = p_cards[p_name]
            fuda_ten, yaku_ten, yakus = calculate_score(cards)
            results[p_name] = {'fuda': fuda_ten, 'yaku': yaku_ten, 'yakus': yakus}
            total_yaku_score += yaku_ten
            
        # 3. 結果表示
        st.header("🎴 集計結果")
        grand_total = 0
        
        cols = st.columns(3)
        for i, p_name in enumerate(p_names):
            r = results[p_name]
            others_yaku = total_yaku_score - r['yaku']
            final_score = (r['fuda'] - 88) + (r['yaku'] * 2) - others_yaku
            grand_total += final_score
            
            with cols[i]:
                st.subheader(f"{p_name}")
                st.metric(label="最終得点", value=f"{final_score:+}点")
                st.markdown(f"""
                <small>獲得枚数: {len(p_cards[p_name])}枚<br>
                札点: {r['fuda']}点<br>
                役: {', '.join(r['yakus']) if r['yakus'] else 'ナシ'}</small>
                """, unsafe_allow_html=True)

        st.divider()
        if grand_total == 0:
            st.success("✅ 計算完了！ 合計はピッタリ 0点 です。")
        else:
            st.error(f"⚠️ エラー: 合計が {grand_total}点 です。すべての札を正しく選択されましたか？")
    
    # 最初に戻るボタン
    if st.button("名前入力に戻る"):
        st.session_state.page = 'name_input'
        st.rerun()
