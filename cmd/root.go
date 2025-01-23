package cmd

import (
	"github.com/spf13/cobra"
)

func NewCmdRoot() *cobra.Command {
	rootCmd := &cobra.Command{
		Use:           "fishweb",
		Short:         "Web apps like serverless",
		Version:       "dev",
		SilenceErrors: true,
	}

	rootCmd.AddCommand(NewCmdServe())
	rootCmd.AddCommand(NewCmdNew())

	return rootCmd
}
