# mypilot API Key Configuration Guide

このガイドでは、mypilotでAPIキーを設定する2つの方法について説明します。

## 方法1: launch_env.sh での一括管理（推奨）

### メリット
- 1つのファイルで全てのAPIキーを管理
- 設定の確認・変更が簡単
- 環境変数として動作するため、システム全体で利用可能

### 設定手順

1. **launch_env.shを編集**
   ```bash
   cd /data/openpilot
   nano launch_env.sh
   ```

2. **APIキーを設定**
   ```bash
   # API Keys Configuration
   # Set your API keys here for centralized management
   export MAPTILER_TOKEN="your_maptiler_api_key_here"
   export MAPBOX_TOKEN="your_mapbox_secret_token_here"
   ```

3. **ファイルを保存してopenpilotを再起動**
   ```bash
   sudo reboot
   ```

### APIキーの取得方法

#### MapTiler API Key
1. [MapTiler](https://maptiler.com) にアカウント登録
2. ダッシュボードでAPI キーを作成
3. API キーをコピーして `MAPTILER_TOKEN` に設定

#### Mapbox Token
1. [Mapbox](https://mapbox.com) にアカウント登録
2. Account → Access tokens ページに移動
3. **Secret token (sk.で始まる)** を作成
   - 必要なスコープ: `styles:read`, `fonts:read`, `datasets:read`, `geocoding:read`, `directions:read`
4. Secret tokenを `MAPBOX_TOKEN` に設定

## 方法2: インタラクティブスクリプト

### 設定手順

```bash
cd /data/openpilot
python setup_api_keys.py
```

スクリプトが以下の選択肢を提示します：
1. **launch_env.sh で設定** (推奨)
2. **デバイスパラメータで設定**
3. **現在の設定を確認**

## 設定の確認

### 環境変数の確認
```bash
echo $MAPTILER_TOKEN
echo $MAPBOX_TOKEN
```

### 設定確認スクリプト
```bash
cd /data/openpilot
python setup_api_keys.py
# オプション3を選択
```

## 優先順位

システムは以下の優先順位でAPIキーを使用します：

1. **環境変数** (`MAPTILER_TOKEN`, `MAPBOX_TOKEN`)
2. **デバイスパラメータ** (`CustomMapTilerTokenSk`, `CustomMapboxTokenSk`)
3. **デフォルト** (comma.aiサービス)

## トラブルシューティング

### 環境変数が認識されない
- openpilotを再起動してください
- launch_env.shの構文が正しいか確認してください

### APIキーのエラー
- APIキーが正しいか確認してください
- MapboxはSecret token (sk.で始まる) を使用してください
- 必要な権限がAPIキーに設定されているか確認してください

### 設定の初期化
デバイスパラメータをクリアする場合：
```bash
cd /data/openpilot
python -c "from openpilot.common.params import Params; p = Params(); p.delete('CustomMapTilerTokenSk'); p.delete('CustomMapboxTokenSk'); p.delete('CustomMapboxTokenPk')"
```

## 最小設定

基本的な動作には以下が必要です：
- **MapTiler API Key**: 地図表示用
- **Mapbox Secret Token**: ナビゲーション・ジオコーディング用

## サポート

問題が発生した場合は、以下を確認してください：
1. APIキーが正しく設定されているか
2. 必要な権限がAPIキーに含まれているか  
3. インターネット接続が正常か

詳細については [GitHub リポジトリ](https://github.com/KouMasuda/mypilot) をご覧ください。
