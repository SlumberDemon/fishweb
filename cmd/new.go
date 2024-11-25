package cmd

import (
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
)

func NewCmdNew() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "new <name>",
		Short: "Create new fishweb app",
		Args:  cobra.ExactArgs(1),
		RunE: func(cmd *cobra.Command, args []string) error {
			appName := args[0]
			appDir := filepath.Join(os.ExpandEnv("$HOME/fishweb"), args[0])

			if _, err := os.Stat(appDir); !os.IsNotExist(err) {
				cmd.PrintErrf("app '%s' already exists", appName)
				return nil
			}

			if err := os.MkdirAll(appDir, 0755); err != nil {
				cmd.PrintErrf("failed to create app directory: %v", err)
				return nil
			}

			if _, err := os.Create(filepath.Join(appDir, "main.py")); err != nil {
				cmd.PrintErrf("failed to create main.py: %v", err)
				return nil
			}

			if err := createRequirements(filepath.Join(appDir, "requirements.txt")); err != nil {
				cmd.PrintErrf("failed to create requirements.txt: %v", err)
				return nil
			}

			fmt.Printf("Created app: %s\n", appName)

			return nil
		},
	}

	return cmd
}

func createRequirements(path string) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()

	_, err = fmt.Fprintln(f, "uvicorn")
	return err
}
