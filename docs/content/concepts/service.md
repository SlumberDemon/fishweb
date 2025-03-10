# Service (TODO)

## Linux

::: code-group

``` [fishweb.service]
[Unit]
Description=Fishweb
After=network.target

[Service]
Type=simple
ExecStart=/home/pi/.local/bin/fishweb serve
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```
:::
