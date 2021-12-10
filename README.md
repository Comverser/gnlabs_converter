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
python ./src/converter.py
```

<!-- ### build

```bash
pip3 install Pyinstaller
mkdir ./standalone
pyinstaller --specpath ./standalone/spec --distpath ./standalone/dist --workpath ./standalone/build --onefile ./src/converter.py
``` -->
