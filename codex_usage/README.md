# Codex Usage

Noctalia 5 popup panel for Codex quota usage and reset times. The gauge shows remaining quota.

Toggle with `noctalia msg panel-toggle zerodice0/codex_usage:panel`.
Bind this command to a compositor shortcut to open and close the panel with the same key.

Requires Python 3.11+, Codex CLI signed in with a ChatGPT account, and Noctalia plugin API 26+.
Fetches on open and every 5 minutes while visible. No background polling while closed.
An in-flight request is bounded by a timeout. Settings include CLI path, language and refresh interval.

Uses the official `account/rateLimits/read` app-server method; does not start model turns,
read authentication files, or parse chat logs. API-key billing is not supported.

See the [repository README](https://github.com/zerodice0/noctalia-codex-usage#readme)
for installation, troubleshooting and updates. Keep the cloned repository after installation:
the installer registers it as a local path source instead of copying the plugin files.

Independent community plugin; not affiliated with OpenAI or Noctalia. [MIT license](https://github.com/zerodice0/noctalia-codex-usage/blob/main/LICENSE).
