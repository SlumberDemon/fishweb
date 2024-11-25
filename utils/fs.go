package utils

import "os"

func FileExists(p string) bool {
	_, err := os.Stat(p)
	return err == nil
}
