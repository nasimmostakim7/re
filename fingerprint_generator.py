"""
Fingerprint Generator Module
Generates realistic, randomized browser fingerprint parameters
for anti-detection purposes. Each profile gets unique, consistent fingerprints.
"""

import hashlib
import random
import struct
import json
from typing import Dict, Any, Optional, List, Tuple


# ══════════════════════════════════════════════════════════════
#  GPU / WebGL Data
# ══════════════════════════════════════════════════════════════

WEBGL_VENDORS = [
    "Google Inc.",
    "Google Inc. (NVIDIA)",
    "Google Inc. (AMD)",
    "Google Inc. (Intel)",
    "Google Inc. (Apple)",
]

WEBGL_RENDERERS = {
    "Google Inc. (NVIDIA)": [
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 4080 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3090 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (NVIDIA, NVIDIA GeForce GTX 1660 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 Ti Direct3D11 vs_5_0 ps_5_0, D3D11)",
    ],
    "Google Inc. (AMD)": [
        "ANGLE (AMD, AMD Radeon RX 7900 XTX Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (AMD, AMD Radeon RX 6900 XT Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (AMD, AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (AMD, AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    ],
    "Google Inc. (Intel)": [
        "ANGLE (Intel, Intel(R) UHD Graphics 770 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (Intel, Intel(R) UHD Graphics 730 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "ANGLE (Intel, Intel(R) HD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    ],
    "Google Inc. (Apple)": [
        "ANGLE (Apple, Apple M2 Pro, OpenGL 4.1)",
        "ANGLE (Apple, Apple M2, OpenGL 4.1)",
        "ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)",
        "ANGLE (Apple, Apple M1, OpenGL 4.1)",
    ],
    "Google Inc.": [
        "ANGLE (Unknown, Qualcomm Adreno 740, OpenGL ES 3.2)",
        "ANGLE (Unknown, Mali-G715, OpenGL ES 3.2)",
    ],
}

WEBGL_EXTENSIONS = [
    "ANGLE_instanced_arrays",
    "EXT_blend_minmax",
    "EXT_clip_control",
    "EXT_color_buffer_half_float",
    "EXT_depth_clamp",
    "EXT_disjoint_timer_query",
    "EXT_float_blend",
    "EXT_frag_depth",
    "EXT_polygon_offset_clamp",
    "EXT_shader_texture_lod",
    "EXT_texture_compression_bptc",
    "EXT_texture_compression_rgtc",
    "EXT_texture_filter_anisotropic",
    "EXT_sRGB",
    "KHR_parallel_shader_compile",
    "OES_element_index_uint",
    "OES_fbo_render_mipmap",
    "OES_standard_derivatives",
    "OES_texture_float",
    "OES_texture_float_linear",
    "OES_texture_half_float",
    "OES_texture_half_float_linear",
    "OES_vertex_array_object",
    "WEBGL_color_buffer_float",
    "WEBGL_compressed_texture_s3tc",
    "WEBGL_compressed_texture_s3tc_srgb",
    "WEBGL_debug_renderer_info",
    "WEBGL_debug_shaders",
    "WEBGL_depth_texture",
    "WEBGL_draw_buffers",
    "WEBGL_lose_context",
    "WEBGL_multi_draw",
    "WEBGL_polygon_mode",
]


# ══════════════════════════════════════════════════════════════
#  Screen Resolutions
# ══════════════════════════════════════════════════════════════

DESKTOP_RESOLUTIONS = [
    (1920, 1080), (2560, 1440), (3840, 2160), (1366, 768),
    (1536, 864), (1440, 900), (1680, 1050), (1280, 720),
    (1600, 900), (2560, 1080), (3440, 1440),
]

ANDROID_RESOLUTIONS = [
    (412, 915), (360, 800), (393, 873), (414, 896),
    (390, 844), (428, 926), (360, 780), (384, 854),
    (412, 892), (360, 640), (320, 568),
]


# ══════════════════════════════════════════════════════════════
#  User Agents
# ══════════════════════════════════════════════════════════════

CHROME_VERSIONS = [
    "120.0.6099.109", "120.0.6099.130", "121.0.6167.85",
    "121.0.6167.139", "122.0.6261.69", "122.0.6261.112",
    "123.0.6312.58", "123.0.6312.86", "124.0.6367.60",
    "124.0.6367.91", "125.0.6422.60", "125.0.6422.112",
    "126.0.6478.55", "126.0.6478.114", "127.0.6533.72",
    "128.0.6613.84", "129.0.6668.58", "130.0.6723.70",
]

WINDOWS_VERSIONS = [
    "Windows NT 10.0; Win64; x64",
    "Windows NT 10.0; WOW64",
    "Windows NT 11.0; Win64; x64",
]

ANDROID_DEVICES = [
    ("Samsung SM-S928B", "14"),
    ("Samsung SM-S926B", "14"),
    ("Samsung SM-S911B", "14"),
    ("Samsung SM-A546B", "14"),
    ("Samsung SM-A156B", "14"),
    ("Google Pixel 8 Pro", "14"),
    ("Google Pixel 8", "14"),
    ("Google Pixel 7a", "14"),
    ("OnePlus 12", "14"),
    ("Xiaomi 14", "14"),
    ("Samsung SM-G998B", "13"),
    ("Samsung SM-G991B", "13"),
]


# ══════════════════════════════════════════════════════════════
#  Audio / Canvas / Font data
# ══════════════════════════════════════════════════════════════

COMMON_FONTS = [
    "Arial", "Arial Black", "Calibri", "Cambria", "Cambria Math",
    "Comic Sans MS", "Consolas", "Courier New", "Georgia", "Impact",
    "Lucida Console", "Lucida Sans Unicode", "Microsoft Sans Serif",
    "Palatino Linotype", "Segoe UI", "Segoe UI Symbol", "Tahoma",
    "Times New Roman", "Trebuchet MS", "Verdana", "Wingdings",
]

LANGUAGES = [
    "en-US", "en-GB", "en-AU", "en-CA", "de-DE", "fr-FR",
    "es-ES", "it-IT", "pt-BR", "ja-JP", "ko-KR", "zh-CN",
    "ru-RU", "ar-SA", "hi-IN", "bn-BD", "nl-NL", "sv-SE",
    "pl-PL", "tr-TR",
]

TIMEZONES = [
    "America/New_York", "America/Chicago", "America/Denver",
    "America/Los_Angeles", "America/Toronto", "America/Sao_Paulo",
    "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Moscow",
    "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata", "Asia/Dubai",
    "Asia/Dhaka", "Asia/Singapore", "Australia/Sydney",
    "Pacific/Auckland", "Africa/Cairo", "Africa/Lagos",
]


# ══════════════════════════════════════════════════════════════
#  Core Generator Class
# ══════════════════════════════════════════════════════════════

class FingerprintGenerator:
    """Generates a complete, consistent browser fingerprint from a seed."""

    def __init__(self, seed: Optional[str] = None):
        self.seed = seed or hashlib.sha256(
            struct.pack('d', random.random())
        ).hexdigest()[:16]
        self._rng = random.Random(self.seed)

    def _pick(self, lst: list):
        return self._rng.choice(lst)

    def _pick_n(self, lst: list, n: int) -> list:
        return self._rng.sample(lst, min(n, len(lst)))

    def _rand_int(self, lo: int, hi: int) -> int:
        return self._rng.randint(lo, hi)

    def _rand_float(self, lo: float, hi: float, decimals: int = 6) -> float:
        return round(self._rng.uniform(lo, hi), decimals)

    # ── Canvas noise ──────────────────────────────────────
    def generate_canvas_noise(self) -> Dict[str, Any]:
        canvas_seed = self._rand_int(100000, 999999)
        noise_table = [
            self._rand_float(-0.03, 0.03, 8)
            for _ in range(256)
        ]
        return {
            "canvas_seed": canvas_seed,
            "noise_table": noise_table,
            "noise_intensity": self._rand_float(0.01, 0.04, 4),
            "hash_offset": self._rand_int(1, 255),
        }

    # ── WebGL fingerprint ─────────────────────────────────
    def generate_webgl(self) -> Dict[str, Any]:
        vendor = self._pick(WEBGL_VENDORS)
        renderer_list = WEBGL_RENDERERS.get(vendor, WEBGL_RENDERERS["Google Inc."])
        renderer = self._pick(renderer_list)

        num_ext = self._rand_int(20, len(WEBGL_EXTENSIONS))
        extensions = sorted(self._pick_n(WEBGL_EXTENSIONS, num_ext))

        return {
            "gpu_vendor": vendor,
            "gpu_renderer": renderer,
            "webgl_version": "WebGL 1.0 (OpenGL ES 2.0 Chromium)",
            "webgl2_version": "WebGL 2.0 (OpenGL ES 3.0 Chromium)",
            "shading_language": "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
            "extensions": extensions,
            "max_texture_size": self._pick([4096, 8192, 16384]),
            "max_viewport_dims": self._pick([[4096, 4096], [8192, 8192], [16384, 16384], [32768, 32768]]),
            "max_renderbuffer_size": self._pick([4096, 8192, 16384]),
            "max_vertex_attribs": self._pick([16, 32]),
            "max_vertex_uniform_vectors": self._pick([256, 1024, 4096]),
            "max_fragment_uniform_vectors": self._pick([256, 1024, 4096]),
            "max_varying_vectors": self._pick([15, 16, 30, 31, 32]),
            "aliased_line_width_range": [1, self._pick([1, 7.375, 8])],
            "aliased_point_size_range": [1, self._pick([255, 1024, 8192])],
            "max_anisotropy": self._pick([8, 16]),
            "precision_vertex_highp": {"rangeMin": 127, "rangeMax": 127, "precision": 23},
            "precision_fragment_highp": {"rangeMin": 127, "rangeMax": 127, "precision": 23},
            "unmasked_vendor": vendor,
            "unmasked_renderer": renderer,
        }

    # ── Audio context ─────────────────────────────────────
    def generate_audio(self) -> Dict[str, Any]:
        base_freq = self._rand_float(35.0, 35.8, 10)
        noise_level = self._rand_float(0.00001, 0.0001, 10)
        return {
            "audio_context_hash": hashlib.md5(
                f"{self.seed}_audio".encode()
            ).hexdigest(),
            "base_frequency": base_freq,
            "noise_level": noise_level,
            "channel_count": self._pick([2, 4, 6]),
            "sample_rate": self._pick([44100, 48000]),
            "state": "suspended",
            "max_channel_count": self._pick([2, 6, 8, 32]),
        }

    # ── Screen / Display ──────────────────────────────────
    def generate_screen(self, mode: str = "desktop") -> Dict[str, Any]:
        if mode == "android":
            w, h = self._pick(ANDROID_RESOLUTIONS)
            dpr = self._pick([2.0, 2.625, 3.0, 3.5])
        else:
            w, h = self._pick(DESKTOP_RESOLUTIONS)
            dpr = self._pick([1.0, 1.25, 1.5, 2.0])

        color_depth = self._pick([24, 30, 32])
        return {
            "width": w,
            "height": h,
            "avail_width": w,
            "avail_height": h - self._rand_int(0, 48),
            "color_depth": color_depth,
            "pixel_depth": color_depth,
            "device_pixel_ratio": dpr,
            "orientation_type": "landscape-primary" if mode == "desktop" else "portrait-primary",
            "orientation_angle": 0,
        }

    # ── Navigator / UA ────────────────────────────────────
    def generate_navigator(self, mode: str = "desktop") -> Dict[str, Any]:
        chrome_ver = self._pick(CHROME_VERSIONS)
        major = chrome_ver.split(".")[0]

        if mode == "android":
            device_name, android_ver = self._pick(ANDROID_DEVICES)
            ua = (
                f"Mozilla/5.0 (Linux; Android {android_ver}; {device_name}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{chrome_ver} Mobile Safari/537.36"
            )
            platform = "Linux armv81"
        else:
            win_ver = self._pick(WINDOWS_VERSIONS)
            ua = (
                f"Mozilla/5.0 ({win_ver}) "
                f"AppleWebKit/537.36 (KHTML, like Gecko) "
                f"Chrome/{chrome_ver} Safari/537.36"
            )
            platform = "Win32"

        lang = self._pick(LANGUAGES)
        langs = [lang]
        if "-" in lang:
            base = lang.split("-")[0]
            if base != lang:
                langs.append(base)

        return {
            "user_agent": ua,
            "platform": platform,
            "language": lang,
            "languages": langs,
            "hardware_concurrency": self._pick([2, 4, 6, 8, 12, 16]),
            "device_memory": self._pick([2, 4, 8, 16, 32]),
            "max_touch_points": 10 if mode == "android" else 0,
            "chrome_version": chrome_ver,
            "chrome_major": major,
            "vendor": "Google Inc.",
            "vendor_sub": "",
            "product": "Gecko",
            "product_sub": "20030107",
            "app_version": ua.replace("Mozilla/", ""),
            "do_not_track": self._pick([None, "1"]),
            "cookie_enabled": True,
            "pdf_viewer_enabled": True if mode == "desktop" else False,
            "webdriver": False,
        }

    # ── Timezone ──────────────────────────────────────────
    def generate_timezone(self) -> Dict[str, Any]:
        tz = self._pick(TIMEZONES)
        offsets = {
            "America/New_York": -300, "America/Chicago": -360,
            "America/Denver": -420, "America/Los_Angeles": -480,
            "America/Toronto": -300, "America/Sao_Paulo": -180,
            "Europe/London": 0, "Europe/Paris": 60,
            "Europe/Berlin": 60, "Europe/Moscow": 180,
            "Asia/Tokyo": 540, "Asia/Shanghai": 480,
            "Asia/Kolkata": 330, "Asia/Dubai": 240,
            "Asia/Dhaka": 360, "Asia/Singapore": 480,
            "Australia/Sydney": 600, "Pacific/Auckland": 720,
            "Africa/Cairo": 120, "Africa/Lagos": 60,
        }
        return {
            "timezone": tz,
            "timezone_offset": offsets.get(tz, 0),
        }

    # ── Fonts ─────────────────────────────────────────────
    def generate_fonts(self) -> Dict[str, Any]:
        n = self._rand_int(12, len(COMMON_FONTS))
        fonts = sorted(self._pick_n(COMMON_FONTS, n))
        return {
            "installed_fonts": fonts,
            "font_hash": hashlib.md5(
                ",".join(fonts).encode()
            ).hexdigest(),
        }

    # ── ClientRects noise ─────────────────────────────────
    def generate_client_rects(self) -> Dict[str, Any]:
        return {
            "rect_noise_x": self._rand_float(-0.001, 0.001, 8),
            "rect_noise_y": self._rand_float(-0.001, 0.001, 8),
            "rect_noise_w": self._rand_float(-0.0005, 0.0005, 8),
            "rect_noise_h": self._rand_float(-0.0005, 0.0005, 8),
        }

    # ── Full fingerprint ──────────────────────────────────
    def generate_full_fingerprint(self, mode: str = "desktop") -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "mode": mode,
            "canvas": self.generate_canvas_noise(),
            "webgl": self.generate_webgl(),
            "audio": self.generate_audio(),
            "screen": self.generate_screen(mode),
            "navigator": self.generate_navigator(mode),
            "timezone": self.generate_timezone(),
            "fonts": self.generate_fonts(),
            "client_rects": self.generate_client_rects(),
        }


def generate_fingerprint(seed: Optional[str] = None, mode: str = "desktop") -> Dict[str, Any]:
    gen = FingerprintGenerator(seed)
    return gen.generate_full_fingerprint(mode)


if __name__ == "__main__":
    fp = generate_fingerprint()
    print(json.dumps(fp, indent=2))
