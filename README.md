# DMAF

Dynamic Multi-Agent Framework

## Dependencies

- autogen

```shell
git clone https://github.com/microsoft/autogen.git
cd autogen/python
uv sync  --all-extras
source .venv/bin/activate
cd packages/autogen-magentic-one
pip install -e .
```

- playwright

```shell
playwright install --with-deps chromium
```

- graphviz

```shell
sudo apt install graphviz
```

## Configuration

- .env

```python
CHAT_COMPLETION_PROVIDER='openai'
CHAT_COMPLETION_KWARGS_JSON={"api_key": "REPLACE_WITH_YOUR_API", "model": "gpt-4o-mini"}
```

## Run

```shell
/workspaces/autogen/python/.venv/bin/python /sandbox/autogen-magenticOne.py --logs_dir ./logs
```
