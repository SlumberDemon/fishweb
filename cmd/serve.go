package cmd

import (
	"bytes"
	"fmt"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"time"

	"github.com/slumberdemon/fishweb/utils"
	"github.com/spf13/cobra"
)

func NewCmdServe() *cobra.Command {
	var flags struct {
		port     int
		rootDir  string
		hostname string
	}

	cmd := &cobra.Command{
		Use:   "serve",
		Short: "Start fishweb server",
		Args:  cobra.NoArgs,
		RunE: func(cmd *cobra.Command, args []string) error {
			if strings.HasPrefix(flags.rootDir, "~/") {
				home, err := os.UserHomeDir()
				if err != nil {
					return fmt.Errorf("failed to get home directory: %v", err)
				}
				flags.rootDir = filepath.Join(home, flags.rootDir[2:])
			}

			if err := os.MkdirAll(flags.rootDir, 0755); err != nil {
				return fmt.Errorf("failed to create root directory: %v", err)
			}

			server := &http.Server{
				Addr: fmt.Sprintf("%s:%d", flags.hostname, flags.port),
				Handler: &FishwebHandler{
					rootDir: flags.rootDir,
					apps:    make(map[string]*AppProcess),
				},
			}

			fmt.Printf("Starting Fishweb server on http://%s:%d\n", flags.hostname, flags.port)
			return server.ListenAndServe()
		},
	}

	cmd.Flags().IntVarP(&flags.port, "port", "p", 8888, "Port to run the server on")
	cmd.Flags().StringVarP(&flags.rootDir, "root", "r", "~/fishweb", "Root directory for applications")
	cmd.Flags().StringVarP(&flags.hostname, "hostname", "H", "localhost", "Hostname to listen on")

	return cmd
}

type AppProcess struct {
	cmd      *exec.Cmd
	port     int
	lastUsed time.Time
	shutdown chan struct{}
}

type FishwebHandler struct {
	rootDir string
	apps    map[string]*AppProcess
}

func (h *FishwebHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	hostParts := strings.Split(r.Host, ":")
	domains := strings.Split(hostParts[0], ".")

	if len(domains) < 2 {
		http.Error(w, "Invalid domain. Please use <app-name>.localhost", http.StatusBadRequest)
		return
	}

	subDomain := domains[0]
	appDir := filepath.Join(h.rootDir, subDomain)

	if _, err := os.Stat(appDir); os.IsNotExist(err) {
		http.Error(w, fmt.Sprintf("Application '%s' not found", subDomain), http.StatusNotFound)
		return
	}

	if _, err := os.Stat(filepath.Join(appDir, "main.py")); os.IsNotExist(err) {
		http.Error(w, fmt.Sprintf("main.py not found in %s", appDir), http.StatusNotFound)
		return
	}

	app, err := h.getOrStartApp(subDomain, appDir)
	if err != nil {
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		fmt.Printf("Error starting application %s: %v\n", subDomain, err)
		return
	}

	app.lastUsed = time.Now()

	target, _ := url.Parse(fmt.Sprintf("http://localhost:%d", app.port))
	proxy := httputil.NewSingleHostReverseProxy(target)
	proxy.ServeHTTP(w, r)
}

func (h *FishwebHandler) getOrStartApp(appName, appDir string) (*AppProcess, error) {
	if app, exists := h.apps[appName]; exists {
		resp, err := http.Get(fmt.Sprintf("http://localhost:%d", app.port))
		if err == nil {
			resp.Body.Close()
			return app, nil
		}
		delete(h.apps, appName)
	}

	port := getFreePort()
	if port == 0 {
		return nil, fmt.Errorf("no free ports available")
	}

	uv, err := uvExecutable()
	if err != nil {
		return nil, fmt.Errorf("could not find uv executable")
	}

	var stderr bytes.Buffer
	cmd := exec.Command(uv,
		"run",
		"--with-requirements", "requirements.txt",
		"uvicorn",
		"main:app",
		"--port", strconv.Itoa(port),
		"--ws", "none",
		"--lifespan", "off",
		"--timeout-keep-alive", "30",
	)

	envFile := filepath.Join(appDir, ".env")
	if _, err := os.Stat(envFile); err == nil {
		cmd.Args = append(cmd.Args, "--env-file", envFile)
	}

	cmd.Dir = appDir
	cmd.Stderr = &stderr

	if err := cmd.Start(); err != nil {
		return nil, fmt.Errorf("failed to start uv: %v\nstderr: %s", err, stderr.String())
	}

	app := &AppProcess{
		cmd:      cmd,
		port:     port,
		lastUsed: time.Now(),
		shutdown: make(chan struct{}),
	}
	h.apps[appName] = app

	go h.monitorApp(appName, app)

	if err := waitForAppWithTimeout(port, 30*time.Second); err != nil {
		cmd.Process.Kill()
		delete(h.apps, appName)
		return nil, fmt.Errorf("application failed to start: %v", err)
	}

	return app, nil
}

func (h *FishwebHandler) monitorApp(appName string, app *AppProcess) {
	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			if time.Since(app.lastUsed) > 0 {
				app.cmd.Process.Kill()
				delete(h.apps, appName)
				close(app.shutdown)
				return
			}
		case <-app.shutdown:
			return
		}
	}
}

func waitForAppWithTimeout(port int, timeout time.Duration) error {
	endpoint := fmt.Sprintf("http://localhost:%d", port)
	backoff := 100 * time.Millisecond

	start := time.Now()
	for time.Since(start) < timeout {
		resp, err := http.Get(endpoint)
		if err == nil {
			resp.Body.Close()
			return nil
		}
		time.Sleep(backoff)
	}

	return fmt.Errorf("application failed to start within timeout")
}

func getFreePort() int {
	listener, err := net.Listen("tcp", ":0")
	if err != nil {
		return 0
	}
	defer listener.Close()

	return listener.Addr().(*net.TCPAddr).Port
}

func uvExecutable() (string, error) {
	if uvPath, err := exec.LookPath("uv"); err == nil {
		return uvPath, nil
	}

	homedir, err := os.UserHomeDir()
	if err != nil {
		return "", err
	}

	for _, candidate := range []string{
		filepath.Join(homedir, ".local", "bin", "uv"),
		"/usr/local/bin/uv",
		// add extra paths for homebrew etc to allow none standalone version to be used
	} {
		if utils.FileExists(candidate) {
			return candidate, nil
		}
	}

	return "", fmt.Errorf("uv not found")
}
