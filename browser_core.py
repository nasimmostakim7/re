"""
Browser Core Module
Handles browser launching with CDP injection, binary patching,
and JS runtime protection for anti-detection.
"""

import os
import re
import sys
import json
import shutil
import struct
import subprocess
import tempfile
import time
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List

from fingerprint_generator import FingerprintGenerator


# ══════════════════════════════════════════════════════════════
#  Binary Patcher — removes cdc_ / webdriver markers
# ══════════════════════════════════════════════════════════════

class BinaryPatcher:
    """
    Patches chromedriver / chrome binary to remove automation
    detection strings like 'cdc_', '$cdc_', 'webdriver'.
    """

    PATCH_PATTERNS = [
        (b"cdc_", b"xxx_"),
        (b"$cdc_", b"$xxx_"),
        (b"webdriver", b"xxxxxxver"),
        (b"$wdc_", b"$xxx_"),
        (b"is_controlled_by_automation", b"is_xontrolled_by_xutomation"),
        (b"navigator.webdriver", b"navigator.xxxxxxxxxx"),
        (b"WEBDRIVER", b"XXXXXXXXX"),
        (b"enable-automation", b"xxxxxx-xxxxxxxxxxx"),
        (b"AutomationExtension", b"XxtomxtionExtxnsion"),
    ]

    @staticmethod
    def find_chromedriver() -> Optional[str]:
        """Locate chromedriver binary in common paths."""
        search_paths = []

        if platform.system() == "Windows":
            search_paths = [
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "chromedriver"),
                os.path.join(os.environ.get("PROGRAMFILES", ""), "chromedriver"),
                os.path.join(os.environ.get("USERPROFILE", ""), ".wdm"),
            ]
            exe_name = "chromedriver.exe"
        else:
            search_paths = [
                "/usr/local/bin",
                "/usr/bin",
                os.path.expanduser("~/.wdm"),
            ]
            exe_name = "chromedriver"

        for sp in search_paths:
            if not os.path.exists(sp):
                continue
            for root, dirs, files in os.walk(sp):
                if exe_name in files:
                    return os.path.join(root, exe_name)

        result = shutil.which("chromedriver")
        return result

    @staticmethod
    def find_chrome_binary() -> Optional[str]:
        """Locate Chrome browser binary."""
        if platform.system() == "Windows":
            candidates = [
                os.path.join(os.environ.get("PROGRAMFILES", ""),
                             "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(os.environ.get("PROGRAMFILES(X86)", ""),
                             "Google", "Chrome", "Application", "chrome.exe"),
                os.path.join(os.environ.get("LOCALAPPDATA", ""),
                             "Google", "Chrome", "Application", "chrome.exe"),
            ]
        elif platform.system() == "Darwin":
            candidates = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            ]
        else:
            candidates = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
            ]

        for c in candidates:
            if os.path.isfile(c):
                return c

        return shutil.which("google-chrome") or shutil.which("chromium")

    @classmethod
    def patch_binary(cls, binary_path: str) -> Dict[str, Any]:
        """
        Patch a binary file to remove detection strings.
        Creates a backup before patching.
        Returns patch results.
        """
        if not os.path.isfile(binary_path):
            return {"success": False, "error": f"File not found: {binary_path}"}

        backup_path = binary_path + ".backup"
        if not os.path.exists(backup_path):
            shutil.copy2(binary_path, backup_path)

        with open(binary_path, "rb") as f:
            data = f.read()

        original_size = len(data)
        patches_applied = []

        for old_bytes, new_bytes in cls.PATCH_PATTERNS:
            count = data.count(old_bytes)
            if count > 0:
                data = data.replace(old_bytes, new_bytes)
                patches_applied.append({
                    "pattern": old_bytes.decode("utf-8", errors="replace"),
                    "replacement": new_bytes.decode("utf-8", errors="replace"),
                    "occurrences": count,
                })

        if patches_applied:
            with open(binary_path, "wb") as f:
                f.write(data)

        return {
            "success": True,
            "binary_path": binary_path,
            "backup_path": backup_path,
            "original_size": original_size,
            "patched_size": len(data),
            "patches_applied": patches_applied,
            "total_patches": sum(p["occurrences"] for p in patches_applied),
        }

    @classmethod
    def patch_all(cls) -> Dict[str, Any]:
        """Patch both chromedriver and chrome binary."""
        results = {}
        cd = cls.find_chromedriver()
        if cd:
            results["chromedriver"] = cls.patch_binary(cd)
        else:
            results["chromedriver"] = {"success": False, "error": "Not found"}

        chrome = cls.find_chrome_binary()
        if chrome:
            results["chrome"] = cls.patch_binary(chrome)
        else:
            results["chrome"] = {"success": False, "error": "Not found"}

        return results


