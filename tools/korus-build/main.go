package main

import (
	"bufio"
	"flag"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
)

type crate struct {
	dir  string
	name string
}

func main() {
	only := flag.String("only", "", "comma-separated list of crates to build, e.g. korus_enemy_ai,korus_save (default: all)")
	debug := flag.Bool("debug", false, "build in debug mode instead of release")
	root := flag.String("path", "", "Korus project root (default: auto-detected by walking up from the current directory)")
	flag.Parse()

	projectRoot, err := resolveRoot(*root)
	if err != nil {
		fatal(err)
	}

	nativeDir := filepath.Join(projectRoot, "native")
	toolsDir := filepath.Join(projectRoot, "tools")

	crates, err := discoverCrates(nativeDir)
	if err != nil {
		fatal(err)
	}
	if len(crates) == 0 {
		fatal(fmt.Errorf("no crates found under %s", nativeDir))
	}

	if *only != "" {
		crates, err = filterCrates(crates, strings.Split(*only, ","))
		if err != nil {
			fatal(err)
		}
		if len(crates) == 0 {
			fatal(fmt.Errorf("--only matched no crates"))
		}
	}

	profile := "release"
	if *debug {
		profile = "debug"
	}

	var failed []string
	for _, c := range crates {
		fmt.Printf("\n=== building %s (%s) ===\n", c.name, profile)
		if err := cargoBuild(c, *debug); err != nil {
			fmt.Fprintf(os.Stderr, "build failed for %s: %v\n", c.name, err)
			failed = append(failed, c.name)
			continue
		}
		if err := copyBinary(c, profile, toolsDir); err != nil {
			fmt.Fprintf(os.Stderr, "copy failed for %s: %v\n", c.name, err)
			failed = append(failed, c.name)
			continue
		}
		fmt.Printf("-> %s\n", filepath.Join("tools", c.name+exeSuffix()))
	}

	if len(failed) > 0 {
		fmt.Fprintf(os.Stderr, "\n%d crate(s) failed: %s\n", len(failed), strings.Join(failed, ", "))
		os.Exit(1)
	}
	fmt.Printf("\nbuilt %d crate(s) successfully\n", len(crates))
}

func resolveRoot(explicit string) (string, error) {
	if explicit != "" {
		abs, err := filepath.Abs(explicit)
		if err != nil {
			return "", err
		}
		if !isDir(filepath.Join(abs, "native")) {
			return "", fmt.Errorf("%s does not contain a native/ directory", abs)
		}
		return abs, nil
	}

	start, err := os.Getwd()
	if err != nil {
		return "", err
	}
	for dir := start; ; {
		if isDir(filepath.Join(dir, "native")) && isDir(filepath.Join(dir, "tools")) {
			return dir, nil
		}
		parent := filepath.Dir(dir)
		if parent == dir {
			return "", fmt.Errorf("could not find a Korus project root (native/ + tools/) above %s; pass --path", start)
		}
		dir = parent
	}
}

func discoverCrates(nativeDir string) ([]crate, error) {
	entries, err := os.ReadDir(nativeDir)
	if err != nil {
		return nil, err
	}

	var crates []crate
	for _, e := range entries {
		if !e.IsDir() {
			continue
		}
		manifest := filepath.Join(nativeDir, e.Name(), "Cargo.toml")
		if _, err := os.Stat(manifest); err != nil {
			continue
		}
		name, err := packageName(manifest)
		if err != nil {
			return nil, fmt.Errorf("reading %s: %w", manifest, err)
		}
		crates = append(crates, crate{dir: filepath.Join(nativeDir, e.Name()), name: name})
	}
	return crates, nil
}

var packageNameRe = regexp.MustCompile(`^name\s*=\s*"([^"]+)"`)

func packageName(manifestPath string) (string, error) {
	f, err := os.Open(manifestPath)
	if err != nil {
		return "", err
	}
	defer f.Close()

	inPackage := false
	scanner := bufio.NewScanner(f)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if strings.HasPrefix(line, "[") {
			inPackage = line == "[package]"
			continue
		}
		if inPackage {
			if m := packageNameRe.FindStringSubmatch(line); m != nil {
				return m[1], nil
			}
		}
	}
	if err := scanner.Err(); err != nil {
		return "", err
	}
	return "", fmt.Errorf("no [package] name found")
}

func filterCrates(all []crate, requested []string) ([]crate, error) {
	byName := make(map[string]crate, len(all))
	names := make([]string, 0, len(all))
	for _, c := range all {
		byName[c.name] = c
		names = append(names, c.name)
	}

	var out []crate
	var unknown []string
	for _, r := range requested {
		r = strings.TrimSpace(r)
		if r == "" {
			continue
		}
		c, ok := byName[r]
		if !ok {
			unknown = append(unknown, r)
			continue
		}
		out = append(out, c)
	}
	if len(unknown) > 0 {
		return nil, fmt.Errorf("unknown crate(s) in --only: %s (available: %s)", strings.Join(unknown, ", "), strings.Join(names, ", "))
	}
	return out, nil
}

func cargoBuild(c crate, debug bool) error {
	args := []string{"build", "--manifest-path", filepath.Join(c.dir, "Cargo.toml")}
	if !debug {
		args = append(args, "--release")
	}
	cmd := exec.Command("cargo", args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func copyBinary(c crate, profile, toolsDir string) error {
	src := filepath.Join(c.dir, "target", profile, c.name+exeSuffix())
	dst := filepath.Join(toolsDir, c.name+exeSuffix())

	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()

	if err := os.MkdirAll(toolsDir, 0o755); err != nil {
		return err
	}

	tmp := dst + ".tmp"
	out, err := os.OpenFile(tmp, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0o755)
	if err != nil {
		return err
	}
	if _, err := io.Copy(out, in); err != nil {
		out.Close()
		os.Remove(tmp)
		return err
	}
	if err := out.Close(); err != nil {
		os.Remove(tmp)
		return err
	}
	return os.Rename(tmp, dst)
}

func exeSuffix() string {
	if runtime.GOOS == "windows" {
		return ".exe"
	}
	return ""
}

func isDir(path string) bool {
	info, err := os.Stat(path)
	return err == nil && info.IsDir()
}

func fatal(err error) {
	fmt.Fprintln(os.Stderr, "error:", err)
	os.Exit(1)
}
