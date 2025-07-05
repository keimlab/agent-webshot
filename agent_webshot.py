#!/usr/bin/env python3
"""
Screenshot Tool for AI Agents
AIエージェント向けの高機能スクリーンショットツール

Features:
- フルページキャプチャ（Chrome DevTools Protocol使用）
- 自動的な日付・時刻ベースのファイル管理
- エラーハンドリングと詳細なレスポンス
- Claude Code, GitHub Copilot等のエージェントに最適化
"""
import os
import argparse
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


class ScreenshotTool:
    """AIエージェント向けスクリーンショット取得ツール"""

    def __init__(self, timeout: int = 30):
        """
        Args:
            timeout: ページ読み込みのタイムアウト時間（秒）
        """
        self.driver = None
        self.timeout = timeout

    def _generate_filename(self, url: str, prefix: str = "screenshot") -> Tuple[str, str]:
        """
        タイムスタンプ付きのファイル名を生成する。
        
        Args:
            url: キャプチャ対象のURL
            prefix: ファイル名のプレフィックス
            
        Returns:
            (filename, timestamp): ファイル名とタイムスタンプのタプル
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # URLからドメイン名を抽出してファイル名に含める
        domain = ""
        if url.startswith(("http://", "https://")):
            # ホスト名全体を取得
            hostname = url.split("/")[2]
            
            # www.を除去
            if hostname.startswith("www."):
                hostname = hostname[4:]
            
            # 主要なドメイン名を抽出
            domain_parts = hostname.split(".")
            
            # 一般的なTLDとccTLDのパターンを処理
            if len(domain_parts) >= 2:
                # .co.jp, .com.cn などの複合TLDを持つ場合
                if len(domain_parts) >= 3 and domain_parts[-2] in ["co", "com", "net", "org", "ac", "edu", "gov"]:
                    domain = f"_{domain_parts[-3]}"
                else:
                    # 通常の.com, .jp などの場合
                    domain = f"_{domain_parts[0]}"
        
        filename = f"{prefix}{domain}_{timestamp}.png"
        return filename, timestamp

    def prepare_output_path(self, base_folder: str, url: str, prefix: str = "screenshot") -> Tuple[str, str]:
        """
        出力パスを準備し、必要なディレクトリを作成する。
        
        Returns:
            (full_path, relative_path): 完全パスと相対パスのタプル
        """
        # 今日の日付でフォルダを作成
        today = datetime.now().strftime("%Y-%m-%d")
        save_dir = Path(base_folder) / today
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイル名生成
        filename, _ = self._generate_filename(url, prefix)
        
        full_path = save_dir / filename
        relative_path = f"{base_folder}/{today}/{filename}"
        
        return str(full_path), relative_path

    def configure_driver(self, window_size: str = "1920,1080", headless: bool = True) -> webdriver.Chrome:
        """
        Chrome WebDriverを構成して返す。
        
        Args:
            window_size: ウィンドウサイズ（幅,高さ）
            headless: ヘッドレスモードで実行するか
        """
        options = Options()
        
        if headless:
            options.add_argument("--headless=new")  # 新しいヘッドレスモード
        
        # パフォーマンスと安定性のための設定
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument(f"--window-size={window_size}")
        options.add_argument("--force-device-scale-factor=1")
        
        # 画像やフォントの読み込みを最適化
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # User-Agentを設定（より自然なブラウジング）
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        # ChromeDriverの自動管理
        try:
            if WEBDRIVER_MANAGER_AVAILABLE:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
            else:
                driver = webdriver.Chrome(options=options)
            
            # ページ読み込みタイムアウトを設定
            driver.set_page_load_timeout(self.timeout)
            
            return driver
            
        except Exception as e:
            raise WebDriverException(f"WebDriverの初期化に失敗しました: {str(e)}")

    def wait_for_page_load(self, driver: webdriver.Chrome, wait_time: int = 3) -> bool:
        """
        ページの読み込み完了を待機する。
        
        Returns:
            読み込みが成功したかどうか
        """
        try:
            # JavaScriptの実行完了を待つ
            WebDriverWait(driver, self.timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # 追加の待機時間（動的コンテンツの読み込み用）
            import time
            time.sleep(wait_time)
            
            return True
            
        except TimeoutException:
            return False

    def capture_fullpage_screenshot(self, driver: webdriver.Chrome, save_path: str) -> Dict[str, Any]:
        """
        Chrome DevTools Protocolを使用してフルページスクリーンショットを撮影する。
        """
        try:
            # ページメトリクスを取得
            metrics = driver.execute_cdp_cmd('Page.getLayoutMetrics', {})
            width = metrics['contentSize']['width']
            height = metrics['contentSize']['height']
            
            # デバイスメトリクスをエミュレート
            driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                'width': int(width),
                'height': int(height),
                'deviceScaleFactor': 1,
                'mobile': False
            })
            
            # スクリーンショットを撮影
            screenshot = driver.execute_cdp_cmd('Page.captureScreenshot', {
                'format': 'png',
                'captureBeyondViewport': True,
                'clip': {
                    'x': 0,
                    'y': 0,
                    'width': width,
                    'height': height,
                    'scale': 1
                }
            })
            
            # デバイスメトリクスをリセット
            driver.execute_cdp_cmd('Emulation.clearDeviceMetricsOverride', {})
            
            # base64デコードして保存
            screenshot_data = base64.b64decode(screenshot['data'])
            
            with open(save_path, 'wb') as f:
                f.write(screenshot_data)
            
            return {
                'success': True,
                'width': int(width),
                'height': int(height),
                'method': 'CDP'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'CDP'
            }

    def capture_screenshot(
        self,
        url: str,
        output_folder: str = "./screenshots",
        file_prefix: str = "screenshot",
        window_size: str = "1920,1080",
        full_page: bool = True,
        wait_time: int = 3,
        headless: bool = True
    ) -> Dict[str, Any]:
        """
        指定されたURLのスクリーンショットを取得する。
        
        Args:
            url: キャプチャするURL
            output_folder: 保存先フォルダ
            file_prefix: ファイル名のプレフィックス
            window_size: ウィンドウサイズ
            full_page: フルページキャプチャを行うか
            wait_time: ページ読み込み後の追加待機時間
            headless: ヘッドレスモードで実行するか
            
        Returns:
            実行結果の詳細な辞書
        """
        start_time = datetime.now()
        
        try:
            # URLの検証・補正
            if not url:
                raise ValueError("URLが指定されていません")
            
            if not (url.startswith("http://") or url.startswith("https://") or url.startswith("file://")):
                url = "https://" + url
            
            # 保存パスを準備
            save_path, relative_path = self.prepare_output_path(output_folder, url, file_prefix)
            
            print(f"🚀 スクリーンショット取得を開始: {url}")
            
            # WebDriverを設定
            self.driver = self.configure_driver(window_size, headless)
            
            # ページを開く
            print(f"📄 ページを読み込み中...")
            self.driver.get(url)
            
            # ページ読み込み完了を待つ
            if not self.wait_for_page_load(self.driver, wait_time):
                print(f"⚠️  ページの読み込みがタイムアウトしました")
            
            # 現在のページ情報を取得
            page_title = self.driver.title
            current_url = self.driver.current_url
            
            # スクリーンショットを撮影
            print(f"📸 スクリーンショットを撮影中...")
            
            if full_page:
                capture_result = self.capture_fullpage_screenshot(self.driver, save_path)
                if not capture_result['success']:
                    # フォールバック: 通常のスクリーンショット
                    self.driver.save_screenshot(save_path)
                    capture_result = {'success': True, 'method': 'standard'}
            else:
                self.driver.save_screenshot(save_path)
                capture_result = {'success': True, 'method': 'standard'}
            
            # ファイル情報を取得
            file_size = os.path.getsize(save_path)
            file_size_mb = file_size / (1024 * 1024)
            
            # 処理時間を計算
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 成功レスポンス
            result = {
                "success": True,
                "message": "✅ スクリーンショットの保存に成功しました",
                "file": {
                    "path": save_path,
                    "relative_path": relative_path,
                    "size_bytes": file_size,
                    "size_mb": round(file_size_mb, 2)
                },
                "page": {
                    "url": url,
                    "final_url": current_url,
                    "title": page_title,
                    "redirected": url != current_url
                },
                "capture": {
                    "full_page": full_page,
                    "method": capture_result.get('method', 'unknown'),
                    "width": capture_result.get('width'),
                    "height": capture_result.get('height')
                },
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "duration_seconds": round(duration, 2),
                    "window_size": window_size,
                    "headless": headless
                }
            }
            
            print(f"✅ 保存完了: {relative_path}")
            print(f"📊 ファイルサイズ: {file_size:,} bytes ({file_size_mb:.2f} MB)")
            print(f"⏱️  処理時間: {duration:.2f}秒")
            
            return result
            
        except WebDriverException as e:
            error_msg = f"WebDriverエラー: {str(e)}"
            if not WEBDRIVER_MANAGER_AVAILABLE:
                error_msg += "\n💡 webdriver-managerのインストールを推奨: pip install webdriver-manager"
            
            return self._error_response(error_msg, url, start_time)
            
        except TimeoutException as e:
            return self._error_response(f"タイムアウトエラー: ページの読み込みが{self.timeout}秒を超えました", url, start_time)
            
        except Exception as e:
            return self._error_response(f"予期しないエラー: {str(e)}", url, start_time)
            
        finally:
            # WebDriverを確実に終了
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass

    def _error_response(self, error_msg: str, url: str, start_time: datetime) -> Dict[str, Any]:
        """エラーレスポンスを生成する"""
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"❌ {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "page": {
                "url": url
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": round(duration, 2)
            }
        }


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(
        description="AIエージェント向け高機能スクリーンショットツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 基本的な使用方法
  python screenshot.py --url https://example.com
  
  # フルページキャプチャを無効化
  python screenshot.py --url https://example.com --no-full-page
  
  # カスタム設定
  python screenshot.py --url https://example.com --prefix "test" --wait 5
  
  # デバッグ用（ブラウザを表示）
  python screenshot.py --url https://example.com --no-headless
        """
    )
    
    parser.add_argument("--url", required=True, help="スクリーンショットを撮るURL")
    parser.add_argument(
        "--output-folder",
        default="./screenshots",
        help="保存先フォルダ（デフォルト: ./screenshots）"
    )
    parser.add_argument(
        "--prefix",
        "--file-prefix",
        dest="file_prefix",
        default="screenshot",
        help="ファイル名のプレフィックス（デフォルト: screenshot）"
    )
    parser.add_argument(
        "--window-size",
        default="1920,1080",
        help="ウィンドウサイズ（デフォルト: 1920,1080）"
    )
    parser.add_argument(
        "--no-full-page",
        action="store_true",
        help="フルページスクリーンショットを無効化"
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=3,
        help="ページ読み込み後の追加待機時間（秒）"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="ページ読み込みのタイムアウト時間（秒）"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="ブラウザを表示する（デバッグ用）"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="結果をJSON形式で出力"
    )
    
    return parser.parse_args()


