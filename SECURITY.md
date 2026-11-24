# Security policy

This is a university demo that runs on your own machine. It is built to have as little attack surface as possible:

- **Loopback only.** The Streamlit server binds to `localhost` (127.0.0.1 / ::1), never to a public interface, and runs headless.
- **XSRF protection on, CORS protection on, telemetry off** (`browser.gatherUsageStats = false`). See `.streamlit/config.toml`.
- **No static file route.** `server.enableStaticServing = false`. The vendored fonts in `fonts/` are embedded into the page as base64 data URIs, so no file is served from disk.
- **Upload route capped at zero.** Streamlit always registers its internal upload endpoint, even when an app has no uploader. That endpoint still requires a live session id and an XSRF token, and `server.maxUploadSize = 0` makes it reject any upload body. This app has no file uploader.
- No secrets, no database, no login. The app makes no network requests at runtime.
- The code uses no `eval`, `exec`, `pickle`, `subprocess` or shell calls. User input is one text field, parsed by a strict validator (`drone/inputs.py`) that caps its length and the number of cells; error messages never echo the raw input.
- HTML is only built from constant strings and validated numbers. Tracebacks are never shown in the page (`client.showErrorDetails = "none"`).
- Dependencies are pinned to exact versions with hashes and installed with `pip install --require-hashes`. CI uses read-only permissions and actions pinned to commit SHAs.

## Reporting a vulnerability

Please use GitHub private vulnerability reporting: open the **Security** tab of this repository and choose **Report a vulnerability**. Do not open a public issue for security problems.

## Supported versions

Only the latest commit on `main` is supported.
