# CLI Reference

## fishweb

```
fishweb [command] [flags]
```

### Options

```
--version             -v        Show the version
--install-completion            Install completion for the current shell.
--show-completion               Show completion for the current shell, to copy it or customize the installation.
--help                          Show this message and exit.
```

## serve

Start fishweb server

```
fishweb serve [flags]
```

### Options

```
--host    -h      TEXT     host address to listen on
                           [default: localhost]
--port    -p      INTEGER  port number to listen on
                           [default: 8888]
--root    -r      PATH     root directory to serve apps from
                           [default: fishweb]
--reload  -r               enable live reloading
--help                     Show this message and exit.
```

## logs

View app log

```
fishweb logs [OPTIONS] [APP]
```

### Options

```
--all   -a            show logs for all apps
--root  -r      PATH  root directory to search for apps
                      [default: /Users/sofa/fishweb]
--help                Show this message and exit.
```