def main():
    """メイン関数（コマンドライン実行用）"""
    args = parse_args()
    
    tool = ScreenshotTool(timeout=args.timeout)
    result = tool.capture_screenshot(
        url=args.url,
        output_folder=args.output_folder,
        file_prefix=args.file_prefix,
        window_size=args.window_size,
        full_page=not args.no_full_page,
        wait_time=args.wait,
        headless=not args.no_headless
    )
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if not result["success"]:
            exit(1)


# エージェント向けのショートカット関数
def screenshot(
    url: str,
    output_folder: str = "./screenshots",
    file_prefix: str = "screenshot",
    full_page: bool = True,
    wait_time: int = 3,
    **kwargs
) -> Dict[str, Any]:
    """
    AIエージェントから直接呼び出せるスクリーンショット関数
    
    Args:
        url: スクリーンショットを撮るURL
        output_folder: 保存先フォルダ
        file_prefix: ファイル名のプレフィックス
        full_page: フルページスクリーンショットを撮るか
        wait_time: ページ読み込み後の待機時間
        **kwargs: その他のオプション
        
    Returns:
        実行結果の詳細な辞書
        
    Example:
        >>> result = screenshot("https://example.com")
        >>> if result["success"]:
        ...     print(f"保存先: {result['file']['relative_path']}")
    """
    tool = ScreenshotTool()
    return tool.capture_screenshot(
        url=url,
        output_folder=output_folder,
        file_prefix=file_prefix,
        full_page=full_page,
        wait_time=wait_time,
        **kwargs
    )


if __name__ == "__main__":
    main()