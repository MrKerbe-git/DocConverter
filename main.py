import sys
import os
import shutil
import subprocess
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QTreeWidget,
    QTreeWidgetItem, QProgressBar, QTextEdit, QSplitter,
    QMessageBox, QCheckBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

# ── 설정 ─────────────────────────────────────────────────────────────────────

LIBREOFFICE_CANDIDATES = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]

SUPPORTED_EXT = {
    ".hwp", ".hwpx",
    ".docx", ".doc",
    ".xlsx", ".xls",
    ".pptx", ".ppt",
    ".odt", ".ods", ".odp",
}

# ── 다국어 문자열 ─────────────────────────────────────────────────────────────

LANG = {
    "ko": {
        "title":        "문서 → PDF 변환기",
        "src":          "소스 폴더",
        "out":          "출력 경로",
        "browse":       "찾아보기",
        "scan":         "스캔",
        "select_all":   "전체 선택",
        "deselect_all": "전체 해제",
        "convert":      "변환 시작",
        "stop":         "중지",
        "found":        "파일 {}개 발견",
        "no_src":       "소스 폴더를 선택해주세요.",
        "no_out":       "출력 경로를 입력해주세요.",
        "no_files":     "선택된 파일이 없습니다.",
        "converting":   "변환 중",
        "done":         "모든 변환이 완료되었습니다.",
        "stopped":      "변환이 중지되었습니다.",
        "files_hdr":    "파일 목록",
        "log_hdr":      "변환 로그",
        "toggle":       "English",
        "no_lo":        "LibreOffice를 찾을 수 없습니다.\n설치 상태를 확인해주세요.",
        "src_ph":       "예: C:/Documents/폴더",
        "out_ph":       "예: C:/Data_Convert",
        "open_folder":  "완료 후 출력 폴더 열기",
        "dup_title":    "중복 파일 발견",
        "dup_msg":      "PDF 파일 {count}개가 이미 존재합니다.\n처리 방법을 선택하세요:",
        "overwrite_all":"전체 덮어쓰기",
        "skip_existing":"기존 건너뛰기",
        "cancel":       "취소",
        "summary":      "완료  |  성공: {s}   실패: {f}   건너뜀: {k}",
        "dup_detail":   "중복 파일 목록",
    },
    "en": {
        "title":        "Document → PDF Converter",
        "src":          "Source Folder",
        "out":          "Output Path",
        "browse":       "Browse",
        "scan":         "Scan",
        "select_all":   "Select All",
        "deselect_all": "Deselect All",
        "convert":      "Convert",
        "stop":         "Stop",
        "found":        "{} files found",
        "no_src":       "Please select a source folder.",
        "no_out":       "Please enter an output path.",
        "no_files":     "No files selected.",
        "converting":   "Converting",
        "done":         "All conversions completed.",
        "stopped":      "Conversion stopped.",
        "files_hdr":    "File List",
        "log_hdr":      "Conversion Log",
        "toggle":       "한국어",
        "no_lo":        "LibreOffice not found.\nPlease verify your installation.",
        "src_ph":       "e.g. C:/Documents/folder",
        "out_ph":       "e.g. C:/Data_Convert",
        "open_folder":  "Open output folder on completion",
        "dup_title":    "Duplicate Files Found",
        "dup_msg":      "{count} PDF file(s) already exist.\nChoose how to handle them:",
        "overwrite_all":"Overwrite All",
        "skip_existing":"Skip Existing",
        "cancel":       "Cancel",
        "summary":      "Done  |  Success: {s}   Failed: {f}   Skipped: {k}",
        "dup_detail":   "Duplicate file list",
    },
}

# ── 다크모드 ──────────────────────────────────────────────────────────────────

