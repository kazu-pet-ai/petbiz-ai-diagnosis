# PetBiz AI 60秒経営診断

犬猫販売ペットショップ・トリミングサロン・ブリーダーの経営者／責任者向けに、業態ごとの数値から経営課題の仮説、改善優先順位、AI活用候補を約60秒で提示する無料デモです。複数KPIを比較した「AIの着眼点」も提示します。犬猫販売ペットショップでは、現在の在店CA総数を母数として90日超在店比率を内部計算します。入力情報は保存しません。初期MVPは外部API・DBなしのルールベース診断です。

現在診断できる業態は「犬猫販売ペットショップ」「トリミングサロン」「ブリーダー」です。「用品中心ペットショップ」「総合ペットショップ」は将来対応候補としてUIに表示しています。業態名、サンプル値、診断関数は `modules/diagnosis.py` に集約しているため、新しい業態を追加しやすい構成です。

## インストールと起動

Python 3.10以上を推奨します。

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

ブラウザで通常 `http://localhost:8501` が開きます。

## Streamlit Community Cloudへデプロイ

1. このフォルダをGitHubリポジトリへpushします（`.env` と `.streamlit/secrets.toml` はコミットしないでください）。
2. [Streamlit Community Cloud](https://share.streamlit.io/) でGitHub連携し、対象リポジトリを選びます。
3. Main file pathに `app.py` を指定してDeployします。
## CTA URLの変更

CTAは公開情報であるGoogleフォームURLへ固定しており、Secretsや環境変数は使用しません。変更する場合は `config.py` の `CTA_URL` を編集します。

## 将来的なGemini API接続

現在の診断入口は `modules/diagnosis.py` の `diagnose()` に集約しています。将来は同じ `DiagnosisResult` を返すGemini用アダプター（例: `modules/gemini_diagnosis.py`）を追加し、設定値で呼び分けるとUIを変更せず移行できます。

1. Gemini SDKを `requirements.txt` に追加します。
2. `GEMINI_API_KEY` をローカル環境変数またはStreamlit Secretsへ登録します。
3. 入力値のみを構造化してAPIへ渡し、レスポンスを検証して `DiagnosisResult` に変換します。
4. API失敗時は現在のルールベースへフォールバックします。

APIキーをソースコードやGitHubへ直接記載しないでください。`.env.example` と `.streamlit/secrets.toml.example` はキー名の見本のみです。

## フォルダ構成

```text
.
├── app.py                         # Streamlit UI
├── config.py                      # CTA等の設定
├── modules/
│   ├── __init__.py
│   └── diagnosis.py               # 業態定義、サンプル値、比較型ルール、共通結果モデル
├── tests/
│   ├── test_app.py                # 画面、サンプル入力、結果表示のテスト
│   └── test_diagnosis.py          # 3業態、極端値、設定のテスト
├── .streamlit/
│   └── secrets.toml.example       # Secrets設定例
├── .env.example                   # 環境変数例
├── requirements.txt
└── README.md
```

## テスト

```bash
python -m unittest discover -s tests -v
python -m compileall app.py config.py modules tests
```

診断は入力指標に基づく簡易的な課題仮説であり、経営成果を保証するものではありません。
