### Helper: download youtube videos

#### CLI commands

``` bash
python src/main.py
python src/main.py -id <youtube id>
python src/main.py -id <youtube id> -a

uv run src/main.py
uv run src/main.py -id <youtube id>
uv run src/main.py -id <youtube id> -a
```

#### parameter

``` bash
-id, --youtube_id -> Youtube ID (11 characters)
-l, --language    -> audio language (default="de")
-a, --audio       -> only audio track
-d, --debug       -> show web traffic
```

#### download

``` bash
 -> ./result/video/<channel>/<title>.webm
 -> ./result/audio/<channel>/<title>.m4a
```

#### dependencies

``` bash
- click  -> https://pypi.org/project/click
- yt-dlp -> https://pypi.org/project/yt-dlp
```

#### static type check

``` bash
uv run _mypy.py src
uv run _pyright.py src
uv run _basedpyright.py src
```
