# XONOMO Anti-Detect Browser

Premium anti-detect browser with advanced fingerprint spoofing, CDP injection, and multi-profile management.

## Features

- **CDP Injection** — Injects fingerprint parameters via Chrome DevTools Protocol on browser launch
- **WebGL Masking** — Proxied WebGL parameters (vendor, renderer, extensions) per profile
- **Canvas Noise** — Unique canvas fingerprint per profile via noise table injection
- **Binary Patching** — Removes `cdc_`, `webdriver` and automation strings from chromedriver/chrome
- **JS Runtime Protection** — `toString()` spoofing so websites can't detect overridden functions
- **Navigator/Screen/Audio/Timezone Spoofing** — Full browser fingerprint control
- **Profile Management** — Create, search, run, delete profiles with SQLite storage
- **Android Screen Mode** — Mobile emulation with proper mouse scroll support
- **Full Screen Mode** — Desktop full-screen browser launch
- **License System** — Admin approval, expiry date, and hardware-locked licensing
- **Search Profiles** — Search by profile name or number

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Building EXE

See [NUITKA_GUIDE.md](NUITKA_GUIDE.md) for complete Nuitka EXE conversion instructions.

## Project Structure

```
├── main.py                  # Entry point
├── gui_app.py               # PyQt5 GUI application
├── browser_core.py          # CDP injection, binary patching, JS protection
├── fingerprint_generator.py # Fingerprint parameter generation
├── profile_manager.py       # Profile CRUD with SQLite
├── license_manager.py       # License validation & enforcement
├── requirements.txt         # Python dependencies
├── NUITKA_GUIDE.md         # EXE build guide (Bengali)
└── README.md               # This file
```

## License

Proprietary — XONOMO
