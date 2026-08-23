package main

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"log/slog"
	"net"
	"os/exec"
	"regexp"
	"strings"
	"sync"
	"time"

	_ "embed"

	"github.com/abenz1267/elephant/v2/internal/comm/handlers"
	"github.com/abenz1267/elephant/v2/internal/util"
	"github.com/abenz1267/elephant/v2/pkg/common"
	"github.com/abenz1267/elephant/v2/pkg/pb/pb"
)

var (
	Name       = "translate"
	NamePretty = "Translate"
	config     *Config
)

//go:embed README.md
var readme string

const (
	ActionCopy = "copy"
)

type Config struct {
	common.Config `koanf:",squash"`
	Placeholder   string `koanf:"placeholder" desc:"placeholder shown while translating" default:"translating…"`
	MinChars      int    `koanf:"min_chars" desc:"don't translate if query is shorter than min_chars" default:"2"`
	TargetLang    string `koanf:"target_lang" desc:"target language code for translate-shell (ISO 639-1, e.g. en, ru, de)" default:"en"`
	Command       string `koanf:"command" desc:"translate-shell command. supports %LANG% and %QUERY%" default:"trans -brief -no-ansi :%LANG% -- %QUERY%"`
	CopyCommand   string `koanf:"copy_command" desc:"command to copy the translated result. supports %VALUE%" default:"wl-copy -n '%VALUE%'"`
	Async         bool   `koanf:"async" desc:"translate asynchronously (live update while typing)" default:"true"`
}

var (
	resultsMu sync.Mutex
	results   = map[string]string{}
)

func Setup() {
	LoadConfig()
}

func LoadConfig() {
	config = &Config{
		Config: common.Config{
			Icon: "accessories-dictionary-symbolic",
		},
		Placeholder: "translating…",
		MinChars:    2,
		TargetLang:  "en",
		Command:     "trans -brief -no-ansi :%LANG% -- %QUERY%",
		CopyCommand: "wl-copy -n '%VALUE%'",
		Async:       true,
	}

	common.LoadConfig(Name, config)

	if config.NamePretty != "" {
		NamePretty = config.NamePretty
	}
}

func Available() bool {
	p, err := exec.LookPath("trans")

	if p == "" || err != nil {
		slog.Info(Name, "available", "translate-shell (trans) not found. disabling")
		return false
	}

	return true
}

func PrintDoc(write bool) {
	if !write {
		fmt.Println(readme)
		fmt.Println()
	}

	util.PrintConfig(config, Name, write)
}

var langRe = regexp.MustCompile(`^([a-z]{2,3}):(.+)$`)

func parseQuery(query string) (string, string) {
	lang := config.TargetLang
	text := query

	if m := langRe.FindStringSubmatch(query); m != nil {
		lang = m[1]
		text = strings.TrimSpace(m[2])
	}

	return lang, text
}

func runTranslate(lang, query string) (string, error) {
	shellQuery := strings.ReplaceAll(config.Command, "%LANG%", lang)
	shellQuery = strings.ReplaceAll(shellQuery, "%QUERY%", query)

	cmd := exec.Command("sh", "-c", shellQuery)

	out, err := cmd.Output()
	if err != nil {
		return "", err
	}

	return strings.TrimSpace(string(out)), nil
}

func Query(conn net.Conn, query string, _ []rune, single bool, _ bool, format uint8) []*pb.QueryResponse_Item {
	start := time.Now()

	entries := []*pb.QueryResponse_Item{}

	if query != "" && len(query) >= config.MinChars {
		sum := md5.Sum([]byte(query))
		identifier := hex.EncodeToString(sum[:])

		resultsMu.Lock()
		cached, hit := results[query]
		resultsMu.Unlock()

		text := config.Placeholder
		if hit {
			text = cached
		}

		e := &pb.QueryResponse_Item{
			Identifier: identifier,
			Text:       text,
			Icon:       config.Icon,
			Subtext:    query,
			Provider:   Name,
			Score:      1,
			Type:       pb.QueryResponse_REGULAR,
			State:      []string{"current"},
			Actions:    []string{ActionCopy},
		}

		if !hit {
			if config.Async {
				go func() {
					lang, text := parseQuery(query)
					result, err := runTranslate(lang, text)
					if err != nil {
						slog.Error(Name, "translate", err)
						e.Text = "%DELETE%"
					} else {
						e.Text = result
						resultsMu.Lock()
						results[query] = result
						resultsMu.Unlock()
					}

					handlers.UpdateItem(format, query, conn, e)
				}()

				entries = append(entries, e)
			} else {
				lang, text := parseQuery(query)
				result, err := runTranslate(lang, text)
				if err == nil {
					e.Text = result
					resultsMu.Lock()
					results[query] = result
					resultsMu.Unlock()
					entries = append(entries, e)
				}
			}
		} else {
			entries = append(entries, e)
		}
	}

	slog.Debug(Name, "query", time.Since(start))

	return entries
}

func Activate(single bool, identifier, action string, query string, args string, format uint8, conn net.Conn) {
	switch action {
	case ActionCopy:
		resultsMu.Lock()
		result, hit := results[query]
		resultsMu.Unlock()

		if !hit {
			var err error
			lang, text := parseQuery(query)
			result, err = runTranslate(lang, text)
			if err != nil {
				slog.Error(Name, "copy", err)
				return
			}
		}

		cmd := common.ReplaceResultOrStdinCmd(config.CopyCommand, result)

		err := cmd.Start()
		if err != nil {
			slog.Error(Name, "copy", err)
			return
		}

		go func() {
			cmd.Wait()
		}()
	default:
		slog.Error(Name, "activate", fmt.Sprintf("unknown action: %s", action))
	}
}

func Icon() string {
	return config.Icon
}

func HideFromProviderlist() bool {
	return config.HideFromProviderlist
}

func State(provider string) *pb.ProviderStateResponse {
	return &pb.ProviderStateResponse{
		Actions: []string{},
	}
}
