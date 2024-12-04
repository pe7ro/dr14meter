## From sources

See: [https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-requirements]()

```commandline
# create virtual environment
python3 -m venv venv
# or to use system installed packages:
python3 -m venv --system-site-packages venv

# install 
venv/bin/python3 -m pip install -e .
```

# Debian
Use `pipx`.

```commandline
pipx install dr14meter
# or 
pipx install --system-site-packages dr14meter
```

Installing from a wheel file:
```commandline
pipx install dist/dr14meter-1.1.0a0-py3-none-any.whl
```

Uninstall:
```commandline
pipx uninstall dr14meter
```

# Distribution

```commandline
venv/bin/python3 -m pip install --upgrade build
venv/bin/python3 -m build
venv/bin/python3 -m pip install --upgrade twine
venv/bin/python3 -m twine upload --repository testpypi dist/* -u __token__ -p pypi-XXX
venv/bin/python3 -m twine upload dist/* -u __token__ -p pypi-XXX
```