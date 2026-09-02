from dataclasses import dataclass
from typing import Callable


DOG_CAT_SHOP = "犬猫販売ペットショップ"
BUSINESS_LABELS = (DOG_CAT_SHOP, "トリミングサロン", "ブリーダー")
COMING_SOON_BUSINESSES = ("用品中心ペットショップ", "総合ペットショップ")

SAMPLE_DATA = {
    DOG_CAT_SHOP: {"sales": 12, "visits": 40, "conversion": 30.0, "price": 250000, "days": 55, "inventory": 15, "long_stay": 3, "inquiries": 50},
    "トリミングサロン": {"revenue": 900000, "treatments": 150, "ticket": 6000, "return_rate": 52.0, "occupancy": 88.0, "new_customers": 30, "next_booking": 35.0},
    "ブリーダー": {"inquiries": 40, "visits": 12, "contracts": 3, "inquiry_visit": 30.0, "visit_contract": 25.0, "sales_days": 90, "digital_share": 70.0},
}


@dataclass(frozen=True)
class Issue:
    title: str
    detail: str
    severity: int


@dataclass(frozen=True)
class DiagnosisResult:
    score: int
    priority_message: str
    ai_insight: str
    top_issues: list[Issue]
    ai_uses: list[str]
    human_domains: list[str]


def _issue(title: str, detail: str, severity: int) -> Issue:
    return Issue(title, detail, max(0, min(30, severity)))


def calculate_long_stay_ratio(long_stay: int, inventory: int) -> float:
    """Return the share of current CA staying 90+ days; zero is safe."""
    if inventory <= 0:
        return 0.0
    return long_stay / inventory * 100


def _shop(d: dict) -> list[Issue]:
    issues = []
    conversion, visits, inquiries = d["conversion"], d["visits"], d["inquiries"]
    long_stay_ratio = calculate_long_stay_ratio(d["long_stay"], d["inventory"])
    if d["long_stay"] > 0 and d["inventory"] > 0:
        issues.append(_issue(
            "長期在店",
            f"月間接客数{visits}件・成約率{conversion:g}%に対して、在店CA{d['inventory']}頭のうち90日超在店が{d['long_stay']}頭（{long_stay_ratio:.0f}%）です。新規集客だけでなく長期在店比率の推移を確認し、CAの健康状態・福祉を最優先に、個別CAごとの訴求内容・価格・店舗適性・接客状況を確認する価値があります。",
            round(12 + min(long_stay_ratio, 40) * 0.45),
        ))
    elif d["long_stay"] > 0:
        issues.append(_issue("入力値の整合性", f"現在の在店CA総数が0頭で、90日超在店CAが{d['long_stay']}頭と入力されています。比率を評価する前に、入力値を確認する価値があります。", 8))
    if d["days"] >= 50:
        context = "90日超在店CAもいるため、" if d["long_stay"] else "長期化の兆候を早めに捉えるため、"
        issues.append(_issue(
            "販売日数",
            f"平均販売日数は{d['days']}日です。{context}在店日数別の推移と検討中のお客様へのフォローを週次で確認する優先度が高いと考えられます。",
            round(8 + max(0, d["days"] - 50) / 4),
        ))
    if conversion < 35 and visits >= 25:
        title = "成約プロセス" if conversion >= 25 else "成約率"
        issues.append(_issue(
            title,
            f"月間接客数{visits}件に対して成約率は{conversion:g}%です。新規集客だけでなく、接客内容・提案方法・検討後フォローの改善余地を確認してください。",
            round(10 + (35 - conversion) * 0.65),
        ))
    elif conversion < 25:
        issues.append(_issue("成約率", f"成約率は{conversion:g}%です。接客数{visits}件の母数も踏まえ、接客ごとの検討理由と見送り理由をまず確認する価値があります。", round(10 + (25 - conversion) * 0.8)))
    if inquiries >= 30 and visits < inquiries * 0.6:
        rate = visits / max(inquiries, 1) * 100
        issues.append(_issue(
            "問い合わせから来店までの導線",
            f"問い合わせは{inquiries}件ある一方、来店／接客は{visits}件で、単純比較では約{rate:.0f}%です。返信速度・来店提案・日程調整の流れを確認する価値があります。",
            round(12 + min(12, (60 - rate) * 0.3)),
        ))
    if inquiries < 20:
        issues.append(_issue("問い合わせ獲得", f"問い合わせは月{inquiries}件です。成約プロセスとのバランスを見ながら、WEB・SNS・紹介からの流入経路を確認する価値があります。", round(18 - inquiries / 2)))
    return issues


