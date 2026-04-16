#!/usr/bin/env python3
"""
FTS5 Onboarding Setup
首次使用時引導使用者設定 API Key
"""

import os
import sys
import json

SETUP_FILE = os.path.expanduser("~/.openclaw/fts5.env")
CONFIG_FILE = os.path.expanduser("~/.openclaw/config.json")
OPENCLAW_DIR = os.path.expanduser("~/.openclaw")


def check_openclaw_dir():
    """確保 ~/.openclaw 目錄存在"""
    if not os.path.exists(OPENCLAW_DIR):
        print(f"❌ OpenClaw 目錄不存在：{OPENCLAW_DIR}")
        print("   請先安裝 OpenClaw")
        return False
    return True


def check_current_config():
    """檢查現有設定"""
    print("🔍 檢查現有設定...")
    
    # 1. 環境變數
    env_key = os.environ.get("MINIMAX_API_KEY")
    if env_key:
        print("✅ 偵測到環境變數 MINIMAX_API_KEY")
        return True, "env"
    
    # 2. 設定檔
    if os.path.exists(SETUP_FILE):
        with open(SETUP_FILE, 'r') as f:
            content = f.read()
            if "sk-cp-" in content or "YOUR_API_KEY" in content:
                print("⚠️ 偵測到設定檔，但尚未填入真實 API Key")
                return False, "config_empty"
            with open(SETUP_FILE, 'r') as f2:
                for line in f2:
                    if line.startswith("MINIMAX_API_KEY=") and len(line.split("=", 1)[1].strip()) > 10:
                        print("✅ 偵測到設定檔中的 API Key")
                        return True, "config"
    
    # 3. config.json
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                if "fts5" in config and config["fts5"].get("api_key"):
                    print("✅ 偵測到 config.json 中的 API Key")
                    return True, "config_json"
        except:
            pass
    
    return False, None


def prompt_api_key():
    """引導使用者輸入 API Key"""
    print("\n" + "="*50)
    print("📋 FTS5 系統設定")
    print("="*50)
    print("""
FTS5 需要 MiniMax API Key 才能運作。

請選擇設定方式：

1. 環境變數（建議）
   export MINIMAX_API_KEY=sk-cp-xxxxxxxxxxxxx
   # 然後重新執行此腳本

2. 設定檔（一次性設定）
   輸入您的 API Key，我們會幫您建立設定檔

3. 略過（稍後手動設定）
   您可以稍後編輯 ~/.openclaw/fts5.env
""")
    
    choice = input("請選擇 [1/2/3]: ").strip()
    
    if choice == "1":
        if os.environ.get("MINIMAX_API_KEY"):
            print("✅ 環境變數已設定")
            return True
        else:
            print("❌ 請先設定環境變數後重新執行")
            print("   export MINIMAX_API_KEY=sk-cp-xxxxxxxxxxxxx")
            return False
    
    elif choice == "2":
        return setup_config_file()
    
    elif choice == "3":
        create_empty_config()
        print("✅ 已建立空白設定檔，請稍後編輯 ~/.openclaw/fts5.env")
        return False
    
    else:
        print("❌ 無效選項")
        return False


def setup_config_file():
    """設定設定檔"""
    print("\n📝 請輸入您的 MiniMax API Key")
    print("   (格式：sk-cp-xxxxxxxxxxxxx)")
    
    api_key = input("\nAPI Key: ").strip()
    
    if not api_key or len(api_key) < 20:
        print("❌ API Key 格式不正確")
        return False
    
    if not api_key.startswith("sk-"):
        print("⚠️ API Key 通常以 sk- 開頭，確認嗎？")
        confirm = input("繼續？ [y/N]: ").strip().lower()
        if confirm != 'y':
            return False
    
    # 建立設定檔
    os.makedirs(os.path.dirname(SETUP_FILE), exist_ok=True)
    
    with open(SETUP_FILE, 'w') as f:
        f.write(f"# FTS5 設定檔\n")
        f.write(f"# 請填入您的 MiniMax API Key\n")
        f.write(f"MINIMAX_API_KEY={api_key}\n")
    
    print(f"\n✅ 設定檔已儲存：{SETUP_FILE}")
    return True


def create_empty_config():
    """建立空白設定檔"""
    os.makedirs(os.path.dirname(SETUP_FILE), exist_ok=True)
    
    with open(SETUP_FILE, 'w') as f:
        f.write("# FTS5 設定檔\n")
        f.write("# 請填入您的 MiniMax API Key\n")
        f.write("MINIMAX_API_KEY=sk-cp-YOUR_KEY_HERE\n")
    
    print(f"✅ 已建立空白設定檔：{SETUP_FILE}")


def verify_setup():
    """驗證設定是否正確"""
    print("\n🔧 驗證設定...")
    
    # 讀取 API Key
    api_key = None
    
    env_key = os.environ.get("MINIMAX_API_KEY")
    if env_key:
        api_key = env_key
        print("✅ 使用環境變數")
    
    if not api_key and os.path.exists(SETUP_FILE):
        with open(SETUP_FILE, 'r') as f:
            for line in f:
                if line.startswith("MINIMAX_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    if key and key != "sk-cp-YOUR_KEY_HERE":
                        api_key = key
                        print("✅ 使用設定檔")
                        break
    
    if not api_key:
        print("❌ 無法讀取 API Key")
        return False
    
    # 測試連線
    print("\n🧪 測試 API 連線...")
    try:
        import urllib.request
        import json
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": "MiniMax-M2.7",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Hi"}]
        }
        
        req = urllib.request.Request(
            "https://api.minimax.io/anthropic/v1/messages",
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            print("✅ API 連線成功！")
            return True
            
    except Exception as e:
        print(f"❌ API 連線失敗：{e}")
        return False


def main():
    print("🚀 FTS5 Onboarding Setup")
    print("="*50)
    
    # 檢查 OpenClaw 目錄
    if not check_openclaw_dir():
        sys.exit(1)
    
    # 檢查現有設定
    configured, source = check_current_config()
    
    if configured:
        print(f"\n✅ FTS5 已設定完成（來源：{source}）")
        verify = input("是否要驗證？ [Y/n]: ").strip().lower()
        if verify != 'n':
            if verify_setup():
                print("\n🎉 FTS5 已就緒！")
            else:
                print("\n⚠️ 設定可能有问题，請重新執行此腳本")
        return
    
    # 尚未設定，引導設定
    print("\n⚠️ 尚未設定 FTS5 API Key")
    if prompt_api_key():
        if verify_setup():
            print("\n🎉 FTS5 設定完成！")
        else:
            print("\n⚠️ 設定完成但驗證失敗，請檢查 API Key")


if __name__ == "__main__":
    main()