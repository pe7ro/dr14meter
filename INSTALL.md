## From sources

See: [https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-requirements]()

```bash
# create virtual environment (reusing installed packages)
python3 -m venv --system-site-packages venv
# or create clean environment:
python3 -m venv venv

# install 
venv/bin/python3 -m pip install -e .
# or
pipx install --system-site-packages .
```

# Debian
Use `pipx`.

# pipx / pip

```bash
pipx install dr14meter
# or 
pipx install --system-site-packages dr14meter
```

Installing from a wheel file:
```bash
pipx install dist/dr14meter-1.1.0a0-py3-none-any.whl
```

Uninstall:
```bash
pipx uninstall dr14meter
```

# Tests

```bash
venv/bin/python3 -m pip install -e . pytest
venv/bin/python3 -m pytest
```

Tests that decode FLAC need `ffmpeg` and `ffprobe` in PATH; the plotting tests need
`matplotlib` (and `scipy` for `--compress`). Missing tools skip those tests.

# Distribution (uploading to pypi)

```bash
venv/bin/python3 -m pip install --upgrade build
venv/bin/python3 -m build
venv/bin/python3 -m pip install --upgrade twine
venv/bin/python3 -m twine upload --repository testpypi dist/* -u __token__ -p pypi-XXX
venv/bin/python3 -m twine upload dist/* -u __token__ -p pypi-XXX
```