def _salon(d: dict) -> list[Issue]:
    issues = []
    occupancy, ticket = d["occupancy"], d["ticket"]
    if occupancy >= 80:
        revenue_per_treatment = d["revenue"] / max(d["treatments"], 1)
        issues.append(_issue(
            "客単価・メニュー構成",
            f"予約稼働率は{occupancy:g}%で、単純に予約件数を増やす余地は限られている可能性があります。現在の平均客単価は{ticket:,}円、施術1件あたり売上は約{revenue_per_treatment:,.0f}円です。外部との高低比較ではなく、目標客単価との差・メニュー構成・施術時間あたり売上をまず確認する価値があります。",
            21,
        ))
    elif occupancy < 60:
        extra = f"月間新規顧客数は{d['new_customers']}人であり、" if d["new_customers"] < 10 else "新規来店後の再来状況も含め、"
        issues.append(_issue("予約稼働率", f"予約稼働率は{occupancy:g}%です。{extra}空き枠の告知・紹介・予約導線を確認する優先度が高いと考えられます。", round((60 - occupancy) * 0.6 + 8)))
    if d["return_rate"] < 60:
        comparison = f"月間新規顧客数は{d['new_customers']}人確保できている一方、" if d["new_customers"] >= 15 else "新規集客と並行して、"
        issues.append(_issue("再来率", f"{comparison}再来率は{d['return_rate']:g}%です。集客量だけでなく、施術後フォロー・来店周期に合った案内・満足度を確認する価値があります。", round((60 - d["return_rate"]) * 0.7 + 10)))
    if d["next_booking"] < 45:
        comparison = f"再来率{d['return_rate']:g}%に対して、" if d["return_rate"] >= 60 else "再来率との改善をつなげるため、"
        issues.append(_issue("次回予約率", f"{comparison}次回予約率は{d['next_booking']:g}%です。会計時の案内方法と、お客様ごとの適切な次回来店時期の伝え方を確認してください。", round((45 - d["next_booking"]) * 0.55 + 9)))
    if occupancy < 60 and d["new_customers"] < 10:
        issues.append(_issue("新規顧客獲得", f"予約稼働率{occupancy:g}%、月間新規顧客数は{d['new_customers']}人です。商圏での認知、口コミ、紹介、予約ページまでの導線を一続きで確認する価値があります。", 16))
    return issues


def _breeder(d: dict) -> list[Issue]:
    issues = []
    inquiries, visits = d["inquiries"], d["visits"]
    if d["inquiry_visit"] < 35:
        comparison = f"問い合わせは月{inquiries}件確保できている一方、" if inquiries >= 20 else "問い合わせ母数も踏まえつつ、"
        issues.append(_issue("問い合わせ対応", f"{comparison}問い合わせ→見学率は{d['inquiry_visit']:g}%です。集客だけを増やす前に、初回返信の速さ・安心材料・説明内容・見学までの日程調整を確認する価値があります。", round((40 - d["inquiry_visit"]) * 0.6 + 10)))
    if d["visit_contract"] < 40:
        comparison = f"見学は月{visits}件ある一方、" if visits >= 10 else "見学数の母数に注意しながら、"
        issues.append(_issue("見学からの成約", f"{comparison}見学→成約率は{d['visit_contract']:g}%です。見学時の説明、お客様の生活環境・希望の確認、信頼形成の流れをまず確認する価値があります。", round((40 - d["visit_contract"]) * 0.6 + 10)))
    if inquiries < 15 and visits < 6:
        issues.append(_issue("集客・SNS／WEB導線", f"問い合わせは月{inquiries}件、見学は月{visits}件です。飼育方針や日々の様子が伝わる発信から問い合わせまでの導線を確認する優先度が高いと考えられます。", 20))
    if d["sales_days"] > 75:
        comparison = f"見学→成約率{d['visit_contract']:g}%を踏まえ、" if d["visit_contract"] >= 40 else "成約プロセスとあわせて、"
        issues.append(_issue("販売までの期間", f"平均販売期間は{d['sales_days']}日です。{comparison}健康と福祉を最優先に、問い合わせ母数・露出先・検討者フォローを確認する価値があります。", round((d["sales_days"] - 75) / 4 + 10)))
    if d["digital_share"] < 40:
        issues.append(_issue("SNS・WEB導線", f"SNS／WEB由来の問い合わせ割合は{d['digital_share']:g}%です。問い合わせ数とのバランスを見ながら、飼育方針・日々の様子・見学案内が伝わる発信を確認してください。", round((40 - d["digital_share"]) * 0.35 + 8)))
    return issues


_RULES: dict[str, Callable[[dict], list[Issue]]] = {DOG_CAT_SHOP: _shop, "トリミングサロン": _salon, "ブリーダー": _breeder}

