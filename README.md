# Rhizome
> A simple Python HTTP/API server with a focus on plugins and config.

Rhizome is a lightweight HTTP server built on Python's `http.server` module. Rather than hard-coding routes or logic, everything is driven by **plugins** — Python modules that register themselves to URL hooks via a JSON config file. This makes it easy to spin up a local API or web server and extend it without touching the core.

---

## Features

- Zero external dependencies — pure Python stdlib
- Plugin system: any `.py` file in `plugins/` can become an API endpoint
- GET and POST support, with query string and body parsing
- Configurable access control (lock down plugins, config files, or the whole site)
- Coloured terminal output with request logging
- Auto-opens the server in your browser on start (optional)

---

## Getting Started

```bash
git clone https://github.com/SoftPankek7/Rhizome.git
cd Rhizome
python main.py
```
Python 3.10+ is required (uses `match` statements).

---

## Configuration

Server behaviour is controlled by `settings.json`:

```json
{
    "hostType": "localnet",
    "hostPort": 8080,
    "apiDir": "/api/",
    "indexFile": "index.html",
    "access": {
        "Plugin": false,
        "Config": false,
        "API":    true,
        "Website": true
    },
    "invalidAccess": "invalid.html",
    "openOnHost": true,
    "encoding": "UTF-8"
}
```

| Key | Description |
|---|---|
| `hostType` | `localhost`, `localnet`, `localnet2`, `quad0`, or a custom IP |
| `hostPort` | Port to listen on |
| `apiDir` | URL prefix for API hooks (e.g. `/api/`) |
| `indexFile` | File served at `/` |
| `access.Plugin` | Whether `plugins/` directory is publicly accessible |
| `access.Config` | Whether `modules.json` / `settings.json` are publicly accessible |
| `access.API` | Whether API hooks are enabled |
| `access.Website` | Whether static file serving is enabled |
| `invalidAccess` | HTML file shown when access is denied |
| `openOnHost` | Open browser automatically on start |
| `encoding` | Response encoding (usually `UTF-8`) |

---

## Plugins

Plugins live in the `plugins/` directory. Each is a plain Python file with (at minimum) an `api()` function as entrypoint - and `api_init()` for any specific init functions.

### Registering a plugin

Plugins are registered in `modules.json`:

```json
[
    {
        "name": "myplugin",
        "reason": "A short description",
        "apiHook": "myendpoint"
    }
]
```

This maps `GET /api/myendpoint` (and `POST /api/myendpoint`) to `plugins/myplugin.py`.

### Writing a plugin

```python
# plugins/myplugin.py

def api_init():
    """Called once when the server loads. Optional."""
    print("myplugin initialised")

def api(request):
    """
    request[0] — "GET" or "POST"
    request[1] — the raw BaseHTTPRequestHandler instance
    request[2] — parsed query params (dict of lists)
    """
    return {
        "body": "<h1>Hello from myplugin!</h1>",
        "mime": "text/html"
    }
```

### Plugin return values

Your `api()` function should return a dict with one of:

| Key | Effect |
|---|---|
| `body` | Respond with this content (string or bytes). Defaults to `text/html`. |
| `mime` | MIME type for the `body` response (e.g. `application/json`). |
| `redirect` | Issue a 302 redirect to this URL. |

Any can be None, but is not recommended.

---

## File Structure

```
Rhizome
.
├── Examples
│   ├── battery.html
│   └── proxy.html
|
├── index.html
├── invalid.html
├── main.py
├── modules.json
├── plugins
│   ├── alert.py
│   ├── battery.py
│   └── proxy.py
|
└── settings.json
```

---

## Examples

The `Examples/` directory contains sample plugins to get started.
The default `modules.json` ships with two demos:

- **`alert`** — demo plugin hooked to `/api/alertDemo`
- **`battery`** — reads and returns battery status, hooked to `/api/battery`

---

## License

MIT — see [LICENSE](LICENSE).
