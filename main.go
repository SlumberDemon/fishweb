package main

import (
	"os"

	"github.com/slumberdemon/fishweb/cmd"
)

func main() {
	root := cmd.NewCmdRoot()
	if err := root.Execute(); err != nil {
		os.Exit(1)
	}
}
