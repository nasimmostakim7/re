# XONOMO Anti-Detect Browser — Nuitka EXE রূপান্তর সম্পূর্ণ গাইডলাইন

## সূচিপত্র

1. [প্রয়োজনীয়তা](#১-প্রয়োজনীয়তা)
2. [Nuitka ইনস্টলেশন](#২-nuitka-ইনস্টলেশন)
3. [C কম্পাইলার সেটআপ](#৩-c-কম্পাইলার-সেটআপ)
4. [বেসিক EXE বিল্ড](#৪-বেসিক-exe-বিল্ড)
5. [অপ্টিমাইজড বিল্ড](#৫-অপ্টিমাইজড-বিল্ড)
6. [Standalone Distribution](#৬-standalone-distribution)
7. [OneFile EXE](#৭-onefile-exe)
8. [আইকন ও মেটাডেটা](#৮-আইকন-ও-মেটাডেটা)
9. [ট্রাবলশুটিং](#৯-ট্রাবলশুটিং)
10. [সম্পূর্ণ কমান্ড](#১০-সম্পূর্ণ-কমান্ড)

---

## ১. প্রয়োজনীয়তা

### সিস্টেম রিকোয়ারমেন্ট

| বিষয় | মিনিমাম | রেকমেন্ডেড |
|-------|---------|-------------|
| OS | Windows 10 | Windows 10/11 64-bit |
| RAM | 4 GB | 8 GB+ |
| Disk Space | 2 GB free | 5 GB+ free |
| Python | 3.8+ | 3.11 বা 3.12 |

### প্রয়োজনীয় সফটওয়্যার

```
Python 3.11+ (python.org থেকে ডাউনলোড)
pip (Python এর সাথে আসে)
Nuitka
C Compiler (MinGW-w64 বা Visual Studio)
```

---

## ২. Nuitka ইনস্টলেশন

### Step 1: pip দিয়ে Nuitka ইনস্টল

```bash
pip install nuitka
```

### Step 2: ভার্সন চেক

```bash
python -m nuitka --version
```

### Step 3: প্রজেক্ট ডিপেন্ডেন্সি ইনস্টল

```bash
pip install -r requirements.txt
```

---

## ৩. C কম্পাইলার সেটআপ

### অপশন A: MinGW-w64 (সহজ — রেকমেন্ডেড)

Nuitka নিজেই MinGW ডাউনলোড করতে পারে:

```bash
python -m nuitka --mingw64 main.py
```

প্রথমবার রান করলে Nuitka স্বয়ংক্রিয়ভাবে MinGW-w64 ডাউনলোড ও সেটআপ করবে।

### অপশন B: Visual Studio (বড় প্রজেক্টের জন্য)

1. [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) ডাউনলোড করুন
2. ইনস্টলারে **"Desktop development with C++"** সিলেক্ট করুন
3. ইনস্টল করুন (প্রায় 6-8 GB)

### অপশন C: ম্যানুয়াল MinGW ইনস্টল

```bash
# winget দিয়ে (Windows 11):
winget install -e --id MinGW-w64.MinGW-w64

# অথবা chocolatey দিয়ে:
choco install mingw
```

---

## ৪. বেসিক EXE বিল্ড

### সবচেয়ে সহজ কমান্ড

```bash
python -m nuitka main.py
```

এটি `main.exe` তৈরি করবে একই ফোল্ডারে।

### টেস্ট রান

```bash
main.exe
```

---

## ৫. অপ্টিমাইজড বিল্ড

### ফাস্ট বিল্ড (ডেভেলপমেন্ট)

```bash
python -m nuitka ^
    --mingw64 ^
    --follow-imports ^
    --enable-plugin=pyqt5 ^
    main.py
```

### অপ্টিমাইজড বিল্ড (প্রোডাকশন)

```bash
python -m nuitka ^
    --mingw64 ^
    --follow-imports ^
    --enable-plugin=pyqt5 ^
    --lto=yes ^
    --jobs=4 ^
    main.py
```

### ফ্ল্যাগ ব্যাখ্যা

| ফ্ল্যাগ | কাজ |
|---------|-----|
| `--mingw64` | MinGW-w64 কম্পাইলার ব্যবহার |
| `--follow-imports` | সকল ইম্পোর্ট করা মডিউল কম্পাইল করে |
| `--enable-plugin=pyqt5` | PyQt5 সাপোর্ট |
| `--lto=yes` | Link Time Optimization (ছোট ও দ্রুত EXE) |
| `--jobs=4` | ৪টি CPU কোর দিয়ে বিল্ড (দ্রুত) |

---

## ৬. Standalone Distribution

### Standalone বিল্ড (সম্পূর্ণ প্যাকেজ)

এই কমান্ডটি একটি ফোল্ডার তৈরি করবে যেখানে Python ছাড়াই EXE রান করা যাবে:

```bash
python -m nuitka ^
    --mingw64 ^
    --standalone ^
    --follow-imports ^
    --enable-plugin=pyqt5 ^
    --include-data-dir=.=. ^
    --output-dir=build ^
    main.py
```

### আউটপুট ফোল্ডার স্ট্রাকচার

```
build/
└── main.dist/
    ├── main.exe          ← মূল EXE ফাইল
    ├── python311.dll     ← Python DLL
    ├── PyQt5/            ← PyQt5 লাইব্রেরি
    ├── *.dll             ← প্রয়োজনীয় DLL ফাইল
    └── ...
```

### ডিস্ট্রিবিউশন

`main.dist` ফোল্ডারটি ZIP করে যেকোনো Windows কম্পিউটারে পাঠাতে পারবেন। Python ইনস্টল থাকার দরকার নেই।

---

## ৭. OneFile EXE

### একটি মাত্র EXE ফাইল তৈরি

```bash
python -m nuitka ^
    --mingw64 ^
    --onefile ^
    --follow-imports ^
    --enable-plugin=pyqt5 ^
    --output-dir=build ^
    main.py
```

### OneFile vs Standalone

| বিষয় | OneFile | Standalone |
|-------|---------|------------|
| আউটপুট | একটি EXE | ফোল্ডার + EXE |
| সাইজ | ছোট (60-100 MB) | বড় (150-300 MB) |
| স্টার্টআপ | ধীর (extract করে) | দ্রুত |
| ডিস্ট্রিবিউশন | সহজ | ZIP করতে হয় |

> **রেকমেন্ডেশন:** ডিস্ট্রিবিউশনের জন্য `--onefile` ব্যবহার করুন।

---

## ৮. আইকন ও মেটাডেটা

### কাস্টম আইকন যোগ করা

আপনার একটি `.ico` ফাইল দরকার। PNG থেকে ICO করতে: [ConvertICO.com](https://convertico.com/)

```bash
python -m nuitka ^
    --mingw64 ^
    --onefile ^
    --follow-imports ^
    --enable-plugin=pyqt5 ^
    --windows-icon-from-ico=icon.ico ^
    --output-dir=build ^
    main.py
```

### সম্পূর্ণ মেটাডেটা সহ

```bash
python -m nuitka ^
    --mingw64 ^
    --onefile ^
    --follow-imports ^
    --enable-plugin=pyqt5 ^
    --windows-icon-from-ico=icon.ico ^
    --windows-company-name="XONOMO" ^
    --windows-product-name="XONOMO Anti-Detect Browser" ^
    --windows-file-version=1.0.0.0 ^
    --windows-product-version=1.0.0.0 ^
    --windows-file-description="Premium Anti-Detect Browser" ^
    --output-dir=build ^
    main.py
```

### UAC Admin Rights (যদি দরকার)

```bash
    --windows-uac-admin ^
```

### Console Window লুকানো

```bash
    --windows-console-mode=disable ^
```

---

## ৯. ট্রাবলশুটিং

### সমস্যা ১: "ModuleNotFoundError"

```bash
# নির্দিষ্ট মডিউল include করুন:
--include-module=websocket
--include-module=sqlite3

# অথবা সব প্যাকেজ:
--include-package=websocket
```

### সমস্যা ২: PyQt5 plugin না পাওয়া

```bash
# PyQt5 plugins ম্যানুয়ালি include:
--include-qt-plugins=all
```

### সমস্যা ৩: বিল্ড অনেক সময় নিচ্ছে

```bash
# CPU কোর বাড়ান:
--jobs=8

# Cache ব্যবহার করুন:
--cache-mode=force
```

### সমস্যা ৪: EXE অনেক বড়

```bash
# অপ্রয়োজনীয় মডিউল বাদ দিন:
--nofollow-import-to=unittest
--nofollow-import-to=test
--nofollow-import-to=tkinter

# LTO চালু করুন:
--lto=yes
```

### সমস্যা ৫: Antivirus False Positive

Nuitka দিয়ে তৈরি EXE কিছু antivirus detect করতে পারে। সমাধান:

```bash
# Code signing certificate ব্যবহার করুন (প্রোডাকশনে):
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com main.exe

# অথবা antivirus-এ exception যোগ করুন
```

### সমস্যা ৬: DLL না পাওয়া

```bash
# নির্দিষ্ট DLL include:
--include-data-files=path/to/file.dll=file.dll
```

---

## ১০. সম্পূর্ণ কমান্ড

### সম্পূর্ণ প্রোডাকশন বিল্ড কমান্ড (কপি-পেস্ট করুন):

```bash
python -m nuitka ^
    --mingw64 ^
    --onefile ^
    --follow-imports ^
    --enable-plugin=pyqt5 ^
    --include-module=websocket ^
    --include-module=sqlite3 ^
    --include-module=json ^
    --include-module=hashlib ^
    --include-qt-plugins=all ^
    --lto=yes ^
    --jobs=4 ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=icon.ico ^
    --windows-company-name="XONOMO" ^
    --windows-product-name="XONOMO Anti-Detect Browser" ^
    --windows-file-version=1.0.0.0 ^
    --windows-product-version=1.0.0.0 ^
    --windows-file-description="Premium Anti-Detect Browser" ^
    --nofollow-import-to=unittest ^
    --nofollow-import-to=test ^
    --nofollow-import-to=tkinter ^
    --nofollow-import-to=setuptools ^
    --output-dir=build ^
    main.py
```

### Linux/Mac-এ বিল্ড করতে (^ এর বদলে \ ব্যবহার করুন):

```bash
python -m nuitka \
    --follow-imports \
    --enable-plugin=pyqt5 \
    --standalone \
    --include-module=websocket \
    --include-module=sqlite3 \
    --lto=yes \
    --jobs=4 \
    --output-dir=build \
    main.py
```

---

## বিল্ড অটোমেশন স্ক্রিপ্ট

### `build.bat` (Windows)

নিচের কোডটি `build.bat` ফাইলে সেভ করুন:

```batch
@echo off
echo ============================================
echo   XONOMO Anti-Detect Browser — Build Script
echo ============================================
echo.

REM Check Python
python --version 2>nul || (
    echo ERROR: Python not found!
    echo Download from https://python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install nuitka

REM Build
echo.
echo Building EXE... This may take 5-15 minutes.
echo.

python -m nuitka ^
    --mingw64 ^
    --onefile ^
    --follow-imports ^
    --enable-plugin=pyqt5 ^
    --include-module=websocket ^
    --include-module=sqlite3 ^
    --lto=yes ^
    --jobs=4 ^
    --windows-console-mode=disable ^
    --windows-company-name="XONOMO" ^
    --windows-product-name="XONOMO Anti-Detect Browser" ^
    --windows-file-version=1.0.0.0 ^
    --windows-product-version=1.0.0.0 ^
    --nofollow-import-to=unittest ^
    --nofollow-import-to=test ^
    --nofollow-import-to=tkinter ^
    --output-dir=build ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo   BUILD SUCCESSFUL!
    echo   EXE Location: build\main.exe
    echo ============================================
) else (
    echo.
    echo BUILD FAILED! Check errors above.
)
pause
```

### ব্যবহার:

```
1. Command Prompt খুলুন
2. প্রজেক্ট ফোল্ডারে যান: cd path\to\project
3. build.bat রান করুন
4. 5-15 মিনিট অপেক্ষা করুন
5. build\main.exe ফাইলটি পাবেন
```

---

## গুরুত্বপূর্ণ নোট

1. **প্রথম বিল্ড ধীর হবে** — Nuitka C কোড জেনারেট ও কম্পাইল করে। পরবর্তী বিল্ডগুলো দ্রুত হবে (cache ব্যবহার করে)।

2. **EXE সাইজ** — PyQt5 সহ EXE সাধারণত 60-100 MB হয়। এটি স্বাভাবিক।

3. **Windows Defender** — প্রথমবার EXE রান করলে Windows SmartScreen সতর্কতা দেখাতে পারে। "Run anyway" ক্লিক করুন অথবা code signing certificate ব্যবহার করুন।

4. **Python ভার্সন** — Python 3.11 বা 3.12 দিয়ে বিল্ড করলে সবচেয়ে ভালো পারফরমেন্স পাবেন।

5. **64-bit বিল্ড** — 64-bit Python ইনস্টল করুন 64-bit EXE পেতে।
