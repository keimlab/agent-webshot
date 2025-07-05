# Agent WebShot - Screenshot Tool for AI Agents

AIエージェント（Claude Code、GitHub Copilot等）向けの高機能Webスクリーンショットツールです。Chrome DevTools Protocolを使用してWebページの全体をキャプチャできます。Agent Tools Seriesの第一弾として開発されました。

## 🌟 特徴

- **フルページキャプチャ**: Chrome DevTools Protocolを使用し、スクロールが必要な長いページも完全にキャプチャ
- **AIエージェント最適化**: 詳細なJSON形式のレスポンスで、エージェントが結果を解析しやすい設計
- **自動ファイル管理**: 日付別フォルダと年月日時分秒を含むファイル名で整理
- **柔軟な設定**: ウィンドウサイズ、待機時間、ヘッドレスモードなど多数のオプション
- **エラーハンドリング**: 詳細なエラー情報とフォールバック機能

## 📋 必要要件

- Python 3.7以上
- Google Chrome または Chromium
- ChromeDriver（Selenium 4.6.0以降は自動管理、それ以前はwebdriver-manager使用）

## 🚀 インストール

### 1. リポジトリのクローンまたはファイルのダウンロード

```bash
git clone <repository-url>
cd <project-directory>
```

### 2. 仮想環境の作成（推奨）

```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# または
venv\Scripts\activate  # Windows
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

`requirements.txt`の内容:
```
selenium==4.15.2
webdriver-manager==4.0.2  # オプション（Selenium 4.6.0以降は不要）
```

**注意**: Selenium 4.15.2にはSelenium Manager 0.4.15が含まれており、ChromeDriverの自動管理が可能です。webdriver-managerはバックアップとして含めていますが、必須ではありません。

## 💻 使用方法

### コマンドライン実行

基本的な使用:
```bash
python agent_webshot.py --url https://example.com
```

オプション付き:
```bash
# フルページキャプチャを無効化
python agent_webshot.py --url https://example.com --no-full-page

# カスタムプレフィックスと待機時間
python agent_webshot.py --url https://example.com --prefix "test" --wait 5

# JSON形式で結果を出力
python agent_webshot.py --url https://example.com --json

# デバッグ用（ブラウザを表示）
python agent_webshot.py --url https://example.com --no-headless
```

### Pythonコードから使用

```python
from agent_webshot import screenshot

# 基本的な使用
result = screenshot("https://example.com")

# カスタム設定
result = screenshot(
    url="https://example.com",
    output_folder="./captures",
    file_prefix="mysite",
    full_page=True,
    wait_time=5,
    window_size="1920,1080"
)

# 結果の確認
if result["success"]:
    print(f"保存先: {result['file']['relative_path']}")
    print(f"ファイルサイズ: {result['file']['size_mb']} MB")
    print(f"ページタイトル: {result['page']['title']}")
    print(f"キャプチャサイズ: {result['capture']['width']}x{result['capture']['height']}")
else:
    print(f"エラー: {result['error']}")
```

### サンプルページでのテスト

プロジェクトに含まれるサンプルページでツールをテストできます：

```bash
# サンプルページのスクリーンショットを撮影
python agent_webshot.py --url "file://$(pwd)/examples/sample-page.html" --prefix "demo"

# 結果をJSON形式で確認
python agent_webshot.py --url "file://$(pwd)/examples/sample-page.html" --json
```

`examples/sample-page.html`は「Modern Web Development Stack」学習ロードマップのページで、フルページキャプチャのテストに最適です。

## 📁 ファイル構成

スクリーンショットは以下の形式で保存されます:

```
screenshots/
├── 2025-07-05/
│   ├── screenshot_yahoo_20250705_093956.png
│   ├── screenshot_google_20250705_094523.png
│   └── test_example_20250705_095012.png
└── 2025-07-06/
    └── ...
