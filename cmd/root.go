package cmd

import (
	"github.com/spf13/cobra"
)

func NewCmdRoot() *cobra.Command {
	cmd := &cobra.Command{
		Use:           "fishweb",
		Short:         "Web apps like serverless",
		Version:       "dev",
		SilenceErrors: true,
	}

	cmd.AddCommand(NewCmdServe())

	return cmd
}
