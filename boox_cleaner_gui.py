"""
Boox Leaf3 Cleaner - GUI
=========================
대상 기기: Boox Leaf3 (D60_SMT_V02_2022_0309, Android 11)
테스트 환경: Windows 11 + ADB platform-tools
다른 Boox 모델/펌웨어에서는 패키지명이 다를 수 있음
제거 방식: pm uninstall -k --user 0 (사용자 레벨, 공장초기화 시 복구됨)
"""

import subprocess
import sys
import os
import shutil
import threading
from datetime import datetime

import customtkinter as ctk

# ── ADB 경로 후보 ────────────────────────────────────────
# PyInstaller --onefile 시 exe 위치 기준으로 탐색
if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ADB_PATHS = [
    os.path.join(_BASE_DIR, "platform-tools", "adb.exe"),
    os.path.join(_BASE_DIR, "adb.exe"),
    "adb",
    os.path.expanduser(r"~\platform-tools\adb.exe"),
]

# ── 제거 대상 패키지 ─────────────────────────────────────
PACKAGES = {
    "Boox 블로트웨어": [
        ("com.onyx.dict", "사전"),
        ("com.onyx.mail", "메일"),
        ("com.onyx.clock", "시계"),
        ("com.onyx.igetshop", "Boox 스토어"),
        ("com.onyx.musicplayer", "음악 플레이어"),
        ("com.onyx.gallery", "갤러리"),
        ("com.onyx.aiassistant", "AI 어시스턴트"),
        ("com.onyx.voicerecorder", "녹음기"),
        ("com.onyx.appmarket", "앱마켓"),
        ("com.onyx.calculator", "계산기"),
        ("com.onyx.easytransfer", "EasyTransfer"),
        ("com.onyx.android.ksync", "KSync"),
        ("com.onyx.android.production.test", "프로덕션 테스트"),
    ],
    "Boox 키보드 (Google 키보드 사용 시)": [
        ("com.onyx.kime", "한글 키보드"),
        ("com.onyx.latinime", "영문 키보드"),
    ],
    "Boox 기타": [
        ("com.onyx.floatingbutton", "플로팅 버튼"),
        ("com.onyx.kreader", "내장 리더"),
    ],
    "Android 불필요 앱": [
        ("org.chromium.chrome", "Chrome 브라우저"),
        ("com.android.providers.calendar", "캘린더 제공자"),
        ("com.google.android.syncadapters.calendar", "캘린더 동기화"),
        ("com.android.providers.contacts", "연락처 제공자"),
        ("com.google.android.syncadapters.contacts", "연락처 동기화"),
        ("com.android.quicksearchbox", "검색"),
        ("com.android.printspooler", "인쇄 스풀러"),
        ("com.android.printservice.recommendation", "인쇄 추천"),
        ("com.android.mms.service", "MMS 서비스"),
        ("com.android.smspush", "SMS Push"),
        ("com.android.wallpapercropper", "배경화면 크롭"),
        ("com.android.wallpaperbackup", "배경화면 백업"),
        ("com.google.android.apps.restore", "Google 복원"),
        ("com.android.calllogbackup", "통화기록 백업"),
        ("com.android.protips", "프로팁"),
        ("com.android.dreams.basic", "스크린세이버"),
        ("com.android.dreams.phototable", "스크린세이버(포토)"),
    ],
}

KEEP_PACKAGES = {
    "com.onyx": "Boox 런처/코어",
    "com.onyx.android.onyxotaservice": "펌웨어 업데이트",
}


# ── ADB 유틸 ─────────────────────────────────────────────

def find_adb() -> str:
    for path in ADB_PATHS:
        if os.path.isfile(path):
            return path
        if shutil.which(path):
            return path
    return ""