```

ファイル名の形式: `{prefix}_{domain}_{YYYYMMDD_HHMMSS}.png`

## 🔧 ChromeDriver管理について

このツールは2つの方法でChromeDriverを管理します：

### Selenium Manager（推奨）
- **対象**: Selenium 4.6.0以降（このプロジェクトでは4.15.2を使用）
- **機能**: ChromeDriverを自動的にダウンロード・管理
- **キャッシュ場所**: `~/.cache/selenium/`
- **メリット**: 公式機能で依存関係が少ない

### webdriver-manager（バックアップ）
- **対象**: Selenium Manager動作しない場合のフォールバック
- **機能**: サードパーティライブラリによるドライバー管理
- **キャッシュ場所**: `~/.wdm/`
- **用途**: 互換性確保のため残置

## 🔧 コマンドラインオプション

| オプション | 説明 | デフォルト |
|------------|------|------------|
| `--url` | キャプチャするURL（必須） | - |
| `--output-folder` | 保存先フォルダ | `./screenshots` |
| `--prefix` | ファイル名のプレフィックス | `screenshot` |
| `--window-size` | ウィンドウサイズ（幅,高さ） | `1920,1080` |
| `--no-full-page` | フルページキャプチャを無効化 | False |
| `--wait` | ページ読み込み後の待機時間（秒） | 3 |
| `--timeout` | ページ読み込みのタイムアウト（秒） | 30 |
| `--no-headless` | ブラウザを表示（デバッグ用） | False |
| `--json` | 結果をJSON形式で出力 | False |

## 📊 レスポンス形式

成功時のレスポンス例:

```json
{
  "success": true,
  "message": "✅ スクリーンショットの保存に成功しました",
  "file": {
    "path": "screenshots/2025-07-05/screenshot_yahoo_20250705_093956.png",
    "relative_path": "./screenshots/2025-07-05/screenshot_yahoo_20250705_093956.png",
    "size_bytes": 2708496,
    "size_mb": 2.58
  },
  "page": {
    "url": "https://www.yahoo.co.jp",
    "final_url": "https://www.yahoo.co.jp/",
    "title": "Yahoo! JAPAN",
    "redirected": true
  },
  "capture": {
    "full_page": true,
    "method": "CDP",
    "width": 1905,
    "height": 6487
  },
  "metadata": {
    "timestamp": "2025-07-05T09:40:05.563860",
    "duration_seconds": 9.19,
    "window_size": "1920,1080",
    "headless": true
  }
}
```

## 🔍 トラブルシューティング

### ChromeDriverエラー

エラー: `WebDriverの初期化に失敗しました`

解決方法:
1. Google Chromeが最新版であることを確認
2. Selenium Managerのキャッシュをクリア: `rm -rf ~/.cache/selenium/`
3. webdriver-managerのキャッシュもクリア: `rm -rf ~/.wdm/`
4. 必要に応じて: `pip install --upgrade selenium webdriver-manager`

### タイムアウトエラー

エラー: `ページの読み込みが30秒を超えました`

解決方法:
- `--timeout`オプションで時間を延長
- `--wait`オプションで追加の待機時間を調整

### M1/M2 Macでの実行エラー

エラー: `[Errno 8] Exec format error`

解決方法:
1. Selenium Managerのキャッシュをクリア: `rm -rf ~/.cache/selenium/`
2. webdriver-managerのキャッシュをクリア: `rm -rf ~/.wdm/`
3. Rosetta 2がインストールされていることを確認
4. Chrome for Macがネイティブ版（Apple Silicon対応）であることを確認

**備考**: Selenium Manager 0.4.15はApple Siliconに対応しており、自動的に適切なChromeDriverをダウンロードします。

## 📝 ライセンス

このプロジェクトはMITライセンスのもとで公開されています。

## 🔄 更新履歴

- 2025-07-05: 初版リリース
  - Chrome DevTools Protocolによるフルページキャプチャ実装
  - AIエージェント向け最適化
  - 日付・時刻ベースのファイル管理機能
  - Selenium Manager 0.4.15対応（自動ChromeDriver管理）

## 🔧 Agent Tools Series

このツールは「Agent Tools Series」の第一弾です。AIエージェントの作業効率を向上させる様々なツールを開発予定です。

### 現在リリース済み
- **agent_webshot** - Webページスクリーンショット取得ツール

### 設計方針
- **統一インターフェース**: 全ツール共通のJSONレスポンス形式
- **エージェント最適化**: 詳細なエラーハンドリングと状況報告
- **独立性**: 各ツールは単独で動作可能
- **拡張性**: 他のagent_ツールとの連携を考慮した設計

## 👥 作者

AIエージェント（Claude Code）との協働により開発