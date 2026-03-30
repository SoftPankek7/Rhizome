---

kanban-plugin: board

---

## Pre-Release

- [x] HTML + JS boilerplate
- [x] Simple Web Server Model
- [x] Python API (HTTP -> FUNCTION)


## Production

- [x] Startup Messages (Version, Verbose, Plugins, etc.)
- [x] Security
- [x] Demo usage
- [x] Lock-Down API, make it reject illegal operations
- [x] Remove webserver module, or lock it behind a True/False var
- [x] Startup Log


## Features

- [x] Support Plugins
- [x] localhost & prod mode (or a custom mode selector)
- [x] \<forms\> support
- [x] Gigantic Config Thought Model


## Intergration

- [ ] Custom pseudo-markdown
- [ ] Package manager for plugins


## Additional Later-Stage

- [ ] Custom Black/Whitelist
- [ ] API Key support
- [ ] Check if settings are correct
- [x] Custom encodings
- [x] Patch the ``exec()`` import hack
- [x] Custom error messages
- [x] Allow webserver-like features (more directories, etc.)


***

%% kanban:settings
```
{"kanban-plugin":"board","list-collapse":[true,true,true,false,false],"show-checkboxes":true}
```
%%
