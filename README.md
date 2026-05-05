# XONOMO Anti-Detect Browser v8

Premium anti-detect browser with advanced fingerprint spoofing, Firebase licensing, and multi-profile management.

## Features

- **undetected_chromedriver** — Automated Chrome with anti-detection built-in
- **selenium_stealth** — Additional stealth patches on top of UC
- **CDP Injection** — Full fingerprint override via Chrome DevTools Protocol
- **WebGL Masking** — Proxied WebGL parameters (vendor, renderer, extensions) per profile
- **Canvas Noise** — 100% unique canvas fingerprint per profile via noise table
- **Binary Patching** — Removes `cdc_`, `$wdc_` automation strings from chromedriver
- **JS Runtime Protection** — `toString()` spoofing with WeakMap/WeakSet
- **Dynamic Battery Masking** — Realistic live battery drain/charge simulation
- **WebRTC Masking/Locking** — Mask or fully disable WebRTC per profile
- **Navigator/Screen/Audio/Timezone Spoofing** — Full browser fingerprint control
- **Cookie Collection** — All Cookie / Site Cookie export (Netscape .txt or .json)
- **Profile Management** — Create, search, rename, launch, delete profiles
- **Android Screen Mode** — Mobile emulation with touch event simulation
- **Full Screen Mode** — Desktop full-screen browser with mobile fingerprint
- **Firebase License System** — Admin approval, expiry, hardware-lock, cross-device login
- **Admin Broadcast Messages** — Real-time message popup from admin panel
- **Proxy Auth Extension** — Built-in Chrome extension for authenticated proxies
- **Portable Chromium Support** — Use bundled Chromium instead of system Chrome

## Installation

```bash
pip install -r requirements.txt
```

## Usage (Single File)

```bash
python xonomo_antidetect.py
```

## Building EXE

See [NUITKA_GUIDE.md](NUITKA_GUIDE.md) for complete Nuitka EXE conversion instructions.

## Project Structure

```
├── xonomo_antidetect.py     # Complete application (single file)
├── requirements.txt         # Python dependencies
├── NUITKA_GUIDE.md         # EXE build guide (Bengali)
└── README.md               # This file
```

## Dependencies

- `PyQt6` — GUI framework
- `undetected-chromedriver` — Anti-detection Chrome driver
- `selenium-stealth` — Additional stealth patches
- `fake-useragent` — Random user agent generation
- `requests` — HTTP requests for proxy validation & IP lookup
- `firebase-admin` — Firebase Firestore for license management

## License

Proprietary — XONOMO