# ══════════════════════════════════════════════════════════════
#  JS Runtime Protection Scripts
# ══════════════════════════════════════════════════════════════

class JSProtection:
    """
    Generates JavaScript injection scripts to protect
    against fingerprint detection and toString() checks.
    """

    @staticmethod
    def get_webdriver_mask_script() -> str:
        """Remove all webdriver-related properties."""
        return """
        // ═══ Webdriver mask ═══
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });
        delete navigator.__proto__.webdriver;

        // Remove webdriver from navigator prototype chain
        const navProto = Object.getPrototypeOf(navigator);
        if (navProto) {
            delete navProto.webdriver;
            Object.defineProperty(navProto, 'webdriver', {
                get: () => undefined,
                configurable: true
            });
        }

        // Remove automation-related window properties
        const propsToDelete = [
            'cdc_adoQpoasnfa76pfcZLmcfl_Array',
            'cdc_adoQpoasnfa76pfcZLmcfl_Promise',
            'cdc_adoQpoasnfa76pfcZLmcfl_Symbol',
            'cdc_adoQpoasnfa76pfcZLmcfl_JSON',
            'cdc_adoQpoasnfa76pfcZLmcfl_Proxy',
            'cdc_adoQpoasnfa76pfcZLmcfl_Object',
        ];
        for (const prop of propsToDelete) {
            try { delete window[prop]; } catch(e) {}
        }

        // Remove any property starting with $ or containing cdc
        for (const key of Object.keys(window)) {
            if (key.match(/^\\$?cdc_/i) || key.match(/^\\$wdc_/i)) {
                try { delete window[key]; } catch(e) {}
            }
        }
        """

    @staticmethod
    def get_tostring_protection_script() -> str:
        """
        Protect overridden functions from toString() detection.
        Websites check: someFunc.toString() to see if it returns
        'function someFunc() { [native code] }' — if not, they know
        it's been tampered with. This script spoofs toString().
        """
        return """
        // ═══ toString() Protection ═══
        const _nativeToString = Function.prototype.toString;
        const _nativeToStringStr = 'function toString() { [native code] }';

        // Map of spoofed functions -> their expected native signatures
        const _spoofedFunctions = new WeakMap();

        // Helper to register a spoofed function
        window.__registerSpoofedFunction = function(fn, nativeName) {
            _spoofedFunctions.set(fn, `function ${nativeName}() { [native code] }`);
        };

        // Override Function.prototype.toString
        const _newToString = function() {
            if (_spoofedFunctions.has(this)) {
                return _spoofedFunctions.get(this);
            }
            return _nativeToString.call(this);
        };

        // Make toString itself appear native
        _spoofedFunctions.set(_newToString, _nativeToStringStr);
        Function.prototype.toString = _newToString;

        // Protect Object.defineProperty from detection
        const _origDefProp = Object.defineProperty;
        _spoofedFunctions.set(_origDefProp, 'function defineProperty() { [native code] }');

        // Protect getter detection
        const _origGetOwnPropDesc = Object.getOwnPropertyDescriptor;
        _spoofedFunctions.set(_origGetOwnPropDesc, 'function getOwnPropertyDescriptor() { [native code] }');
        """

    @staticmethod
    def get_canvas_noise_script(canvas_params: Dict[str, Any]) -> str:
        """Inject canvas noise to create unique fingerprint."""
        seed = canvas_params.get("canvas_seed", 12345)
        noise_table = json.dumps(canvas_params.get("noise_table", []))
        intensity = canvas_params.get("noise_intensity", 0.02)
        return f"""
        // ═══ Canvas Fingerprint Noise ═══
        (function() {{
            const SEED = {seed};
            const NOISE_TABLE = {noise_table};
            const INTENSITY = {intensity};

            // Seeded PRNG
            function mulberry32(a) {{
                return function() {{
                    a |= 0; a = a + 0x6D2B79F5 | 0;
                    var t = Math.imul(a ^ a >>> 15, 1 | a);
                    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
                    return ((t ^ t >>> 14) >>> 0) / 4294967296;
                }};
            }}

            const rng = mulberry32(SEED);

            // Override toDataURL
            const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function(type, quality) {{
                const ctx = this.getContext('2d');
                if (ctx) {{
                    const imageData = ctx.getImageData(0, 0, this.width, this.height);
                    const data = imageData.data;
                    for (let i = 0; i < data.length; i += 4) {{
                        const idx = (i / 4) % NOISE_TABLE.length;
                        const noise = NOISE_TABLE[idx] * INTENSITY * 255;
                        data[i]     = Math.max(0, Math.min(255, data[i] + noise));
                        data[i + 1] = Math.max(0, Math.min(255, data[i+1] + noise * 0.7));
                        data[i + 2] = Math.max(0, Math.min(255, data[i+2] + noise * 0.3));
                    }}
                    ctx.putImageData(imageData, 0, 0);
                }}
                const result = origToDataURL.call(this, type, quality);
                window.__registerSpoofedFunction && window.__registerSpoofedFunction(
                    HTMLCanvasElement.prototype.toDataURL, 'toDataURL'
                );
                return result;
            }};

            // Override toBlob
            const origToBlob = HTMLCanvasElement.prototype.toBlob;
            HTMLCanvasElement.prototype.toBlob = function(callback, type, quality) {{
                const ctx = this.getContext('2d');
                if (ctx) {{
                    const imageData = ctx.getImageData(0, 0, this.width, this.height);
                    const data = imageData.data;
                    for (let i = 0; i < data.length; i += 4) {{
                        const idx = (i / 4) % NOISE_TABLE.length;
                        const noise = NOISE_TABLE[idx] * INTENSITY * 255;
                        data[i] = Math.max(0, Math.min(255, data[i] + noise));
                    }}
                    ctx.putImageData(imageData, 0, 0);
                }}
                return origToBlob.call(this, callback, type, quality);
            }};

            // Register as native
            if (window.__registerSpoofedFunction) {{
                window.__registerSpoofedFunction(HTMLCanvasElement.prototype.toDataURL, 'toDataURL');
                window.__registerSpoofedFunction(HTMLCanvasElement.prototype.toBlob, 'toBlob');
            }}
        }})();
        """

    @staticmethod
    def get_webgl_spoof_script(webgl_params: Dict[str, Any]) -> str:
        """Spoof WebGL parameters through proxy."""
        vendor = webgl_params.get("gpu_vendor", "Google Inc.")
        renderer = webgl_params.get("gpu_renderer", "ANGLE (Intel, Intel HD Graphics)")
        extensions = json.dumps(webgl_params.get("extensions", []))
        max_texture = webgl_params.get("max_texture_size", 16384)
        max_viewport = json.dumps(webgl_params.get("max_viewport_dims", [16384, 16384]))
        max_rb = webgl_params.get("max_renderbuffer_size", 16384)
        max_va = webgl_params.get("max_vertex_attribs", 16)
        max_vuv = webgl_params.get("max_vertex_uniform_vectors", 4096)
        max_fuv = webgl_params.get("max_fragment_uniform_vectors", 1024)
        max_vv = webgl_params.get("max_varying_vectors", 30)

        return f"""
        // ═══ WebGL Fingerprint Spoof via Proxy ═══
        (function() {{
            const SPOOF_VENDOR = "{vendor}";
            const SPOOF_RENDERER = "{renderer}";
            const SPOOF_EXTENSIONS = {extensions};
            const MAX_TEXTURE_SIZE = {max_texture};
            const MAX_VIEWPORT_DIMS = {max_viewport};
            const MAX_RENDERBUFFER_SIZE = {max_rb};
            const MAX_VERTEX_ATTRIBS = {max_va};
            const MAX_VERTEX_UNIFORM_VECTORS = {max_vuv};
            const MAX_FRAGMENT_UNIFORM_VECTORS = {max_fuv};
            const MAX_VARYING_VECTORS = {max_vv};

            const paramOverrides = {{
                // WEBGL_debug_renderer_info
                0x9245: SPOOF_VENDOR,    // UNMASKED_VENDOR_WEBGL
                0x9246: SPOOF_RENDERER,  // UNMASKED_RENDERER_WEBGL
                // Standard params
                0x1F01: SPOOF_RENDERER,  // GL_RENDERER
                0x1F00: SPOOF_VENDOR,    // GL_VENDOR
                0x0D33: MAX_TEXTURE_SIZE,
                0x0D3A: MAX_VIEWPORT_DIMS,
                0x84E8: MAX_RENDERBUFFER_SIZE,
                0x8869: MAX_VERTEX_ATTRIBS,
                0x8DFB: MAX_VERTEX_UNIFORM_VECTORS,
                0x8DFD: MAX_FRAGMENT_UNIFORM_VECTORS,
                0x8DFC: MAX_VARYING_VECTORS,
            }};

            function patchContext(proto, contextName) {{
                // Patch getParameter
                const origGetParam = proto.getParameter;
                proto.getParameter = function(pname) {{
                    if (pname in paramOverrides) {{
                        return paramOverrides[pname];
                    }}
                    return origGetParam.call(this, pname);
                }};

                // Patch getExtension
                const origGetExt = proto.getExtension;
                proto.getExtension = function(name) {{
                    const ext = origGetExt.call(this, name);
                    if (name === 'WEBGL_debug_renderer_info' && ext) {{
                        return ext;
                    }}
                    return ext;
                }};

                // Patch getSupportedExtensions
                const origGetSupExt = proto.getSupportedExtensions;
                proto.getSupportedExtensions = function() {{
                    return SPOOF_EXTENSIONS;
                }};

                // Patch getShaderPrecisionFormat
                const origGetSPF = proto.getShaderPrecisionFormat;
                proto.getShaderPrecisionFormat = function(shaderType, precisionType) {{
                    const result = origGetSPF.call(this, shaderType, precisionType);
                    return result;
                }};

                // Register all as native
                if (window.__registerSpoofedFunction) {{
                    window.__registerSpoofedFunction(proto.getParameter, 'getParameter');
                    window.__registerSpoofedFunction(proto.getExtension, 'getExtension');
                    window.__registerSpoofedFunction(proto.getSupportedExtensions, 'getSupportedExtensions');
                    window.__registerSpoofedFunction(proto.getShaderPrecisionFormat, 'getShaderPrecisionFormat');
                }}
            }}

            if (typeof WebGLRenderingContext !== 'undefined') {{
                patchContext(WebGLRenderingContext.prototype, 'WebGL1');
            }}
            if (typeof WebGL2RenderingContext !== 'undefined') {{
                patchContext(WebGL2RenderingContext.prototype, 'WebGL2');
            }}
        }})();
        """

    @staticmethod
    def get_navigator_spoof_script(nav_params: Dict[str, Any]) -> str:
        """Spoof navigator properties."""
        ua = nav_params.get("user_agent", "")
        plat = nav_params.get("platform", "Win32")
        lang = nav_params.get("language", "en-US")
        langs = json.dumps(nav_params.get("languages", ["en-US"]))
        hw_conc = nav_params.get("hardware_concurrency", 8)
        dev_mem = nav_params.get("device_memory", 8)
        max_tp = nav_params.get("max_touch_points", 0)

        return f"""
        // ═══ Navigator Spoof ═══
        (function() {{
            const spoofProps = {{
                userAgent: "{ua}",
                platform: "{plat}",
                language: "{lang}",
                languages: Object.freeze({langs}),
                hardwareConcurrency: {hw_conc},
                deviceMemory: {dev_mem},
                maxTouchPoints: {max_tp},
                vendor: "Google Inc.",
                webdriver: false,
                cookieEnabled: true,
                pdfViewerEnabled: {'true' if nav_params.get('pdf_viewer_enabled', True) else 'false'},
                appVersion: "{nav_params.get('app_version', '')}",
            }};

            for (const [key, value] of Object.entries(spoofProps)) {{
                try {{
                    Object.defineProperty(navigator, key, {{
                        get: () => value,
                        configurable: true,
                        enumerable: true
                    }});
                    // Also override on prototype
                    const proto = Object.getPrototypeOf(navigator);
                    if (proto) {{
                        Object.defineProperty(proto, key, {{
                            get: () => value,
                            configurable: true,
                            enumerable: true
                        }});
                    }}
                }} catch(e) {{}}
            }}

            // Protect navigator property getters with toString spoofing
            if (window.__registerSpoofedFunction) {{
                for (const key of Object.keys(spoofProps)) {{
                    try {{
                        const desc = Object.getOwnPropertyDescriptor(navigator, key);
                        if (desc && desc.get) {{
                            window.__registerSpoofedFunction(desc.get, 'get ' + key);
                        }}
                    }} catch(e) {{}}
                }}
            }}
        }})();
        """

    @staticmethod
    def get_screen_spoof_script(screen_params: Dict[str, Any]) -> str:
        """Spoof screen properties."""
        w = screen_params.get("width", 1920)
        h = screen_params.get("height", 1080)
        aw = screen_params.get("avail_width", 1920)
        ah = screen_params.get("avail_height", 1040)
        cd = screen_params.get("color_depth", 24)
        pd = screen_params.get("pixel_depth", 24)
        dpr = screen_params.get("device_pixel_ratio", 1.0)

        return f"""
        // ═══ Screen Spoof ═══
        (function() {{
            const screenOverrides = {{
                width: {w}, height: {h},
                availWidth: {aw}, availHeight: {ah},
                colorDepth: {cd}, pixelDepth: {pd}
            }};
            for (const [key, value] of Object.entries(screenOverrides)) {{
                try {{
                    Object.defineProperty(screen, key, {{
                        get: () => value,
                        configurable: true
                    }});
                }} catch(e) {{}}
            }}

            Object.defineProperty(window, 'devicePixelRatio', {{
                get: () => {dpr},
                configurable: true
            }});

            Object.defineProperty(window, 'innerWidth', {{
                get: () => {aw},
                configurable: true
            }});
            Object.defineProperty(window, 'innerHeight', {{
                get: () => {ah},
                configurable: true
            }});
            Object.defineProperty(window, 'outerWidth', {{
                get: () => {w},
                configurable: true
            }});
            Object.defineProperty(window, 'outerHeight', {{
                get: () => {h},
                configurable: true
            }});
        }})();
        """

    @staticmethod
    def get_audio_spoof_script(audio_params: Dict[str, Any]) -> str:
        """Spoof AudioContext fingerprint."""
        noise = audio_params.get("noise_level", 0.00005)
        return f"""
        // ═══ AudioContext Spoof ═══
        (function() {{
            const NOISE = {noise};
            const origCreateOscillator = AudioContext.prototype.createOscillator;
            const origCreateAnalyser = AudioContext.prototype.createAnalyser;
            const origGetFloatFrequencyData = AnalyserNode.prototype.getFloatFrequencyData;
            const origGetByteFrequencyData = AnalyserNode.prototype.getByteFrequencyData;

            AnalyserNode.prototype.getFloatFrequencyData = function(array) {{
                origGetFloatFrequencyData.call(this, array);
                for (let i = 0; i < array.length; i++) {{
                    array[i] += (Math.random() - 0.5) * NOISE * 100;
                }}
            }};

            AnalyserNode.prototype.getByteFrequencyData = function(array) {{
                origGetByteFrequencyData.call(this, array);
                for (let i = 0; i < array.length; i++) {{
                    array[i] = Math.max(0, Math.min(255,
                        array[i] + Math.floor((Math.random() - 0.5) * NOISE * 1000)
                    ));
                }}
            }};

            if (window.__registerSpoofedFunction) {{
                window.__registerSpoofedFunction(
                    AnalyserNode.prototype.getFloatFrequencyData, 'getFloatFrequencyData'
                );
                window.__registerSpoofedFunction(
                    AnalyserNode.prototype.getByteFrequencyData, 'getByteFrequencyData'
                );
            }}
        }})();
        """

    @staticmethod
    def get_client_rects_spoof_script(rect_params: Dict[str, Any]) -> str:
        """Spoof ClientRects for fingerprint noise."""
        nx = rect_params.get("rect_noise_x", 0.0001)
        ny = rect_params.get("rect_noise_y", 0.0001)
        nw = rect_params.get("rect_noise_w", 0.00005)
        nh = rect_params.get("rect_noise_h", 0.00005)
        return f"""
        // ═══ ClientRects Noise ═══
        (function() {{
            const NX = {nx}, NY = {ny}, NW = {nw}, NH = {nh};

            const origGetBCR = Element.prototype.getBoundingClientRect;
            Element.prototype.getBoundingClientRect = function() {{
                const rect = origGetBCR.call(this);
                const obj = {{
                    x:      rect.x + NX,
                    y:      rect.y + NY,
                    width:  rect.width + NW,
                    height: rect.height + NH,
                    top:    rect.top + NY,
                    right:  rect.right + NX + NW,
                    bottom: rect.bottom + NY + NH,
                    left:   rect.left + NX,
                }};
                Object.setPrototypeOf(obj, DOMRect.prototype);
                return obj;
            }};

            if (window.__registerSpoofedFunction) {{
                window.__registerSpoofedFunction(
                    Element.prototype.getBoundingClientRect, 'getBoundingClientRect'
                );
            }}
        }})();
        """

    @staticmethod
    def get_timezone_spoof_script(tz_params: Dict[str, Any]) -> str:
        """Spoof timezone."""
        tz = tz_params.get("timezone", "America/New_York")
        offset = tz_params.get("timezone_offset", -300)
        return f"""
        // ═══ Timezone Spoof ═══
        (function() {{
            const TARGET_TZ = "{tz}";
            const TARGET_OFFSET = {offset};

            // Override Date.getTimezoneOffset
            const origGetTZOffset = Date.prototype.getTimezoneOffset;
            Date.prototype.getTimezoneOffset = function() {{
                return TARGET_OFFSET;
            }};

            // Override Intl.DateTimeFormat
            const origDTF = Intl.DateTimeFormat;
            const origResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
            Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
                const opts = origResolvedOptions.call(this);
                opts.timeZone = TARGET_TZ;
                return opts;
            }};

            if (window.__registerSpoofedFunction) {{
                window.__registerSpoofedFunction(
                    Date.prototype.getTimezoneOffset, 'getTimezoneOffset'
                );
                window.__registerSpoofedFunction(
                    Intl.DateTimeFormat.prototype.resolvedOptions, 'resolvedOptions'
                );
            }}
        }})();
        """

    @staticmethod
    def get_permissions_spoof_script() -> str:
        """Spoof Permissions API to look normal."""
        return """
        // ═══ Permissions Spoof ═══
        (function() {
            const origQuery = navigator.permissions.query;
            navigator.permissions.query = function(desc) {
                if (desc.name === 'notifications') {
                    return Promise.resolve({state: 'prompt', onchange: null});
                }
                return origQuery.call(this, desc);
            };

            if (window.__registerSpoofedFunction) {
                window.__registerSpoofedFunction(
                    navigator.permissions.query, 'query'
                );
            }
        })();
        """

    @staticmethod
    def get_plugins_spoof_script() -> str:
        """Spoof navigator.plugins to look like a real browser."""
        return """
        // ═══ Plugins Spoof ═══
        (function() {
            const pluginData = [
                {name: 'PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                {name: 'Chrome PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                {name: 'Chromium PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                {name: 'Microsoft Edge PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
                {name: 'WebKit built-in PDF', filename: 'internal-pdf-viewer', description: 'Portable Document Format'},
            ];

            const mockPlugins = {
                length: pluginData.length,
                item: function(i) { return pluginData[i] || null; },
                namedItem: function(name) {
                    return pluginData.find(p => p.name === name) || null;
                },
                refresh: function() {}
            };

            for (let i = 0; i < pluginData.length; i++) {
                mockPlugins[i] = pluginData[i];
            }

            Object.defineProperty(navigator, 'plugins', {
                get: () => mockPlugins,
                configurable: true
            });

            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => ({
                    length: 2,
                    item: function(i) { return [{type: 'application/pdf'}, {type: 'text/pdf'}][i]; },
                    namedItem: function(name) { return {type: name}; }
                }),
                configurable: true
            });
        })();
        """

    @staticmethod
    def get_iframe_contentwindow_spoof() -> str:
        """Prevent iframe contentWindow checks from detecting automation."""
        return """
        // ═══ iframe contentWindow Spoof ═══
        (function() {
            const origContentWindow = Object.getOwnPropertyDescriptor(
                HTMLIFrameElement.prototype, 'contentWindow'
            );
            Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                get: function() {
                    const win = origContentWindow.get.call(this);
                    if (win) {
                        try {
                            Object.defineProperty(win, 'chrome', {
                                get: () => window.chrome,
                                configurable: true
                            });
                        } catch(e) {}
                    }
                    return win;
                },
                configurable: true
            });
        })();
        """

    @staticmethod
    def get_chrome_runtime_script() -> str:
        """Add chrome.runtime to look like a real Chrome browser."""
        return """
        // ═══ Chrome Runtime Spoof ═══
        (function() {
            if (!window.chrome) {
                window.chrome = {};
            }
            if (!window.chrome.runtime) {
                window.chrome.runtime = {
                    connect: function() { return {}; },
                    sendMessage: function() {},
                    onMessage: { addListener: function() {}, removeListener: function() {} },
                    id: undefined,
                    getManifest: function() { return {}; },
                    getURL: function(path) { return ''; },
                    PlatformOs: { MAC: 'mac', WIN: 'win', ANDROID: 'android', CROS: 'cros', LINUX: 'linux' },
                    PlatformArch: { ARM: 'arm', X86_32: 'x86-32', X86_64: 'x86-64' },
                };
            }
            if (!window.chrome.loadTimes) {
                window.chrome.loadTimes = function() {
                    return {
                        commitLoadTime: Date.now() / 1000,
                        connectionInfo: 'h2',
                        finishDocumentLoadTime: Date.now() / 1000 + 0.1,
                        finishLoadTime: Date.now() / 1000 + 0.2,
                        firstPaintAfterLoadTime: 0,
                        firstPaintTime: Date.now() / 1000 + 0.05,
                        navigationType: 'Other',
                        npnNegotiatedProtocol: 'h2',
                        requestTime: Date.now() / 1000 - 0.3,
                        startLoadTime: Date.now() / 1000 - 0.2,
                        wasAlternateProtocolAvailable: false,
                        wasFetchedViaSpdy: true,
                        wasNpnNegotiated: true,
                    };
                };
            }
            if (!window.chrome.csi) {
                window.chrome.csi = function() {
                    return {
                        onloadT: Date.now(),
                        pageT: 500 + Math.random() * 1000,
                        startE: Date.now() - 500,
                        tran: 15
                    };
                };
            }
        })();
        """

    @classmethod
    def build_full_injection_script(cls, fingerprint: Dict[str, Any]) -> str:
        """Build complete injection script from fingerprint data."""
        scripts = [
            cls.get_tostring_protection_script(),
            cls.get_webdriver_mask_script(),
            cls.get_chrome_runtime_script(),
            cls.get_plugins_spoof_script(),
            cls.get_permissions_spoof_script(),
            cls.get_navigator_spoof_script(fingerprint.get("navigator", {})),
            cls.get_screen_spoof_script(fingerprint.get("screen", {})),
            cls.get_canvas_noise_script(fingerprint.get("canvas", {})),
            cls.get_webgl_spoof_script(fingerprint.get("webgl", {})),
            cls.get_audio_spoof_script(fingerprint.get("audio", {})),
            cls.get_client_rects_spoof_script(fingerprint.get("client_rects", {})),
            cls.get_timezone_spoof_script(fingerprint.get("timezone", {})),
            cls.get_iframe_contentwindow_spoof(),
        ]
        return "\n".join(scripts)


