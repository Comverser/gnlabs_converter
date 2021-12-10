### env tested

-   ubuntu 20.04
-   python >= 3.8

### install

```bash
pip3 install -r requirements.txt
pip3 install git+https://github.com/klintan/pypcd.git
```

### run

```bash
python ./src/gnlabs_converter.py <path>
```

### build

```bash
pip3 install Pyinstaller
pyinstaller --onefile ./src/gnlabs_converter.py
```
