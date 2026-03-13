# Investment Analytics

## 開発方法

### 環境構築

#### 1. uv のインストール

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

参考：https://docs.astral.sh/uv/getting-started/installation

#### 2. tox-uv のインストール

```sh
uv tool install tox --with tox-uv
```

参考：https://github.com/tox-dev/tox-uv

#### 3. 仮想環境の構築

```sh
uv sync
```

#### 4. Streamlit アプリケーションの起動

```sh
uv run streamlit run src/main.py --server.port 8080
```

### テスト

```sh
tox run-parallel
```

### フォーマット

```sh
tox -e format
```