# ══════════════════════════════════════════════════════════════
#  Browser Launcher with CDP
# ══════════════════════════════════════════════════════════════

class BrowserLauncher:
    """
    Launches Chrome with CDP commands to inject fingerprint parameters.
    """

    def __init__(self, profile_dir: str, fingerprint: Dict[str, Any],
                 proxy: Optional[str] = None):
        self.profile_dir = profile_dir
        self.fingerprint = fingerprint
        self.proxy = proxy
        self.process = None
        self.debug_port = None

    def _find_free_port(self) -> int:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]

    def _get_chrome_args(self, debug_port: int) -> List[str]:
        """Build Chrome launch arguments."""
        nav = self.fingerprint.get("navigator", {})
        screen = self.fingerprint.get("screen", {})
        tz = self.fingerprint.get("timezone", {})
        mode = self.fingerprint.get("mode", "desktop")

        args = [
            f"--remote-debugging-port={debug_port}",
            f"--user-data-dir={self.profile_dir}",
            f"--user-agent={nav.get('user_agent', '')}",
            f"--lang={nav.get('language', 'en-US')}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-infobars",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-dev-shm-usage",
            f"--window-size={screen.get('width', 1920)},{screen.get('height', 1080)}",
        ]

        if tz.get("timezone"):
            args.append(f"--timezone={tz['timezone']}")

        if self.proxy:
            args.append(f"--proxy-server={self.proxy}")

        if mode == "android":
            w = screen.get("width", 412)
            h = screen.get("height", 915)
            args.append(f"--window-size={w},{h}")

        args.append("--excludeSwitches=enable-automation")
        args.append("--useAutomationExtension=false")

        return args

    def launch(self) -> Dict[str, Any]:
        """Launch the browser and inject fingerprint via CDP."""
        chrome_path = BinaryPatcher.find_chrome_binary()
        if not chrome_path:
            return {"success": False, "error": "Chrome binary not found"}

        self.debug_port = self._find_free_port()
        args = [chrome_path] + self._get_chrome_args(self.debug_port)

        os.makedirs(self.profile_dir, exist_ok=True)

        env = os.environ.copy()
        tz_data = self.fingerprint.get("timezone", {})
        if tz_data.get("timezone"):
            env["TZ"] = tz_data["timezone"]

        try:
            self.process = subprocess.Popen(
                args,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            return {"success": False, "error": str(e)}

        time.sleep(2)

        injection_result = self._inject_via_cdp()

        return {
            "success": True,
            "pid": self.process.pid,
            "debug_port": self.debug_port,
            "profile_dir": self.profile_dir,
            "injection": injection_result,
        }

    def _inject_via_cdp(self) -> Dict[str, Any]:
        """Inject fingerprint scripts via Chrome DevTools Protocol."""
        try:
            import websocket
            import urllib.request

            url = f"http://127.0.0.1:{self.debug_port}/json"
            max_retries = 5
            ws_url = None

            for attempt in range(max_retries):
                try:
                    resp = urllib.request.urlopen(url, timeout=3)
                    targets = json.loads(resp.read().decode())
                    for t in targets:
                        if t.get("type") == "page":
                            ws_url = t.get("webSocketDebuggerUrl")
                            break
                    if ws_url:
                        break
                except Exception:
                    time.sleep(1)

            if not ws_url:
                return {"success": False, "error": "Could not connect to CDP"}

            ws = websocket.create_connection(ws_url, timeout=10)

            injection_script = JSProtection.build_full_injection_script(self.fingerprint)

            # Page.addScriptToEvaluateOnNewDocument
            cmd = {
                "id": 1,
                "method": "Page.addScriptToEvaluateOnNewDocument",
                "params": {"source": injection_script}
            }
            ws.send(json.dumps(cmd))
            result1 = json.loads(ws.recv())

            # Also execute immediately on current page
            cmd2 = {
                "id": 2,
                "method": "Runtime.evaluate",
                "params": {"expression": injection_script}
            }
            ws.send(json.dumps(cmd2))
            result2 = json.loads(ws.recv())

            # Set device metrics for mobile emulation if android mode
            if self.fingerprint.get("mode") == "android":
                screen = self.fingerprint.get("screen", {})
                nav = self.fingerprint.get("navigator", {})
                cmd3 = {
                    "id": 3,
                    "method": "Emulation.setDeviceMetricsOverride",
                    "params": {
                        "width": screen.get("width", 412),
                        "height": screen.get("height", 915),
                        "deviceScaleFactor": screen.get("device_pixel_ratio", 3.0),
                        "mobile": True,
                        "screenWidth": screen.get("width", 412),
                        "screenHeight": screen.get("height", 915),
                    }
                }
                ws.send(json.dumps(cmd3))
                json.loads(ws.recv())

                # Enable touch emulation
                cmd4 = {
                    "id": 4,
                    "method": "Emulation.setTouchEmulationEnabled",
                    "params": {
                        "enabled": True,
                        "maxTouchPoints": nav.get("max_touch_points", 10)
                    }
                }
                ws.send(json.dumps(cmd4))
                json.loads(ws.recv())

                # Set user agent override
                cmd5 = {
                    "id": 5,
                    "method": "Emulation.setUserAgentOverride",
                    "params": {
                        "userAgent": nav.get("user_agent", ""),
                        "platform": nav.get("platform", "Linux armv81"),
                    }
                }
                ws.send(json.dumps(cmd5))
                json.loads(ws.recv())

            # Set timezone override
            tz_data = self.fingerprint.get("timezone", {})
            if tz_data.get("timezone"):
                cmd_tz = {
                    "id": 6,
                    "method": "Emulation.setTimezoneOverride",
                    "params": {"timezoneId": tz_data["timezone"]}
                }
                ws.send(json.dumps(cmd_tz))
                json.loads(ws.recv())

            # Set locale override
            nav_data = self.fingerprint.get("navigator", {})
            if nav_data.get("language"):
                cmd_locale = {
                    "id": 7,
                    "method": "Emulation.setLocaleOverride",
                    "params": {"locale": nav_data["language"]}
                }
                ws.send(json.dumps(cmd_locale))
                try:
                    json.loads(ws.recv())
                except Exception:
                    pass

            ws.close()

            return {
                "success": True,
                "scripts_injected": True,
                "cdp_responses": [result1, result2],
            }

        except ImportError:
            return {
                "success": False,
                "error": "websocket-client not installed. Run: pip install websocket-client"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop(self):
        """Stop the browser process."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except Exception:
                self.process.kill()
            self.process = None

    def is_running(self) -> bool:
        """Check if browser process is still running."""
        if self.process:
            return self.process.poll() is None
        return False
