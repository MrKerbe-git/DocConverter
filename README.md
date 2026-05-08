# DocConverter — 문서 → PDF 변환기 / Document → PDF Converter

[![Build Installers](https://github.com/MrKerbe-git/DocConverter/actions/workflows/build.yml/badge.svg)](https://github.com/MrKerbe-git/DocConverter/actions/workflows/build.yml)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-green)

[한국어](#한국어) | [English](#english)

---

<a id="한국어"></a>
## 한국어

HWP, DOCX, XLSX, PPTX 등의 문서를 **PDF로 일괄 변환**하는 크로스플랫폼 데스크탑 앱입니다.  
하위 폴더 구조를 그대로 유지한 채 변환 결과를 저장합니다.

### 주요 기능

- **재귀 폴더 스캔** — 하위 폴더 내 파일까지 자동 탐색 및 트리 표시
- **폴더 구조 보존** — 원본 경로 구조를 출력 경로에 그대로 재현
- **중복 파일 처리** — 이미 존재하는 PDF에 대해 덮어쓰기 / 건너뛰기 선택
- **완료 후 폴더 자동 열기** — 변환 완료 시 탐색기(Finder) 자동 실행
- **변환 요약** — 성공 / 실패 / 건너뜀 건수 표시
- **한/영 UI 전환** — 버튼 한 번으로 언어 전환
- **다크모드 UI**

### 지원 포맷

| 포맷 | 확장자 |
|------|--------|
| 한글 | `.hwp` `.hwpx` |
| Word | `.docx` `.doc` |
| Excel | `.xlsx` `.xls` |
| PowerPoint | `.pptx` `.ppt` |
| LibreOffice | `.odt` `.ods` `.odp` |

### 폴더 구조 보존 예시

```
소스: C:/문서/프로젝트/보고서.hwp
            ↓
출력: C:/PDF변환/프로젝트/보고서.pdf
```

### 다운로드

[**Actions 탭**](../../actions/workflows/build.yml) → 최근 빌드 클릭 → 하단 **Artifacts** 에서 다운로드

| 파일 | 플랫폼 |
|------|--------|
| `DocConverter-Windows.zip` → `DocConverter.exe` | Windows 10/11 |
| `DocConverter-macOS.zip` → `DocConverter.app` | macOS 12+ |

> **macOS 최초 실행 시:** Apple 미서명 앱 경고가 뜰 수 있습니다.  
> 시스템 설정 → 개인 정보 보호 및 보안 → **"확인 없이 열기"** 를 클릭해주세요.

### 요구사항

앱 실행 전 **LibreOffice** 설치가 필요합니다.

- Windows / macOS: [libreoffice.org](https://www.libreoffice.org/download/libreoffice-fresh/)

### 직접 실행 (개발자용)

```bash
pip install PyQt6
python main.py
```

---

<a id="english"></a>
## English

A cross-platform desktop app that **batch-converts documents to PDF** while preserving the original folder structure.  
Supports HWP, DOCX, XLSX, PPTX, and more.

### Features

- **Recursive folder scan** — Detects files in all subfolders and displays them as a tree
- **Folder structure preservation** — Recreates the source folder structure under the output path
- **Duplicate file handling** — Choose to overwrite or skip existing PDFs before conversion
- **Auto-open output folder** — Opens Explorer/Finder automatically on completion
- **Conversion summary** — Shows success / failed / skipped counts
- **Korean / English UI toggle** — Switch language with one click
- **Dark mode UI**

### Supported Formats

| Format | Extensions |
|--------|------------|
| Hangul (HWP) | `.hwp` `.hwpx` |
| Word | `.docx` `.doc` |
| Excel | `.xlsx` `.xls` |
| PowerPoint | `.pptx` `.ppt` |
| LibreOffice | `.odt` `.ods` `.odp` |

### Folder Structure Example

```
Source: C:/Docs/Project/Report.hwp
              ↓
Output: C:/PDF/Project/Report.pdf
```

### Download

[**Actions tab**](../../actions/workflows/build.yml) → Click the latest build → Download from **Artifacts** at the bottom

| File | Platform |
|------|----------|
| `DocConverter-Windows.zip` → `DocConverter.exe` | Windows 10/11 |
| `DocConverter-macOS.zip` → `DocConverter.app` | macOS 12+ |

> **First launch on macOS:** You may see an "unidentified developer" warning.  
> Go to System Settings → Privacy & Security → click **"Open Anyway"**.

### Requirements

**LibreOffice** must be installed before running the app. (Used as the PDF conversion engine)

- Windows / macOS: [libreoffice.org](https://www.libreoffice.org/download/libreoffice-fresh/)

### Run from Source (Developers)

```bash
pip install PyQt6
python main.py
```

---

## Tech Stack

- **GUI** — PyQt6
- **Conversion Engine** — LibreOffice (headless mode)
- **Build** — PyInstaller + GitHub Actions
