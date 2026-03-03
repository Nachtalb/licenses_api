# Software License Browser

A simple static site for browsing and exploring open source software licenses.

License data sourced from [choosealicense.com](https://github.com/github/choosealicense.com).

## Live

[l.naa.gg](https://l.naa.gg)

## Usage

### Fetch license data

```bash
python3 scripts/fetch_licenses.py
```

This downloads all license files from GitHub and generates `data/licenses.json`.

### Serve locally

```bash
./serve.sh
# or
python3 -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000).

## Features

- Dark/light theme (follows system preference)
- Search/filter licenses
- Permissions, conditions, and limitations at a glance
- Copy license text to clipboard
- Fully responsive
- Zero dependencies — vanilla HTML/CSS/JS

## License

[LGPL-3.0](https://www.gnu.org/licenses/lgpl-3.0.en.html)
