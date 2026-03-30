from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import webbrowser # See config
import json       # For the config
import sys        # For the plugins
import os         # For the plugins

version = "1.3.1"

class output:
    class verbose:
        def error(string, quit=None, end="\n", flush=False):
            print(output.colors.red+output.colors.bold + "ERROR"+ output.colors.reset +": "+string, end=end, flush=flush)
            if quit != None:
                exit(quit)

        def info(string, quit=None, end="\n", flush=False):
            print(output.colors.blue+output.colors.bold + "INFO "+ output.colors.reset +": "+string, end=end, flush=flush)
            if quit != None:
                exit(quit)
        
        def warn(string, quit=None, end="\n", flush=False):
            print(output.colors.orange+output.colors.bold + "WARN "+ output.colors.reset +": "+string, end=end, flush=flush)
            if quit != None:
                exit(quit)
            
        class requests:
            def post(string, quit=None, end="\n", flush=False):
                print(output.colors.dim+output.colors.orange+output.colors.bold + "POST "+ output.colors.reset +": "+string, end=end, flush=flush)
                if quit != None:
                    exit(quit)
            
            def get(string, quit=None, end="\n", flush=False):
                print(output.colors.green+output.colors.dim+output.colors.bold + "GET  "+ output.colors.reset +": "+string, end=end, flush=flush)
                if quit != None:
                    exit(quit)
            
            def unknown(string, quit=None, end="\n", flush=False):
                print(output.colors.dim+output.colors.red+output.colors.bold + "???? "+ output.colors.reset +": "+string, end=end, flush=flush)
                if quit != None:
                    exit(quit)
    
    class colors:
        reset= "\033[0m"
        bold = "\033[1m"
        dim  = "\033[2m"
        italic="\033[3m"
        underl="\033[4m"
        blink ="\033[5m"
        reverse="\033[7m"
        strike="\033[9m"
        dblunderl="\033[21m"

        black = "\033[30m"
        red   = "\033[31m"
        green = "\033[32m"
        blue  = "\033[34m"

        cyan  = "\033[36m"
        purple= "\033[35m"
        orange= "\033[33m"

output.verbose.info("Rhizome v"+version)
output.verbose.info("PyHTTP Server "+BaseHTTPRequestHandler.server_version)
output.verbose.info("Python v"+sys.version+"\n")
output.verbose.info("Starting up...")
output.verbose.info("Loading settings")

try:
    with open("settings.json") as f:
        settings = json.load(f)

        if len(settings) < 8:
            output.verbose.error("The settings.json file does not contain any/enough settings.", 7)

except FileNotFoundError:
    output.verbose.error("The settings.json file does not exist.", 8)


output.verbose.info("Done loading settings.")
output.verbose.info("Dumping settings..")

for i in settings:
    output.verbose.info(str(i) + "=" + str(settings[i]))

# TODO : Add API black/whitelist
# TODO : Add API key support

output.verbose.info("Generating hostname..")

match settings["hostType"]:
    case "localhost":
        hostName = "localhost"
    case "localnet" :
        try:
            import socket
            hostName = socket.gethostbyname(socket.gethostname())
        except ImportError:
            output.verbose.error("Socket is not installed. Please run pip install socket, or set the hostType to quad0.", 6)
        except Exception as Err:
            output.verbose.error("Socket failed to get localip. See below.")
            output.verbose.error(str(Err))
    case "localnet2":
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        hostName = s.getsockname()[0]
        s.close()
    case "quad0":
        hostName = "0.0.0.0"
    case _:
        hostName = settings["hostType"]

output.verbose.info(f"Picked {hostName} (hostType={settings["hostType"]})")
output.verbose.info("Starting to import plugins")

# HACK : Cheeky hack to import from the plugins/ folder too
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'plugins'))
sys.path.append(module_path)


_cache_plugins = {}

def _load_mod(name):
    try:
        out = __import__(name)
        output.verbose.info(f"Loaded {name}")
        return out
    except ImportError:
        output.verbose.error(f"Invalid module name ({name})")

def load_modules():
    try:
        with open("modules.json") as f:
            global modules
            modules = json.load(f)

            if len(modules) == 0:
                output.verbose.warn("The modules.json file does not contain any APIs.")

    except FileNotFoundError:
        output.verbose.error("The modules.json file does not exist.", 4)

    plugins_list = []

    for i in modules:
        target_import = i["name"]
        reason_import = i["reason"]

        plugins_list.append(i["name"])

        output.verbose.info(f"Importing {target_import} ({reason_import})")
        initp = _load_mod(target_import)

        _cache_plugins[i["name"]] = initp

        if hasattr(initp, "api_init"):
            initp.api_init()
        else:
            output.verbose.warn(f"{target_import} has no api_init()")

    output.verbose.info(f"Done. Loaded {len(plugins_list)} plugins.")