DARK_QSS = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
}
QLabel { color: #d4d4d4; }

QLineEdit {
    background-color: #2d2d2d;
    border: 1px solid #4a4a4a;
    border-radius: 4px;
    padding: 4px 8px;
    color: #d4d4d4;
}
QLineEdit:focus { border: 1px solid #0078d4; }
QLineEdit::placeholder { color: #666; }

QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #5a5a5a;
    border-radius: 4px;
    padding: 4px 10px;
    color: #d4d4d4;
}
QPushButton:hover  { background-color: #505050; border-color: #888; }
QPushButton:pressed { background-color: #0078d4; border-color: #0078d4; color: #fff; }
QPushButton:disabled { background-color: #2a2a2a; color: #555; border-color: #3a3a3a; }
QPushButton#convertBtn {
    background-color: #0078d4;
    border-color: #0078d4;
    color: #ffffff;
    font-weight: bold;
}
QPushButton#convertBtn:hover  { background-color: #1a8fe3; }
QPushButton#convertBtn:pressed { background-color: #005fa3; }
QPushButton#stopBtn {
    background-color: #c0392b;
    border-color: #c0392b;
    color: #ffffff;
    font-weight: bold;
}
QPushButton#stopBtn:hover  { background-color: #e74c3c; }

QTreeWidget {
    background-color: #252526;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    color: #d4d4d4;
    alternate-background-color: #2a2a2a;
    outline: none;
}
QTreeWidget::item { padding: 2px 4px; }
QTreeWidget::item:hover    { background-color: #2a2d2e; }
QTreeWidget::item:selected { background-color: #094771; color: #fff; }

QTextEdit {
    background-color: #1a1a1a;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    color: #d4d4d4;
}

QProgressBar {
    background-color: #2d2d2d;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    text-align: center;
    color: #d4d4d4;
    height: 18px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                stop:0 #005fa3, stop:1 #0078d4);
    border-radius: 3px;
}

QCheckBox { color: #d4d4d4; spacing: 6px; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid #5a5a5a;
    border-radius: 3px;
    background: #2d2d2d;
}
QCheckBox::indicator:checked {
    background-color: #0078d4;
    border-color: #0078d4;
    image: none;
}
QCheckBox::indicator:hover { border-color: #888; }

QSplitter::handle { background-color: #3a3a3a; }

QScrollBar:vertical {
    background: #252526; width: 10px; border-radius: 5px; margin: 0;
}
QScrollBar::handle:vertical {
    background: #4a4a4a; border-radius: 5px; min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #686868; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QMessageBox { background-color: #252526; color: #d4d4d4; }
QMessageBox QLabel { color: #d4d4d4; }
"""

def apply_dark_palette(app: QApplication):
    p = QPalette()
    c = {
        "dark":    QColor(30,  30,  30),
        "mid":     QColor(45,  45,  45),
        "light":   QColor(60,  60,  60),
        "text":    QColor(212, 212, 212),
        "dim":     QColor(100, 100, 100),
        "accent":  QColor(0,   120, 212),
        "white":   QColor(255, 255, 255),
    }
    p.setColor(QPalette.ColorRole.Window,          c["dark"])
    p.setColor(QPalette.ColorRole.WindowText,      c["text"])
    p.setColor(QPalette.ColorRole.Base,            c["mid"])
    p.setColor(QPalette.ColorRole.AlternateBase,   c["dark"])
    p.setColor(QPalette.ColorRole.ToolTipBase,     c["light"])
    p.setColor(QPalette.ColorRole.ToolTipText,     c["text"])
    p.setColor(QPalette.ColorRole.Text,            c["text"])
    p.setColor(QPalette.ColorRole.Button,          c["light"])
    p.setColor(QPalette.ColorRole.ButtonText,      c["text"])
    p.setColor(QPalette.ColorRole.Highlight,       c["accent"])
    p.setColor(QPalette.ColorRole.HighlightedText, c["white"])
    p.setColor(QPalette.ColorRole.Link,            c["accent"])
    p.setColor(QPalette.ColorRole.PlaceholderText, c["dim"])
    # Disabled state
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, c["dim"])
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text,       c["dim"])
    p.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, c["dim"])
    app.setPalette(p)

# ── 유틸 ─────────────────────────────────────────────────────────────────────

def find_libreoffice() -> str | None:
    for path in LIBREOFFICE_CANDIDATES:
        if os.path.isfile(path):
            return path
    return shutil.which("soffice")

def open_folder(path: str):
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.run(["open", path])
    else:
        subprocess.run(["xdg-open", path])

# ── 변환 워커 스레드 ──────────────────────────────────────────────────────────

class ConversionWorker(QThread):
    # sig_log: (message, status)  status = "ok" | "err" | "skip"
    sig_progress = pyqtSignal(int, int, str)
    sig_log      = pyqtSignal(str, str)
    sig_done     = pyqtSignal(int, int, int)   # success, fail, skip

    def __init__(self, files: list, source_base: str, output_base: str,
                 lo_path: str, overwrite_mode: str = "overwrite"):
        super().__init__()
        self.files          = files
        self.source_base    = Path(source_base)
        self.output_base    = Path(output_base)
        self.lo_path        = lo_path
        self.overwrite_mode = overwrite_mode   # "overwrite" | "skip"
        self._stop          = False

    def stop(self):
        self._stop = True

    def run(self):
        total   = len(self.files)
        success = fail = skip = 0

        for i, fp_str in enumerate(self.files):
            if self._stop:
                break
            fp = Path(fp_str)
            self.sig_progress.emit(i + 1, total, fp.name)
            try:
                rel      = fp.relative_to(self.source_base)
                out_dir  = self.output_base / rel.parent
                out_file = out_dir / (fp.stem + ".pdf")

                if self.overwrite_mode == "skip" and out_file.exists():
                    self.sig_log.emit(f"⏭  {rel}", "skip")
                    skip += 1
                    continue

                out_dir.mkdir(parents=True, exist_ok=True)
                result = subprocess.run(
                    [self.lo_path, "--headless", "--convert-to", "pdf",
                     "--outdir", str(out_dir), str(fp)],
                    capture_output=True, text=True,
                    timeout=120, encoding="utf-8", errors="replace",
                )

                if out_file.exists():
                    self.sig_log.emit(f"✓  {rel}", "ok")
                    success += 1
                else:
                    err = (result.stderr or result.stdout).strip()
                    self.sig_log.emit(f"✗  {rel}\n   {err}", "err")
                    fail += 1

            except subprocess.TimeoutExpired:
                self.sig_log.emit(f"✗  {fp.name}  (timeout)", "err")
                fail += 1
            except Exception as exc:
                self.sig_log.emit(f"✗  {fp.name}  {exc}", "err")
                fail += 1

        self.sig_done.emit(success, fail, skip)

# ── 메인 윈도우 ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang        = "ko"
        self.worker      = None
        self.source_base = ""
        self.file_items  = []   # list[(QTreeWidgetItem, file_path_str)]
        self._build_ui()
        self._retranslate()

    def t(self, key: str) -> str:
        return LANG[self.lang][key]

    # ── UI 구성 ───────────────────────────────────────────────────────────────

    def _build_ui(self):
        self.setMinimumSize(980, 700)
        root = QWidget()
        self.setCentralWidget(root)
        vbox = QVBoxLayout(root)
        vbox.setSpacing(8)
        vbox.setContentsMargins(14, 10, 14, 10)

        # 상단: 제목 + 언어 버튼
        top_row = QHBoxLayout()
        title_lbl = QLabel()
        title_lbl.setObjectName("appTitle")
        f = QFont()
        f.setPointSize(11)
        f.setBold(True)
        title_lbl.setFont(f)
        self._title_lbl = title_lbl
        top_row.addWidget(title_lbl)
        top_row.addStretch()
        self.lang_btn = QPushButton()
        self.lang_btn.setFixedWidth(78)
        self.lang_btn.clicked.connect(self._toggle_lang)
        top_row.addWidget(self.lang_btn)
        vbox.addLayout(top_row)

        # 소스 폴더 행
        src_row = QHBoxLayout()
        self.src_lbl = QLabel()
        self.src_lbl.setFixedWidth(74)
        self.src_edit = QLineEdit()
        self.src_browse_btn = QPushButton()
        self.src_browse_btn.setFixedWidth(80)
        self.src_browse_btn.clicked.connect(self._browse_src)
        self.scan_btn = QPushButton()
        self.scan_btn.setFixedWidth(70)
        self.scan_btn.clicked.connect(self._scan)
        src_row.addWidget(self.src_lbl)
        src_row.addWidget(self.src_edit)
        src_row.addWidget(self.src_browse_btn)
        src_row.addWidget(self.scan_btn)
        vbox.addLayout(src_row)

        # 출력 경로 행
        out_row = QHBoxLayout()
        self.out_lbl = QLabel()
        self.out_lbl.setFixedWidth(74)
        self.out_edit = QLineEdit()
        self.out_browse_btn = QPushButton()
        self.out_browse_btn.setFixedWidth(80)
        self.out_browse_btn.clicked.connect(self._browse_out)
        out_row.addWidget(self.out_lbl)
        out_row.addWidget(self.out_edit)
        out_row.addWidget(self.out_browse_btn)
        vbox.addLayout(out_row)

        # 스플리터: 파일 트리 | 변환 로그
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 4, 5, 0)
        ll.setSpacing(4)
        self.tree_hdr = self._bold_label()
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setAlternatingRowColors(True)
        ll.addWidget(self.tree_hdr)
        ll.addWidget(self.tree)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(5, 4, 0, 0)
        rl.setSpacing(4)
        self.log_hdr = self._bold_label()
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setFont(QFont("Consolas", 9))
        rl.addWidget(self.log_hdr)
        rl.addWidget(self.log_box)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([480, 480])
        vbox.addWidget(splitter)

        # 하단 컨트롤 행
        bot = QHBoxLayout()
        self.sel_all_btn = QPushButton()
        self.sel_all_btn.setFixedWidth(90)
        self.sel_all_btn.clicked.connect(self._select_all)
        self.desel_btn = QPushButton()
        self.desel_btn.setFixedWidth(90)
        self.desel_btn.clicked.connect(self._deselect_all)
        self.open_folder_chk = QCheckBox()
        self.open_folder_chk.setChecked(True)
        bot.addWidget(self.sel_all_btn)
        bot.addWidget(self.desel_btn)
        bot.addSpacing(12)
        bot.addWidget(self.open_folder_chk)
        bot.addStretch()
        self.convert_btn = QPushButton()
        self.convert_btn.setObjectName("convertBtn")
        self.convert_btn.setFixedSize(120, 34)
        self.convert_btn.clicked.connect(self._start_or_stop)
        bot.addWidget(self.convert_btn)
        vbox.addLayout(bot)

        # 상태 + 진행바
        self.status_lbl = QLabel(" ")
        self.status_lbl.setStyleSheet("color: #888;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        vbox.addWidget(self.status_lbl)
        vbox.addWidget(self.progress_bar)

    def _bold_label(self, text: str = "") -> QLabel:
        lbl = QLabel(text)
        f = lbl.font()
        f.setBold(True)
        lbl.setFont(f)
        return lbl

    # ── 번역 적용 ─────────────────────────────────────────────────────────────

    def _retranslate(self):
        self._title_lbl.setText(self.t("title"))
        self.setWindowTitle(self.t("title"))
        self.lang_btn.setText(self.t("toggle"))
        self.src_lbl.setText(self.t("src"))
        self.out_lbl.setText(self.t("out"))
        self.src_browse_btn.setText(self.t("browse"))
        self.out_browse_btn.setText(self.t("browse"))
        self.scan_btn.setText(self.t("scan"))
        self.tree_hdr.setText(self.t("files_hdr"))
        self.log_hdr.setText(self.t("log_hdr"))
        self.sel_all_btn.setText(self.t("select_all"))
        self.desel_btn.setText(self.t("deselect_all"))
        self.open_folder_chk.setText(self.t("open_folder"))
        self.src_edit.setPlaceholderText(self.t("src_ph"))
        self.out_edit.setPlaceholderText(self.t("out_ph"))
        self._sync_convert_btn()

    def _sync_convert_btn(self):
        running = bool(self.worker and self.worker.isRunning())
        if running:
            self.convert_btn.setObjectName("stopBtn")
            self.convert_btn.setText(self.t("stop"))
        else:
            self.convert_btn.setObjectName("convertBtn")
            self.convert_btn.setText(self.t("convert"))
        # Re-apply QSS so objectName change takes effect
        self.convert_btn.setStyle(self.convert_btn.style())

    # ── 액션 ──────────────────────────────────────────────────────────────────

    def _toggle_lang(self):
        self.lang = "en" if self.lang == "ko" else "ko"
        self._retranslate()

    def _browse_src(self):
        path = QFileDialog.getExistingDirectory(self, self.t("src"))
        if path:
            self.src_edit.setText(path)
            self._scan()

    def _browse_out(self):
        path = QFileDialog.getExistingDirectory(self, self.t("out"))
        if path:
            self.out_edit.setText(path)

    def _scan(self):
        src = self.src_edit.text().strip()
        if not src or not os.path.isdir(src):
            QMessageBox.warning(self, self.t("title"), self.t("no_src"))
            return

        self.source_base = src
        self.tree.clear()
        self.file_items.clear()

        src_path  = Path(src)
        all_files = sorted(
            p for p in src_path.rglob("*")
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXT
        )

        self.tree_hdr.setText(
            f"{self.t('files_hdr')}  ({self.t('found').format(len(all_files))})"
        )
        if not all_files:
            return

        dir_nodes: dict[str, QTreeWidgetItem] = {}
        for fp in all_files:
            rel    = fp.relative_to(src_path)
            parent = self.tree.invisibleRootItem()
            cum    = Path()
            for part in rel.parts[:-1]:
                cum = cum / part
                key = str(cum)
                if key not in dir_nodes:
                    node = QTreeWidgetItem(parent, [f"📁  {part}"])
                    node.setExpanded(True)
                    dir_nodes[key] = node
                parent = dir_nodes[key]

            item = QTreeWidgetItem(parent, [f"📄  {rel.parts[-1]}"])
            item.setCheckState(0, Qt.CheckState.Checked)
            item.setData(0, Qt.ItemDataRole.UserRole, str(fp))
            self.file_items.append((item, str(fp)))

    def _select_all(self):
        for item, _ in self.file_items:
            item.setCheckState(0, Qt.CheckState.Checked)

    def _deselect_all(self):
        for item, _ in self.file_items:
            item.setCheckState(0, Qt.CheckState.Unchecked)

    def _checked_files(self) -> list:
        return [fp for item, fp in self.file_items
                if item.checkState(0) == Qt.CheckState.Checked]

    def _find_conflicts(self, files: list, src: str, out: str) -> list:
        conflicts = []
        src_p = Path(src)
        out_p = Path(out)
        for fp_str in files:
            fp       = Path(fp_str)
            rel      = fp.relative_to(src_p)
            out_file = out_p / rel.parent / (fp.stem + ".pdf")
            if out_file.exists():
                conflicts.append(str(rel))
        return conflicts

    def _ask_overwrite(self, conflicts: list) -> str | None:
        count   = len(conflicts)
        preview = "\n".join(conflicts[:12])
        if count > 12:
            preview += f"\n... ({count - 12}개 더)"

        msg = QMessageBox(self)
        msg.setWindowTitle(self.t("dup_title"))
        msg.setText(self.t("dup_msg").format(count=count))
        msg.setDetailedText(preview)
        msg.setIcon(QMessageBox.Icon.Warning)

        ow_btn  = msg.addButton(self.t("overwrite_all"), QMessageBox.ButtonRole.AcceptRole)
        sk_btn  = msg.addButton(self.t("skip_existing"), QMessageBox.ButtonRole.ActionRole)
        _ca_btn = msg.addButton(self.t("cancel"),        QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(sk_btn)
        msg.exec()

        clicked = msg.clickedButton()
        if clicked == ow_btn:
            return "overwrite"
        if clicked == sk_btn:
            return "skip"
        return None   # cancel

    def _start_or_stop(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            return
        self._start_conversion()

    def _start_conversion(self):
        src   = self.src_edit.text().strip()
        out   = self.out_edit.text().strip()
        files = self._checked_files()

        if not src or not os.path.isdir(src):
            QMessageBox.warning(self, self.t("title"), self.t("no_src"))
            return
        if not out:
            QMessageBox.warning(self, self.t("title"), self.t("no_out"))
            return
        if not files:
            QMessageBox.warning(self, self.t("title"), self.t("no_files"))
            return

        lo_path = find_libreoffice()
        if not lo_path:
            QMessageBox.critical(self, self.t("title"), self.t("no_lo"))
            return

        # 중복 파일 확인
        overwrite_mode = "overwrite"
        conflicts = self._find_conflicts(files, src, out)
        if conflicts:
            choice = self._ask_overwrite(conflicts)
            if choice is None:
                return   # 취소
            overwrite_mode = choice

        self.log_box.clear()
        self.progress_bar.setMaximum(len(files))
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self._sync_convert_btn()

        self.worker = ConversionWorker(files, src, out, lo_path, overwrite_mode)
        self.worker.sig_progress.connect(self._on_progress)
        self.worker.sig_log.connect(self._on_log)
        self.worker.sig_done.connect(self._on_done)
        self.worker.start()

    # ── 슬롯 ──────────────────────────────────────────────────────────────────

    def _on_progress(self, current: int, total: int, name: str):
        self.progress_bar.setValue(current)
        pct = int(current / total * 100)
        self.progress_bar.setFormat(f"{pct}%  ({current}/{total})")
        self.status_lbl.setText(f"{self.t('converting')}: {name}")

    def _on_log(self, msg: str, status: str):
        color = {"ok": "#4ec9b0", "err": "#f44747", "skip": "#dcdcaa"}.get(status, "#d4d4d4")
        html  = msg.replace("&", "&amp;").replace("<", "&lt;").replace("\n", "<br>")
        self.log_box.append(
            f'<span style="color:{color};font-family:Consolas,monospace">{html}</span>'
        )

    def _on_done(self, success: int, fail: int, skip: int):
        self.progress_bar.setVisible(False)
        self._sync_convert_btn()

        stopped = bool(self.worker and self.worker._stop)
        if stopped:
            self.status_lbl.setText(self.t("stopped"))
            self.log_box.append(f'<br><span style="color:#f0a500"><b>{self.t("stopped")}</b></span>')
        else:
            summary = self.t("summary").format(s=success, f=fail, k=skip)
            self.status_lbl.setText(summary)
            color = "#4ec9b0" if fail == 0 else "#f0a500"
            self.log_box.append(f'<br><span style="color:{color}"><b>{summary}</b></span>')

            if self.open_folder_chk.isChecked():
                out = self.out_edit.text().strip()
                if out and os.path.isdir(out):
                    open_folder(out)

# ── 진입점 ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    apply_dark_palette(app)
    app.setStyleSheet(DARK_QSS)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
