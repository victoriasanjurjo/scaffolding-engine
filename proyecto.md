# Sistema de Notificaciones

```tree
mi-proyecto/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── config.py
│   └── main.py
├── tests/
│   └── test_engine.py
├── .gitignore
├── README.md
└── requirements.txt
```

### `src/config.py`

```python
import os

DEBUG = os.getenv("DEBUG", "True") == "True"
APP_NAME = "EngineScaffold"
```

### `.gitignore`

```text
__pycache__/
*.pyc
.env
.venv/
dist/
build/
```
