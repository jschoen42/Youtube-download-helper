### Helper: download youtube videos

#### CLI commands

``` bash
uv run src/main.py
uv run src/main.py -id <youtube id>

uv run src/main.py -a
uv run src/main.py -id <youtube id> -a
```

#### parameter

``` bash
-id, --youtube_id -> Youtube ID (11 characters)
-a, --audio       -> only audio track
-l, --language    -> force language
-d, --debug       -> show web traffic
```

#### download

``` bash
 -> ./data/video/<channel>/<title> (<video-id>+<audio-id>).mkv
 -> ./data/video/<channel>/<title> (<video-id>+<audio-id>).mp4
 -> ./data/audio/<channel>/<title> (<audio-id>).m4a
 -> ./data/audio/<channel>/<title> (<audio-id>).webm
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
