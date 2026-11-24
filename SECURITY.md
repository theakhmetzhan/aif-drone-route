# Security policy

This is a university demo that runs on your own machine. It is built to have as little attack surface as possible:

- The Streamlit server binds to `localhost` only (`.streamlit/config.toml`), runs headless, and has usage statistics turned off.
- XSRF protection and CORS protection stay on. There is no file uploader, no secrets, no database and no login.
- The app makes no network requests at runtime. Fonts are vendored in `static/fonts/` and served locally.
- The code uses no `eval`, `exec`, `pickle`, `subprocess` or shell calls. User input is one text field, parsed by a strict validator (`drone/inputs.py`) that caps its length and the number of cells; error messages never echo the raw input.
- HTML is only built from constant strings and validated numbers.
- Dependencies are pinned to exact versions with hashes and installed with `pip install --require-hashes`. CI uses read-only permissions and actions pinned to commit SHAs.

## Reporting a vulnerability

Please use GitHub private vulnerability reporting: open the **Security** tab of this repository and choose **Report a vulnerability**. Do not open a public issue for security problems.

## Supported versions

Only the latest commit on `main` is supported.