load_modules()

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith(settings["apiDir"]) and settings["access"]["API"]:
            for i in modules:
                if settings["apiDir"] + i["apiHook"] == self.path.split("?")[0]:
                    output.verbose.info(f"Using API '{i['name']}' for hook '{i['apiHook']}' ({i['reason']})")
                    tempMod = _cache_plugins[i["name"]]

                    params = parse_qs(urlparse(self.path).query, keep_blank_values=True)

                    _output = tempMod.api(["GET", self, params])

                    if _output.get("redirect"):
                        self.send_response(302)
                        self.send_header("Location", _output["redirect"])
                        self.end_headers()

                    elif _output.get("body"):
                        self.send_response(200)
                        mime = _output.get("mime") or "text/html"
                        self.send_header("Content-Type", mime)
                        self.end_headers()
                        body = _output["body"]

                        if isinstance(body, bytes):
                            self.wfile.write(body)
                        else:
                            self.wfile.write(body.encode(settings["encoding"]))

        elif self.path.split("?")[0] in [settings["indexFile"], "/"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            with open(settings["indexFile"]) as serve:
                for i in serve.readlines():
                    self.wfile.write(bytes(i, encoding=settings["encoding"]))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            path = self.path.split("?")[0].lstrip("/")
             
            if path.startswith("plugins/") and not settings["access"]["Plugin"]:
                with open(settings["invalidAccess"]) as serve:
                    for i in serve.readlines():
                        self.wfile.write(bytes(i, encoding=settings["encoding"]))
            elif path in ["modules.json", "settings.json"] and not settings["access"]["Config"]:
                with open(settings["invalidAccess"]) as serve:
                    for i in serve.readlines():
                        self.wfile.write(bytes(i, encoding=settings["encoding"]))
            elif not settings["access"]["Website"]:
                with open(settings["invalidAccess"]) as serve:
                    for i in serve.readlines():
                        self.wfile.write(bytes(i, encoding=settings["encoding"]))
            else:
                try:
                    with open(path) as serve:
                        for i in serve.readlines():
                            self.wfile.write(bytes(i, encoding=settings["encoding"]))
                except FileNotFoundError:
                    output.verbose.warn(f"Could not find '{path}'. Dropping connection.")
                

    def do_POST(self):
        if self.path.startswith(settings["apiDir"]) and settings["access"]["API"]:
            for i in modules:
                
                # print(self.path)
                # print(self.path.split("?")[0])
                if settings["apiDir"] + i["apiHook"] == self.path.split("?")[0]:
                    tempMod = _cache_plugins[i["name"]]

                    content_length = int(self.headers["Content-Length"])
                    post_data = self.rfile.read(content_length).decode(settings["encoding"])

                    params = parse_qs(post_data, keep_blank_values=True)

                    # print(params)
                    _output = tempMod.api(["POST", self, params])

                    if _output.get("redirect"):
                        self.send_response(302)
                        self.send_header("Location", _output["redirect"])
                        self.end_headers()

                    elif _output.get("body"):
                        self.send_response(200)
                        mime = _output.get("mime") or "text/html"
                        self.send_header("Content-Type", mime)
                        self.end_headers()
                        body = _output["body"]

                        if isinstance(body, bytes):
                            self.wfile.write(body)
                        else:
                            self.wfile.write(body.encode(settings["encoding"]))
        else:
            try:
                with open(settings["invalidAccess"]) as serve:
                    for i in serve.readlines():
                        self.wfile.write(bytes(i, encoding=settings["encoding"]))
            except FileNotFoundError:
                output.verbose.warn(f"Could not find essential file '{self.path.split("?")[0]}'. Dropping connection.")

    def log_message(self, format, *args):
        if self.command == "POST":
            output.verbose.requests.post(f"(POST) {self.client_address} {self.path} {self.request_version}")
        elif self.command == "GET":
            output.verbose.requests.get(f"(GET) {self.client_address} {self.path} {self.request_version}")
        else:
            output.verbose.requests.unknown(f"({self.command}) {self.client_address} {self.path} {self.request_version}")


if __name__ == "__main__":
    webServer = HTTPServer((hostName, settings["hostPort"]), Server)
    output.verbose.info("Server started http://%s:%s" % (hostName, settings["hostPort"]))

    if settings["openOnHost"]:
        webbrowser.open("http://%s:%s" % (hostName, settings["hostPort"]))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")