_FALLBACKS = {
    DOG_CAT_SHOP: [("KPIの継続確認", "成約率・販売日数・長期在店を週次で並べ、変化の起点を確認してください。"), ("接客品質", "好調な接客の共通点と、お客様が検討を止めた理由を確認する価値があります。"), ("情報発信", "CAごとの個性と暮らしのイメージが伝わる発信を継続してください。")],
    "トリミングサロン": [("KPIの継続確認", "再来率・稼働率・客単価を月次で並べ、どこから変化したか確認してください。"), ("顧客体験", "好調な施術後フォローを整理し、スタッフ間で共有する価値があります。"), ("予約導線", "次回予約の案内方法と予約しやすさを継続確認してください。")],
    "ブリーダー": [("KPIの継続確認", "問い合わせ・見学・成約を一続きで確認し、離脱が増えた段階を見つけてください。"), ("見学体験", "安心につながる説明とニーズ確認を整理する価値があります。"), ("情報発信", "飼育方針と日々の様子が伝わる発信を継続してください。")],
}

_AI_USES = {
    DOG_CAT_SHOP: ["KPI週次分析", "問い合わせ返信案の作成", "接客・スタッフ教育支援"],
    "トリミングサロン": ["再来・予約KPI分析", "来店後メッセージ案の作成", "メニュー別売上の分析"],
    "ブリーダー": ["問い合わせ傾向の分析", "返信・見学案内文の作成", "SNS／WEB発信の下書き"],
}


def _priority_message(business: str, d: dict, first: Issue) -> str:
    if business == DOG_CAT_SHOP:
        if first.title == "長期在店" and d["conversion"] >= 25:
            ratio = calculate_long_stay_ratio(d["long_stay"], d["inventory"])
            return f"月間接客数{d['visits']}件・成約率{d['conversion']:g}%に対して、在店CA{d['inventory']}頭のうち90日超在店が{d['long_stay']}頭（{ratio:.0f}%）です。入力された数値の範囲では、新規集客だけでなく「長期在店」の構造を優先して確認する価値があります。CAの健康状態・福祉を最優先に、個別の状況と比率の推移を確認してください。"
        return f"問い合わせ{d['inquiries']}件、接客{d['visits']}件、成約率{d['conversion']:g}%を比較すると、「{first.title}」を最初に確認する優先度が高いと考えられます。新規集客と既存の接客・販売導線のどちらに改善余地があるかを切り分ける価値があります。"
    if business == "トリミングサロン":
        if first.title == "客単価・メニュー構成":
            return f"予約稼働率は{d['occupancy']:g}%で、月間施術件数は{d['treatments']}件です。単純に予約件数を増やす余地は限られている可能性があるため、売上を伸ばす場合は、新規集客だけでなく「1枠あたり売上・メニュー構成・施術時間」を確認する価値があります。"
        return f"月間新規顧客数{d['new_customers']}人、再来率{d['return_rate']:g}%、予約稼働率{d['occupancy']:g}%を比較すると、「{first.title}」を最初に確認する優先度が高いと考えられます。"
    if first.title == "成約ファネル全体":
        return f"問い合わせ{d['inquiries']}件から見学{d['visits']}件、成約{d['contracts']}件へ進むファネルでは、問い合わせから見学、見学から成約の双方で離脱が発生しています。入力された数値の範囲では、片方の率だけで優先順位を断定せず、「成約ファネル全体」を確認する価値があります。"
    if first.title == "見学からの成約":
        return f"問い合わせ{d['inquiries']}件から見学{d['visits']}件、成約{d['contracts']}件へ進んでいます。最終成果に直接つながる見学後の工程について、説明・ニーズ確認・信頼形成を確認する価値があります。"
    return f"問い合わせ{d['inquiries']}件、見学{d['visits']}件、成約{d['contracts']}件を比較すると、「{first.title}」を最初に確認する優先度が高いと考えられます。"


