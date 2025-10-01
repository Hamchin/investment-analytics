# Investment Analyzer

## 開発方法

#### 1. pyenv の設定

```sh
pyenv install 3.12
pyenv local 3.12
```

#### 2. 仮想環境の作成

```sh
python -m venv venv
```

#### 3. 仮想環境のアクティベート

```sh
source venv/bin/activate
```

#### 4. 依存関係のインストール

```sh
pip install -r requirements.txt
```

#### 5. Streamlit アプリケーションの起動

```sh
streamlit run app/main.py --server.port 8080
```

#### 6. (開発終了時) 仮想環境の終了

```sh
deactivate
```