def run_adb(*args) -> tuple[int, str]:
    adb = find_adb()
    if not adb:
        return 1, "ADB를 찾을 수 없습니다"
    try:
        r = subprocess.run(
            [adb, *args],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        return r.returncode, r.stdout.strip()
    except subprocess.TimeoutExpired:
        return 1, "타임아웃"
    except Exception as e:
        return 1, str(e)


def get_device() -> str | None:
    code, out = run_adb("devices")
    for line in out.splitlines():
        if "\tdevice" in line:
            return line.split("\t")[0]
    return None


def get_installed_packages() -> set[str]:
    _, out = run_adb("shell", "pm", "list", "packages", "-e")
    return {line.replace("package:", "").strip() for line in out.splitlines() if line.startswith("package:")}


# ── GUI ──────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Boox Leaf3 Cleaner")
        self.geometry("750x820")
        self.minsize(650, 650)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.installed: set[str] = set()
        self.checkboxes: dict[str, tuple[ctk.CTkCheckBox, ctk.BooleanVar]] = {}
        self._current_device: str | None = None  # 현재 연결된 기기 ID

        self._build_ui()
        self._start_device_monitor()

    # ── UI 구성 ──────────────────────────────────────────

    def _build_ui(self):
        # 상단: 기기 상태
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=12, pady=(12, 6))

        self.status_label = ctk.CTkLabel(top, text="기기 연결 확인 중...", font=("", 14, "bold"))
        self.status_label.pack(side="left", padx=8, pady=8)

        self.refresh_btn = ctk.CTkButton(top, text="새로고침", width=90, command=self._refresh_device)
        self.refresh_btn.pack(side="right", padx=8, pady=8)

        # 기기 환경 정보
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=12, pady=(0, 4))

        info_text = (
            "테스트 기기 정보\n"
            "  모델: ONYX Boox Leaf3 (코드명: D60)\n"
            "  펌웨어: D60_SMT_V02_2022_0309\n"
            "  Android: 11 (API 30) · 플랫폼: Qualcomm Bengal\n"
            "  보안패치: 2024-02-01\n"
            "\n"
            "⚠ 이 도구는 위 기기/펌웨어에서만 테스트되었습니다.\n"
            "  다른 Boox 모델이나 펌웨어 버전에서는 패키지명이 다를 수 있습니다.\n"
            "  제거 방식: pm uninstall -k --user 0 (사용자 레벨 제거, 공장초기화 시 자동 복구)"
        )
        info_label = ctk.CTkLabel(info_frame, text=info_text, font=("Consolas", 11), text_color="gray", justify="left", anchor="w")
        info_label.pack(padx=10, pady=6, anchor="w")

        # 중간: 패키지 목록 (스크롤)
        self.list_frame = ctk.CTkScrollableFrame(self, label_text="앱 목록")
        self.list_frame.pack(fill="both", expand=True, padx=12, pady=6)

        # 전체 선택/해제
        sel_frame = ctk.CTkFrame(self)
        sel_frame.pack(fill="x", padx=12, pady=(0, 4))

        ctk.CTkButton(sel_frame, text="전체 선택", width=100, command=lambda: self._select_all(True)).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(sel_frame, text="전체 해제", width=100, command=lambda: self._select_all(False)).pack(side="left", padx=4, pady=4)

        installed_label = ctk.CTkLabel(sel_frame, text="", font=("", 12))
        installed_label.pack(side="right", padx=8, pady=4)
        self.installed_label = installed_label

        # 버튼
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", padx=12, pady=(0, 6))

        self.clean_btn = ctk.CTkButton(btn_frame, text="선택 앱 제거", fg_color="#c0392b", hover_color="#e74c3c", command=self._on_clean)
        self.clean_btn.pack(side="left", padx=4, pady=8, expand=True, fill="x")

        self.restore_btn = ctk.CTkButton(btn_frame, text="선택 앱 복구", fg_color="#2980b9", hover_color="#3498db", command=self._on_restore)
        self.restore_btn.pack(side="left", padx=4, pady=8, expand=True, fill="x")

        # 로그
        self.log_box = ctk.CTkTextbox(self, height=150, font=("Consolas", 12))
        self.log_box.pack(fill="x", padx=12, pady=(0, 12))
        self.log_box.configure(state="disabled")

    # ── 로그 ─────────────────────────────────────────────

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ── 기기 자동 감지 ─────────────────────────────────────

    def _start_device_monitor(self):
        """3초마다 기기 연결 상태를 백그라운드에서 확인."""
        def poll():
            device = get_device()
            self.after(0, self._on_device_poll, device)
        threading.Thread(target=poll, daemon=True).start()

    def _on_device_poll(self, device: str | None):
        prev = self._current_device
        self._current_device = device

        if device and not prev:
            # 새로 연결됨
            self.status_label.configure(text=f"연결됨: {device}", text_color="#2ecc71")
            self._log(f"기기 연결됨: {device}")
            self._refresh_list()
        elif not device and prev:
            # 연결 해제됨
            self.status_label.configure(text="기기 없음 — USB 디버깅 확인", text_color="#e74c3c")
            self._log("기기 연결 해제됨")
        elif device and prev and device != prev:
            # 다른 기기로 변경됨
            self.status_label.configure(text=f"연결됨: {device}", text_color="#2ecc71")
            self._log(f"기기 변경됨: {device}")
            self._refresh_list()

        # 3초 후 다시 폴링
        self.after(3000, self._start_device_monitor)

    def _refresh_device(self):
        """수동 새로고침 (버튼용)."""
        device = get_device()
        self._current_device = device
        if device:
            self.status_label.configure(text=f"연결됨: {device}", text_color="#2ecc71")
            self._log(f"기기 연결됨: {device}")
            self._refresh_list()
        else:
            self.status_label.configure(text="기기 없음 — USB 디버깅 확인", text_color="#e74c3c")
            self._log("기기를 찾을 수 없습니다")

    def _refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.checkboxes.clear()

        self.installed = get_installed_packages()
        total_removable = 0

        for category, pkgs in PACKAGES.items():
            has_any = any(p in self.installed for p, _ in pkgs)
            if not has_any:
                # 카테고리 전체 제거됨 — 복구용으로 표시
                cat_label = ctk.CTkLabel(self.list_frame, text=f"── {category} (모두 제거됨) ──", font=("", 12, "bold"), text_color="gray")
                cat_label.pack(anchor="w", padx=4, pady=(10, 2))
                for pkg, name in pkgs:
                    var = ctk.BooleanVar(value=False)
                    cb = ctk.CTkCheckBox(self.list_frame, text=f"  {name}  ({pkg})", variable=var, font=("", 12), text_color="gray")
                    cb.pack(anchor="w", padx=16, pady=1)
                    self.checkboxes[pkg] = (cb, var)
                continue

            cat_label = ctk.CTkLabel(self.list_frame, text=f"── {category} ──", font=("", 12, "bold"))
            cat_label.pack(anchor="w", padx=4, pady=(10, 2))

            for pkg, name in pkgs:
                var = ctk.BooleanVar(value=False)
                is_installed = pkg in self.installed
                if is_installed:
                    var.set(True)
                    total_removable += 1
                    color = "white"
                    status = ""
                else:
                    color = "gray"
                    status = " [제거됨]"

                cb = ctk.CTkCheckBox(self.list_frame, text=f"  {name}{status}  ({pkg})", variable=var, font=("", 12), text_color=color)
                cb.pack(anchor="w", padx=16, pady=1)
                self.checkboxes[pkg] = (cb, var)

        # 유지 권장 표시
        keep_label = ctk.CTkLabel(self.list_frame, text="── 유지 권장 (제거 불가) ──", font=("", 12, "bold"), text_color="#f39c12")
        keep_label.pack(anchor="w", padx=4, pady=(10, 2))
        for pkg, desc in KEEP_PACKAGES.items():
            status = "설치됨" if pkg in self.installed else "없음"
            lbl = ctk.CTkLabel(self.list_frame, text=f"  [{status}] {desc}  ({pkg})", font=("", 12), text_color="#f39c12")
            lbl.pack(anchor="w", padx=16, pady=1)

        self.installed_label.configure(text=f"설치됨: {total_removable}개 제거 가능")

    def _select_all(self, state: bool):
        for pkg, (cb, var) in self.checkboxes.items():
            var.set(state)

    # ── 제거/복구 ────────────────────────────────────────

    def _set_buttons(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self.clean_btn.configure(state=state)
        self.restore_btn.configure(state=state)
        self.refresh_btn.configure(state=state)

    def _get_selected(self) -> list[tuple[str, str]]:
        """선택된 패키지 [(pkg, name)] 반환."""
        all_pkgs = {p: n for pkgs in PACKAGES.values() for p, n in pkgs}
        return [(pkg, all_pkgs.get(pkg, pkg)) for pkg, (_, var) in self.checkboxes.items() if var.get()]

    def _on_clean(self):
        selected = [(p, n) for p, n in self._get_selected() if p in self.installed]
        if not selected:
            self._log("제거할 앱이 없습니다 (설치된 앱 중 선택된 것 없음)")
            return
        self._set_buttons(False)
        self._log(f"{len(selected)}개 앱 제거 시작...")
        threading.Thread(target=self._do_clean, args=(selected,), daemon=True).start()

    def _do_clean(self, targets: list[tuple[str, str]]):
        success, fail = 0, 0
        for pkg, name in targets:
            _, out = run_adb("shell", "pm", "uninstall", "-k", "--user", "0", pkg)
            if "Success" in out:
                self.after(0, self._log, f"  [OK] {name} ({pkg})")
                success += 1
            else:
                self.after(0, self._log, f"  [FAIL] {name} — {out}")
                fail += 1
        self.after(0, self._log, f"제거 완료: {success}개 성공, {fail}개 실패")
        self.after(0, self._set_buttons, True)
        self.after(0, self._refresh_list)

    def _on_restore(self):
        selected = [(p, n) for p, n in self._get_selected() if p not in self.installed]
        if not selected:
            self._log("복구할 앱이 없습니다 (제거된 앱 중 선택된 것 없음)")
            return
        self._set_buttons(False)
        self._log(f"{len(selected)}개 앱 복구 시작...")
        threading.Thread(target=self._do_restore, args=(selected,), daemon=True).start()

    def _do_restore(self, targets: list[tuple[str, str]]):
        success, fail = 0, 0
        for pkg, name in targets:
            _, out = run_adb("shell", "cmd", "package", "install-existing", pkg)
            if "install" in out.lower():
                self.after(0, self._log, f"  [OK] {name} ({pkg})")
                success += 1
            else:
                self.after(0, self._log, f"  [FAIL] {name} — {out}")
                fail += 1
        self.after(0, self._log, f"복구 완료: {success}개 성공, {fail}개 실패")
        self.after(0, self._set_buttons, True)
        self.after(0, self._refresh_list)


if __name__ == "__main__":
    app = App()
    app.mainloop()