def _ai_insight(business: str, d: dict) -> str:
    if business == DOG_CAT_SHOP:
        if d["long_stay"] and d["conversion"] >= 25:
            ratio = calculate_long_stay_ratio(d["long_stay"], d["inventory"])
            if d["inventory"] <= 0:
                return "現在の在店CA総数と90日超在店CA数の入力に整合しない可能性があります。経営上の仮説を出す前に、母数を確認する価値があります。"
            return f"月間接客数{d['visits']}件・成約率{d['conversion']:g}%に対して、在店CAに占める90日超在店の比率は{ratio:.0f}%です。入力された数値の範囲では、新規集客だけでなく、CAの健康と福祉を最優先として、販売日数と長期在店比率の推移を個別に見る価値があります。"
        if d["inquiries"] >= 30 and d["visits"] < d["inquiries"] * 0.6:
            return "問い合わせの母数はある一方、来店／接客までに差があります。広告を増やすより、返信から来店予約までの導線を先に確認する価値があります。"
        if d["visits"] >= 25 and d["conversion"] < 25:
            return "接客数は確保できています。入力された数値の範囲では、集客量より接客・提案・検討後フォローの転換プロセスを優先する仮説が考えられます。"
        return "成約率・販売日数・長期在店比率を週次で並べ、どの指標から変化が現れるかを確認する価値があります。"
    if business == "トリミングサロン":
        if d["occupancy"] >= 80:
            return f"予約稼働率は{d['occupancy']:g}%のため、単純に予約件数を増やす余地は限られている可能性があります。平均客単価{d['ticket']:,}円を外部基準で評価せず、目標客単価との差・1枠あたり売上・メニュー構成・施術時間を先に確認する優先度が高いと考えられます。"
        if d["new_customers"] >= 15 and d["return_rate"] < 60:
            return f"月間新規顧客数{d['new_customers']}人に対して再来率は{d['return_rate']:g}%です。集客を増やす施策と並べて、初回来店後のフォローと次回来店の提案を確認する仮説が考えられます。"
        if d["return_rate"] >= 60 and d["next_booking"] < 45:
            return f"再来率{d['return_rate']:g}%に対して次回予約率は{d['next_booking']:g}%です。会計時の予約提案や適切な来店時期の伝え方を確認する価値があります。"
        return "稼働率・月間新規顧客数・再来率を一続きで見ると、空き枠を埋める施策と既存顧客の継続施策のどちらを先に試すか判断しやすくなります。"
    if d["inquiry_visit"] < 35 and d["visit_contract"] < 40:
        return f"問い合わせ{d['inquiries']}件から見学{d['visits']}件、成約{d['contracts']}件へ進んでいます。問い合わせから見学、見学から成約の双方で離脱が発生しているため、異なる段階の率を単純比較せず、初回対応・見学導線と、成約に直接近い見学時の説明・ニーズ確認・信頼形成を一続きで確認する価値があります。"
    if d["inquiries"] >= 20 and d["inquiry_visit"] < 35:
        return "問い合わせ数は確保できている一方で見学率に改善余地がある可能性があります。集客よりも問い合わせ後の初動・説明内容・見学導線を先に確認する価値があります。"
    if d["visits"] >= 10 and d["visit_contract"] < 40:
        return "見学数は一定数ある一方で成約への転換に差があります。露出を増やす前に、見学時の説明・お客様のニーズ確認・信頼形成を確認する優先度が高いと考えられます。"
    if d["visit_contract"] >= 40 and d["sales_days"] > 75:
        return f"見学→成約率{d['visit_contract']:g}%に対して、平均販売期間は{d['sales_days']}日です。問い合わせ母数・露出先・見学前の導線に改善余地がある可能性があります。"
    return "問い合わせ・見学・成約を一続きで比較し、最も差が大きい段階から確認することで、集客と説明改善の優先順位を整理できます。"


def diagnose(business: str, data: dict) -> DiagnosisResult:
    if business not in _RULES:
        raise ValueError("未対応の業態です")
    issues = sorted(_RULES[business](data), key=lambda x: x.severity, reverse=True)
    if business == "ブリーダー" and data["inquiry_visit"] < 35 and data["visit_contract"] < 40:
        first = issues[0]
        funnel_detail = (
            f"問い合わせ{data['inquiries']}件から見学{data['visits']}件、成約{data['contracts']}件へ進んでいます。"
            "ファネルの双方で離脱が発生しているため、片方の率だけで判断せず、問い合わせ後の初動・見学導線と、成約に直接近い見学時の説明・ニーズ確認・信頼形成を一続きで確認する価値があります。"
        )
        issues[0] = _issue("成約ファネル全体", funnel_detail, first.severity)
    existing = {x.title for x in issues}
    for title, detail in _FALLBACKS[business]:
        if len(issues) >= 3:
            break
        if title not in existing:
            issues.append(_issue(title, detail, 4))
            existing.add(title)
    top = issues[:3]
    score = max(0, min(100, 100 - sum(x.severity for x in top)))
    human = ["CAの健康状態と福祉", "命に関する判断", "お客様への重要な説明", "最終的な経営判断"]
    if business == "トリミングサロン":
        human[0] = "ペットの健康状態と施術可否"
    return DiagnosisResult(score, _priority_message(business, data, top[0]), _ai_insight(business, data), top, _AI_USES[business], human)
