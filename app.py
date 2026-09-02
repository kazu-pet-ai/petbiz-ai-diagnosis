import time

import streamlit as st

from config import APP_NAME, CTA_URL
from modules.diagnosis import (
    BUSINESS_LABELS,
    COMING_SOON_BUSINESSES,
    DOG_CAT_SHOP,
    SAMPLE_DATA,
    diagnose,
)


st.set_page_config(page_title=APP_NAME, page_icon="🐾", layout="centered")

st.markdown(
    """
    <style>
    :root { --blue:#2563eb; --navy:#0f172a; --muted:#64748b; }
    .stApp { background: linear-gradient(145deg,#f8fafc 0%,#fff 45%,#eff6ff 100%); color:var(--navy); }
    .block-container { max-width: 820px; padding-top: 2.2rem; padding-bottom: 3rem; }
    .eyebrow { color:var(--blue); font-size:.78rem; font-weight:800; letter-spacing:.12em; }
    .hero { padding:1.9rem; border:1px solid #dbeafe; border-radius:24px; background:rgba(255,255,255,.92); box-shadow:0 18px 50px rgba(15,23,42,.08); margin-bottom:1.3rem; }
    .hero h1 { font-size:clamp(2rem,7vw,3.3rem); line-height:1.06; margin:.45rem 0 .8rem; letter-spacing:-.04em; }
    .hero p { color:var(--muted); font-size:1.04rem; margin:0; }
    .step { display:inline-block; color:var(--blue); background:#eff6ff; border-radius:999px; padding:.3rem .7rem; font-size:.78rem; font-weight:800; margin-top:.6rem; }
    div[data-testid="stForm"] { background:#fff; border:1px solid #e2e8f0; padding:1.1rem; border-radius:20px; box-shadow:0 8px 30px rgba(15,23,42,.05); }
    div.stButton > button, div[data-testid="stFormSubmitButton"] button { border-radius:12px; min-height:3rem; font-weight:800; }
    .score { text-align:center; padding:1.5rem; border-radius:22px; color:white; background:linear-gradient(135deg,#0f172a,#1e3a8a); margin:1rem 0; }
    .score strong { display:block; font-size:3.4rem; line-height:1; margin:.35rem; }
    .priority { padding:1.15rem 1.25rem; border-left:5px solid var(--blue); background:#eff6ff; border-radius:0 14px 14px 0; font-size:1.06rem; }
    .insight { padding:1.15rem 1.25rem; border:1px solid #bfdbfe; background:linear-gradient(135deg,#eff6ff,#f8fafc); border-radius:16px; }
    .card { padding:1rem 1.2rem; background:#fff; border:1px solid #e2e8f0; border-radius:16px; height:100%; }
    .cta { margin-top:1.4rem; padding:1.6rem; background:#0f172a; color:white; border-radius:22px; }
    .cta h3 { margin-top:0; font-size:1.4rem; }
    .cta p { color:#cbd5e1; }
    div[data-testid="stLinkButton"] a { background:#3b82f6 !important; border-color:#60a5fa !important; color:white !important; }
    div[data-testid="stLinkButton"] a:hover { background:#2563eb !important; border-color:#3b82f6 !important; }
    .disclaimer { color:#64748b; font-size:.78rem; text-align:center; margin-top:2.2rem; }
    @media(max-width:640px){.block-container{padding:1rem}.hero{padding:1.25rem}.hero h1{font-size:2.25rem}}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """<section class="hero"><div class="eyebrow">PET BUSINESS × AI</div>
    <h1>60秒で、次に見るべき<br>経営課題がわかる。</h1>
    <p>いくつかの数字から、改善の優先順位とAI活用のヒントを無料で整理します。</p></section>""",
    unsafe_allow_html=True,
)

st.markdown('<span class="step">STEP 1 / 3</span>', unsafe_allow_html=True)
business = st.radio("業態を選択してください", list(BUSINESS_LABELS), horizontal=True)
st.caption("近日対応：" + " ／ ".join(COMING_SOON_BUSINESSES))
st.markdown('<span class="step">STEP 2 / 3</span>', unsafe_allow_html=True)
st.subheader(f"{business}の数値を入力")


def widget_key(field: str) -> str:
    return f"input:{business}:{field}"


def pct(label: str, field: str, help_text: str | None = None) -> float:
    return st.number_input(
        label,
        min_value=0.0,
        max_value=100.0,
        step=1.0,
        help=help_text or "0〜100%で入力",
        key=widget_key(field),
    )


for field, value in SAMPLE_DATA[business].items():
    st.session_state.setdefault(widget_key(field), value)

if st.button("サンプルデータで試す", use_container_width=True):
    for field, value in SAMPLE_DATA[business].items():
        st.session_state[widget_key(field)] = value
    st.rerun()


with st.form("diagnosis_form"):
    data = {}
    c1, c2 = st.columns(2)
    if business == DOG_CAT_SHOP:
        with c1:
            data["sales"] = st.number_input("月間CA販売数", 0, help="CA＝コンパニオンアニマル", key=widget_key("sales"))
            data["visits"] = st.number_input("月間来店／接客数", 0, key=widget_key("visits"))
            data["conversion"] = pct("成約率（%）", "conversion", "月間CA販売数 ÷ 月間来店／接客数 × 100")
            data["price"] = st.number_input("平均販売単価（円）", 0, step=10000, key=widget_key("price"))
        with c2:
            data["days"] = st.number_input("平均販売日数（日）", 0, key=widget_key("days"))
            data["inventory"] = st.number_input("現在の在店CA総数", 0, help="診断時点で在店しているCAの総数", key=widget_key("inventory"))
            data["long_stay"] = st.number_input("90日以上在店しているCA数", 0, key=widget_key("long_stay"))
            data["inquiries"] = st.number_input("月間問い合わせ数", 0, key=widget_key("inquiries"))
    elif business == "トリミングサロン":
        with c1:
            data["revenue"] = st.number_input("月間売上（円）", 0, step=50000, key=widget_key("revenue"))
            data["treatments"] = st.number_input("月間施術件数", 0, key=widget_key("treatments"))
            data["ticket"] = st.number_input("平均客単価（円）", 0, step=500, key=widget_key("ticket"))
            data["return_rate"] = pct("再来率（%）", "return_rate")
        with c2:
            data["occupancy"] = pct("予約稼働率（%）", "occupancy")
            data["new_customers"] = st.number_input("月間新規顧客数", 0, key=widget_key("new_customers"))
            data["next_booking"] = pct("次回予約率（%）", "next_booking")
    else:
        with c1:
            data["inquiries"] = st.number_input("月間問い合わせ数", 0, key=widget_key("inquiries"))
            data["visits"] = st.number_input("月間見学数", 0, key=widget_key("visits"))
            data["contracts"] = st.number_input("月間成約数", 0, key=widget_key("contracts"))
            data["inquiry_visit"] = pct("問い合わせ→見学率（%）", "inquiry_visit", "月間見学数 ÷ 月間問い合わせ数 × 100")
        with c2:
            data["visit_contract"] = pct("見学→成約率（%）", "visit_contract", "月間成約数 ÷ 月間見学数 × 100")
            data["sales_days"] = st.number_input("平均販売期間（日）", 0, key=widget_key("sales_days"))
            data["digital_share"] = pct("SNS／WEBからの問い合わせ割合（%）", "digital_share")
    submitted = st.form_submit_button("AI診断を開始", use_container_width=True, type="primary")

if submitted:
    status = st.status("診断を開始しています…", expanded=True)
    for message in ["入力データを確認しています…", "重要KPIを比較しています…", "改善優先順位を算出しています…"]:
        status.write(message)
        time.sleep(0.28)
    status.update(label="診断が完了しました", state="complete", expanded=False)
    result = diagnose(business, data)
    st.markdown('<span class="step">STEP 3 / 3</span>', unsafe_allow_html=True)
    st.subheader("診断結果")
    st.markdown(f'<div class="score">経営スコア<strong>{result.score}</strong><span>／100点</span></div>', unsafe_allow_html=True)
    st.caption("入力された指標をもとにした簡易診断です。絶対的な経営評価ではありません。")
    st.markdown("#### 最優先課題")
    st.markdown(f'<div class="priority">{result.priority_message}</div>', unsafe_allow_html=True)
    st.markdown("#### AIの着眼点")
    st.markdown(f'<div class="insight">✦ {result.ai_insight}</div>', unsafe_allow_html=True)
    st.markdown("#### 改善優先順位 TOP 3")
    for i, issue in enumerate(result.top_issues, 1):
        st.markdown(f"**{i}. {issue.title}**  \n{issue.detail}")
    left, right = st.columns(2)
    with left:
        st.markdown("#### AI活用候補")
        st.markdown('<div class="card">' + "<br>".join(f"✓ {x}" for x in result.ai_uses) + "</div>", unsafe_allow_html=True)
    with right:
        st.markdown("#### 人が判断すべき領域")
        st.markdown('<div class="card">' + "<br>".join(f"• {x}" for x in result.human_domains) + "</div>", unsafe_allow_html=True)
    st.info("AIは判断者ではなく、意思決定を支援する道具です。")
    st.markdown(
        """<div class="cta"><h3>この数字の“原因”まで、30分で一緒に整理しませんか？</h3>
        <p>この診断は、数値から課題の可能性を整理した簡易診断です。本当に重要なのは、『なぜその数字になったのか』を現場から見つけること。30分無料相談では、AIを使うべきところ・人が担うべきところを一緒に整理します。</p></div>""",
        unsafe_allow_html=True,
    )
    st.link_button("30分無料相談を申し込む →", CTA_URL, use_container_width=True, type="primary")

st.markdown('<div class="disclaimer">本診断は簡易的なデモであり、経営成果を保証するものではありません。<br>入力された情報のみをもとに課題仮説を提示します。入力情報は保存しません。</div>', unsafe_allow_html=True)
