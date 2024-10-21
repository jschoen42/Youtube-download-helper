
# Youtube download helper

requirements

``` python
 yt-dlp
```

venv with special Python version (powershell)

```console
 & 'C:\Program Files\_prog\Python312\python.exe' -m venv .venv-3.12
.venv-3.12\Scripts\activate
```

start

```console
python main.py rU5mxh5tsI0 (video + audio)
python main.py -a uJ1LbXU_hLQ (only audio)
```

if youtube id starts with '-':

```console
python main.py -YyWIuo-zUQ (not working)
 -> python main.py -a YyWIuo-zUQ
 -> python main.py -a -- -YyWIuo-zUQ
```
