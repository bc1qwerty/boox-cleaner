"""
Boox Cleaner - GUI v2.3
========================
Boox E-ink 기기 블로트웨어 제거 + 시스템 최적화 도구.
기기를 자동 감지하여 모델별 제거 대상을 표시합니다.

지원 기기:
  - Boox Leaf3 (D60, Android 11)
  - Boox Palma2 Pro (Palma2_Pro_C, Android 13-15)

v2.3 변경사항 (2026-04-24):
  - 시스템 가속 최적화 기능 추가 (애니메이션 제거, 로그 버퍼 확장)
  - Palma 2 Pro 통신 관련 블로트웨어 목록 강화
  - 최신 펌웨어 대응 및 UI 개선
"""

VERSION = "2.3"

import subprocess
import sys
import os
import shutil
import threading
from datetime import datetime

import customtkinter as ctk

# ── ADB ──────────────────────────────────────────────────
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

# ── 기기 프로필 ──────────────────────────────────────────

DEVICE_PROFILES = {
    "Leaf3": {
        "display_name": "Boox Leaf3",
        "codename": "D60",
        "firmware": "D60_SMT_V02_2022_0309",
        "android": "11 (API 30)",
        "platform": "Qualcomm Bengal",
        "security_patch": "2024-02-01",
    },
    "Palma2_Pro_C": {
        "display_name": "Boox Palma2 Pro",
        "codename": "Palma2_Pro_C",
        "firmware": "4.1.1-rel (2025-12-27)",
        "android": "15 (API 35)",
        "platform": "Qualcomm Lito",
        "security_patch": "2025-10-01",
    },
}

# ── 앱 제거 대상 (pm uninstall -k --user 0) ─────────────

COMMON_PACKAGES = {
    "Boox 블로트웨어": [
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
        ("com.onyx.android.production.test", "프로덕션 테스트"),
    ],
    "Boox 키보드 (Google 키보드 사용 시)": [
        ("com.onyx.kime", "한글 키보드"),
        ("com.onyx.latinime", "영문 키보드"),
    ],
    "Boox 기타": [
        ("com.onyx.floatingbutton", "플로팅 버튼"),
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

DEVICE_EXTRA_PACKAGES = {
    "Palma2_Pro_C": {
        "Palma2 Pro 전용": [
            ("com.onyx.android.note", "노트"),
            ("com.onyx.tscalibration", "TS 캘리브레이션"),
            ("org.codeaurora.snapcam", "카메라 (SnapCam)"),
            ("org.codeaurora.dialer", "다이얼러"),
            ("com.android.contacts", "연락처 앱"),
            ("com.android.mms", "문자/MMS"),
            ("com.android.stk", "SIM 툴킷"),
            ("com.google.android.apps.books", "Google Books"),
            ("com.google.android.tts", "Google TTS"),
            ("com.android.emergency", "긴급 정보"),
            ("com.android.storagemanager", "저장공간 관리"),
            ("com.android.soundpicker", "소리 선택기"),
        ],
    },
}

# ── 서비스 비활성화 대상 (pm disable-user) ────────────────

COMMON_SERVICES = {
    "불필요 시스템 서비스": [
        ("com.android.cellbroadcastreceiver", "긴급재난문자"),
        ("com.android.cellbroadcastservice", "긴급재난문자 서비스"),
        ("com.android.cellbroadcastreceiver.module", "긴급재난문자 모듈"),
        ("com.android.cellbroadcastreceiver.overlay.common", "긴급재난문자 오버레이"),
        ("com.android.bips", "인쇄 (BIPS)"),
        ("com.android.htmlviewer", "HTML 뷰어"),
        ("com.android.DeviceAsWebcam", "웹캠 모드"),
        ("com.android.hotspot2.osulogin", "핫스팟 2.0 로그인"),
        ("com.android.managedprovisioning", "기기 프로비저닝"),
        ("com.android.emergency", "긴급 정보"),
        ("com.android.storagemanager", "저장공간 관리"),
    ],
    "Qualcomm 불필요 서비스": [
        ("com.qualcomm.qti.xrwifi", "XR WiFi"),
        ("com.qualcomm.qti.xrvd.service", "XR 비디오"),
        ("com.qualcomm.qti.xrcb", "XR 콜백"),
        ("com.qualcomm.qti.ridemodeaudio", "라이드 모드 오디오"),
        ("com.qualcomm.qti.voiceai.speech", "음성 AI"),
        ("vendor.qti.bluetooth.xpan", "BT XPAN"),
        ("vendor.qti.data.ntnsatapp", "위성 통신"),
    ],
    "블루투스 (사용 안 할 경우)": [
        ("com.android.bluetooth", "블루투스"),
    ],
}

SIM_SERVICES = {
    "SIM/통신 관련 (SIM 미사용 시)": [
        ("com.qti.phone", "전화 서비스"),
        ("com.qualcomm.qti.lpa", "eSIM 프로비저닝"),
        ("com.qualcomm.qti.confdialer", "회의전화"),
        ("com.qualcomm.qti.simcontacts", "SIM 연락처"),
        ("com.qualcomm.qti.callfeaturessetting", "통화 기능 설정"),
        ("com.qualcomm.qti.uimGbaApp", "SIM 인증"),
        ("com.qualcomm.uimremoteserver", "SIM 원격 서버"),
        ("com.qualcomm.uimremoteclient", "SIM 원격 클라이언트"),
        ("com.qualcomm.qti.remoteSimlockAuth", "SIM 잠금 인증"),
        ("com.qualcomm.qti.uceShimService", "통신 UCE"),
        ("com.qualcomm.qti.poweroffalarm", "전원꺼짐 알람"),
        ("com.qti.xdivert", "착신전환"),
        ("com.qti.dcf", "DCF 서비스"),
        ("com.android.imsserviceentitlement", "IMS 서비스"),
        ("com.android.simappdialog", "SIM 앱 다이얼로그"),
        ("vendor.qti.imsrcs", "IMS RCS"),
        ("vendor.qti.imsdatachannel", "IMS 데이터채널"),
    ],
}

# ── 성능 최적화 설정 ─────────────────────────────────────

PERFORMANCE_SETTINGS = [
    {
        "key": "window_animation_scale",
        "name": "창 애니메이션 끄기",
        "desc": "E-ink 잔상 제거 및 체감 속도 향상",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "transition_animation_scale",
        "name": "전환 애니메이션 끄기",
        "desc": "E-ink 잔상 제거 및 체감 속도 향상",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "animator_duration_scale",
        "name": "애니메이션 시간 0",
        "desc": "E-ink 잔상 제거 및 체감 속도 향상",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "background_process_limit",
        "name": "백그라운드 프로세스 제한",
        "desc": "최대 2개로 제한하여 메모리/CPU 확보",
        "namespace": "global",
        "on_value": "2",
        "off_value": "null",
    },
    {
        "key": "force_hw_ui",
        "name": "GPU 강제 렌더링",
        "desc": "UI 렌더링을 GPU로 가속",
        "namespace": "global",
        "on_value": "1",
        "off_value": "0",
    },
    {
        "key": "heads_up_notifications_enabled",
        "name": "알림 팝업 비활성화",
        "desc": "불필요한 UI 갱신 제거",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "ble_scan_always_enabled",
        "name": "BLE 항상 스캔 끄기",
        "desc": "백그라운드 블루투스 스캔 중단",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "wifi_scan_always_enabled",
        "name": "WiFi 항상 스캔 끄기",
        "desc": "백그라운드 WiFi 스캔 중단",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "wifi_sleep_policy",
        "name": "WiFi 절전 (화면 꺼지면 끊기)",
        "desc": "대기 시 전력 절약",
        "namespace": "global",
        "on_value": "2",
        "off_value": "0",
    },
    {
        "key": "bluetooth_on",
        "name": "블루투스 끄기",
        "desc": "블루투스 사용 안 할 경우 전력 절약",
        "namespace": "global",
        "on_value": "0",
        "off_value": "1",
    },
    {
        "key": "log_buffer_size",
        "name": "로그 버퍼 확장 (16M)",
        "desc": "시스템 로그 기록으로 인한 지연 방지",
        "namespace": "custom",
        "on_value": "16M",
        "off_value": "256K",
    },
]

# com.onyx (ContentBrowser) 가 실행 중 참조하는 ContentProvider/서비스 공급 패키지.
# 제거하면 SecurityException 또는 기능별 크래시가 발생하여 기기가 부팅 루프에 빠질 수 있음.
# (2026-04-12 분석: kreader 제거 → FilesChangedReceiverAction 크래시 → 리커버리 진입 확인)
KEEP_PACKAGES = {
    "com.onyx": "Boox 런처/코어",
    "com.onyx.android.onyxotaservice": "펌웨어 업데이트",
    "com.onyx.kreader": "내장 리더 (content.database.ContentProvider 공급, 제거 금지)",
    "com.onyx.android.ksync": "KSync (cloudstorage/sync ContentProvider + 서비스 공급)",
    "com.onyx.dict": "사전 (DictionaryProvider/OnyxNewWordProvider 공급)",
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


def get_device_model() -> str:
    _, out = run_adb("shell", "getprop", "ro.product.model")
    return out.strip()


def get_device_info() -> dict[str, str]:
    props = {
        "model": "ro.product.model",
        "brand": "ro.product.brand",
        "firmware": "ro.build.display.id",
        "android": "ro.build.version.release",
        "sdk": "ro.build.version.sdk",
        "platform": "ro.board.platform",
        "security_patch": "ro.build.version.security_patch",
    }
    info = {}
    for key, prop in props.items():
        _, val = run_adb("shell", "getprop", prop)
        info[key] = val.strip()
    return info


def get_installed_packages() -> set[str]:
    _, out = run_adb("shell", "pm", "list", "packages", "-e")
    return {line.replace("package:", "").strip() for line in out.splitlines() if line.startswith("package:")}


def get_disabled_packages() -> set[str]:
    _, out = run_adb("shell", "pm", "list", "packages", "-d")
    return {line.replace("package:", "").strip() for line in out.splitlines() if line.startswith("package:")}


def get_packages_for_device(model: str) -> dict[str, list[tuple[str, str]]]:
    packages = dict(COMMON_PACKAGES)
    packages.update(DEVICE_EXTRA_PACKAGES.get(model, {}))
    return packages


def get_services_for_device(model: str) -> dict[str, list[tuple[str, str]]]:
    services = dict(COMMON_SERVICES)
    services.update(SIM_SERVICES)
    return services


# ── GUI ──────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"Boox Cleaner v{VERSION}")
        self.geometry("780x880")
        self.minsize(680, 700)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.installed: set[str] = set()
        self.disabled: set[str] = set()
        self.app_checkboxes: dict[str, tuple[ctk.CTkCheckBox, ctk.BooleanVar]] = {}
        self.svc_checkboxes: dict[str, tuple[ctk.CTkCheckBox, ctk.BooleanVar]] = {}
        self._current_device: str | None = None
        self._current_model: str = ""
        self._current_packages: dict[str, list[tuple[str, str]]] = {}
        self._current_services: dict[str, list[tuple[str, str]]] = {}

        self._build_ui()
        self._start_device_monitor()

    def _build_ui(self):
        # 상단: 기기 상태
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=12, pady=(12, 6))

        self.status_label = ctk.CTkLabel(top, text="기기 연결 확인 중...", font=("", 14, "bold"))
        self.status_label.pack(side="left", padx=8, pady=8)

        self.refresh_btn = ctk.CTkButton(top, text="새로고침", width=90, command=self._refresh_device)
        self.refresh_btn.pack(side="right", padx=8, pady=8)

        # 기기 정보
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill="x", padx=12, pady=(0, 4))

        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="기기를 연결하면 자동으로 모델을 감지합니다.\n\n"
                 "지원 기기: Boox Leaf3, Boox Palma2 Pro\n"
                 "제거/비활성화 모두 공장초기화 시 자동 복구됨",
            font=("Consolas", 11), text_color="gray", justify="left", anchor="w",
        )
        self.info_label.pack(padx=10, pady=6, anchor="w")

        # 탭
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=12, pady=6)

        self.tab_apps = self.tabview.add("앱 제거")
        self.tab_services = self.tabview.add("서비스 비활성화")
        self.tab_perf = self.tabview.add("성능 최적화")

        self._build_apps_tab()
        self._build_services_tab()
        self._build_perf_tab()

        # 로그
        self.log_box = ctk.CTkTextbox(self, height=130, font=("Consolas", 12))
        self.log_box.pack(fill="x", padx=12, pady=(0, 12))
        self.log_box.configure(state="disabled")

    # ── 앱 제거 탭 ───────────────────────────────────────

    def _build_apps_tab(self):
        self.app_list_frame = ctk.CTkScrollableFrame(self.tab_apps)
        self.app_list_frame.pack(fill="both", expand=True, pady=(0, 4))

        sel = ctk.CTkFrame(self.tab_apps)
        sel.pack(fill="x", pady=(0, 4))
        ctk.CTkButton(sel, text="전체 선택", width=90, command=lambda: self._select_all_dict(self.app_checkboxes, True)).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(sel, text="전체 해제", width=90, command=lambda: self._select_all_dict(self.app_checkboxes, False)).pack(side="left", padx=4, pady=4)
        self.app_count_label = ctk.CTkLabel(sel, text="", font=("", 12))
        self.app_count_label.pack(side="right", padx=8, pady=4)

        btn = ctk.CTkFrame(self.tab_apps)
        btn.pack(fill="x")
        self.app_clean_btn = ctk.CTkButton(btn, text="선택 앱 제거", fg_color="#c0392b", hover_color="#e74c3c", command=self._on_app_clean)
        self.app_clean_btn.pack(side="left", padx=4, pady=4, expand=True, fill="x")
        self.app_restore_btn = ctk.CTkButton(btn, text="선택 앱 복구", fg_color="#2980b9", hover_color="#3498db", command=self._on_app_restore)
        self.app_restore_btn.pack(side="left", padx=4, pady=4, expand=True, fill="x")

    # ── 서비스 비활성화 탭 ───────────────────────────────

    def _build_services_tab(self):
        self.svc_list_frame = ctk.CTkScrollableFrame(self.tab_services)
        self.svc_list_frame.pack(fill="both", expand=True, pady=(0, 4))

        sel = ctk.CTkFrame(self.tab_services)
        sel.pack(fill="x", pady=(0, 4))
        ctk.CTkButton(sel, text="전체 선택", width=90, command=lambda: self._select_all_dict(self.svc_checkboxes, True)).pack(side="left", padx=4, pady=4)
        ctk.CTkButton(sel, text="전체 해제", width=90, command=lambda: self._select_all_dict(self.svc_checkboxes, False)).pack(side="left", padx=4, pady=4)
        self.svc_count_label = ctk.CTkLabel(sel, text="", font=("", 12))
        self.svc_count_label.pack(side="right", padx=8, pady=4)

        btn = ctk.CTkFrame(self.tab_services)
        btn.pack(fill="x")
        self.svc_disable_btn = ctk.CTkButton(btn, text="선택 서비스 비활성화", fg_color="#c0392b", hover_color="#e74c3c", command=self._on_svc_disable)
        self.svc_disable_btn.pack(side="left", padx=4, pady=4, expand=True, fill="x")
        self.svc_enable_btn = ctk.CTkButton(btn, text="선택 서비스 복구", fg_color="#2980b9", hover_color="#3498db", command=self._on_svc_enable)
        self.svc_enable_btn.pack(side="left", padx=4, pady=4, expand=True, fill="x")

    # ── 성능 최적화 탭 ───────────────────────────────────

    def _build_perf_tab(self):
        self.perf_frame = ctk.CTkScrollableFrame(self.tab_perf)
        self.perf_frame.pack(fill="both", expand=True, pady=(0, 4))

        self.perf_vars: dict[str, ctk.BooleanVar] = {}
        for s in PERFORMANCE_SETTINGS:
            var = ctk.BooleanVar(value=False)
            frame = ctk.CTkFrame(self.perf_frame)
            frame.pack(fill="x", padx=4, pady=2)
            cb = ctk.CTkCheckBox(frame, text=f"  {s['name']}", variable=var, font=("", 12))
            cb.pack(side="left", padx=8, pady=4)
            desc = ctk.CTkLabel(frame, text=s["desc"], font=("", 11), text_color="gray")
            desc.pack(side="left", padx=8, pady=4)
            self.perf_vars[s["key"]] = var

        btn = ctk.CTkFrame(self.tab_perf)
        btn.pack(fill="x")
        self.perf_apply_btn = ctk.CTkButton(btn, text="선택 항목 적용", fg_color="#27ae60", hover_color="#2ecc71", command=self._on_perf_apply)
        self.perf_apply_btn.pack(side="left", padx=4, pady=4, expand=True, fill="x")
        self.perf_reset_btn = ctk.CTkButton(btn, text="선택 항목 초기화", fg_color="#7f8c8d", hover_color="#95a5a6", command=self._on_perf_reset)
        self.perf_reset_btn.pack(side="left", padx=4, pady=4, expand=True, fill="x")

    # ── 로그 ─────────────────────────────────────────────

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ── 기기 정보 ────────────────────────────────────────

    def _update_device_info(self, model: str):
        profile = DEVICE_PROFILES.get(model)
        if profile:
            info_text = (
                f"감지된 기기: {profile['display_name']}\n"
                f"  코드명: {profile['codename']} · 펌웨어: {profile['firmware']}\n"
                f"  Android: {profile['android']} · 플랫폼: {profile['platform']}\n"
                f"  보안패치: {profile['security_patch']}"
            )
        else:
            info = get_device_info()
            info_text = (
                f"감지된 기기: {info.get('model', '알 수 없음')} (미등록 모델)\n"
                f"  브랜드: {info.get('brand', '-')} · 펌웨어: {info.get('firmware', '-')}\n"
                f"  Android: {info.get('android', '-')} (API {info.get('sdk', '-')}) · 플랫폼: {info.get('platform', '-')}\n"
                f"  보안패치: {info.get('security_patch', '-')}"
            )
        warn = "\n⚠ 제거/비활성화 모두 공장초기화 시 자동 복구됨"
        self.info_label.configure(text=info_text + warn)

    # ── 기기 자동 감지 ───────────────────────────────────

    def _start_device_monitor(self):
        def poll():
            device = get_device()
            model = get_device_model() if device else ""
            self.after(0, self._on_device_poll, device, model)
        threading.Thread(target=poll, daemon=True).start()

    def _on_device_poll(self, device: str | None, model: str):
        prev = self._current_device
        self._current_device = device

        if device and not prev:
            self._on_device_connected(device, model)
        elif not device and prev:
            self.status_label.configure(text="기기 없음 — USB 디버깅 확인", text_color="#e74c3c")
            self._log("기기 연결 해제됨")
            self._current_model = ""
        elif device and prev and device != prev:
            self._on_device_connected(device, model)

        self.after(3000, self._start_device_monitor)

    def _on_device_connected(self, device: str, model: str):
        self._current_model = model
        self._current_packages = get_packages_for_device(model)
        self._current_services = get_services_for_device(model)
        display = DEVICE_PROFILES.get(model, {}).get("display_name", model)
        self.status_label.configure(text=f"연결됨: {display} ({device})", text_color="#2ecc71")
        self._log(f"기기 연결됨: {display} ({device})")
        self._update_device_info(model)
        self._refresh_all()

    def _refresh_device(self):
        device = get_device()
        self._current_device = device
        if device:
            model = get_device_model()
            self._on_device_connected(device, model)
        else:
            self.status_label.configure(text="기기 없음 — USB 디버깅 확인", text_color="#e74c3c")
            self._log("기기를 찾을 수 없습니다")

    def _refresh_all(self):
        self.installed = get_installed_packages()
        self.disabled = get_disabled_packages()
        self._refresh_app_list()
        self._refresh_svc_list()
        self._refresh_perf_status()

    # ── 앱 목록 ──────────────────────────────────────────

    def _refresh_app_list(self):
        for w in self.app_list_frame.winfo_children():
            w.destroy()
        self.app_checkboxes.clear()
        packages = self._current_packages or COMMON_PACKAGES
        total = 0

        for category, pkgs in packages.items():
            has_any = any(p in self.installed for p, _ in pkgs)
            cat_text = f"── {category}{'' if has_any else ' (모두 제거됨)'} ──"
            cat_color = "white" if has_any else "gray"
            ctk.CTkLabel(self.app_list_frame, text=cat_text, font=("", 12, "bold"), text_color=cat_color).pack(anchor="w", padx=4, pady=(10, 2))

            for pkg, name in pkgs:
                var = ctk.BooleanVar(value=False)
                is_installed = pkg in self.installed
                if is_installed:
                    var.set(True)
                    total += 1
                status = "" if is_installed else " [제거됨]"
                color = "white" if is_installed else "gray"
                cb = ctk.CTkCheckBox(self.app_list_frame, text=f"  {name}{status}  ({pkg})", variable=var, font=("", 12), text_color=color)
                cb.pack(anchor="w", padx=16, pady=1)
                self.app_checkboxes[pkg] = (cb, var)

        ctk.CTkLabel(self.app_list_frame, text="── 유지 권장 (제거 불가) ──", font=("", 12, "bold"), text_color="#f39c12").pack(anchor="w", padx=4, pady=(10, 2))
        for pkg, desc in KEEP_PACKAGES.items():
            status = "설치됨" if pkg in self.installed else "없음"
            ctk.CTkLabel(self.app_list_frame, text=f"  [{status}] {desc}  ({pkg})", font=("", 12), text_color="#f39c12").pack(anchor="w", padx=16, pady=1)

        self.app_count_label.configure(text=f"{total}개 제거 가능")

    # ── 서비스 목록 ──────────────────────────────────────

    def _refresh_svc_list(self):
        for w in self.svc_list_frame.winfo_children():
            w.destroy()
        self.svc_checkboxes.clear()
        services = self._current_services or COMMON_SERVICES
        total_active = 0

        all_known = self.installed | self.disabled
        for category, svcs in services.items():
            exists = [p for p, _ in svcs if p in all_known]
            if not exists:
                continue
            has_active = any(p in self.installed for p, _ in svcs)
            cat_text = f"── {category}{'' if has_active else ' (모두 비활성화됨)'} ──"
            cat_color = "white" if has_active else "gray"
            ctk.CTkLabel(self.svc_list_frame, text=cat_text, font=("", 12, "bold"), text_color=cat_color).pack(anchor="w", padx=4, pady=(10, 2))

            for pkg, name in svcs:
                if pkg not in all_known:
                    continue
                var = ctk.BooleanVar(value=False)
                is_active = pkg in self.installed
                if is_active:
                    var.set(True)
                    total_active += 1
                status = "" if is_active else " [비활성화됨]"
                color = "white" if is_active else "gray"
                cb = ctk.CTkCheckBox(self.svc_list_frame, text=f"  {name}{status}  ({pkg})", variable=var, font=("", 12), text_color=color)
                cb.pack(anchor="w", padx=16, pady=1)
                self.svc_checkboxes[pkg] = (cb, var)

        self.svc_count_label.configure(text=f"{total_active}개 비활성화 가능")

    # ── 성능 상태 ────────────────────────────────────────

    def _refresh_perf_status(self):
        for s in PERFORMANCE_SETTINGS:
            if s["namespace"] == "custom" and s["key"] == "log_buffer_size":
                _, val = run_adb("shell", "logcat", "-g")
                # 출력 예: "main: 256Kb (..." 또는 "main: 16Mb (..."
                is_optimized = s["on_value"].lower() in val.lower()
            else:
                _, val = run_adb("shell", "settings", "get", s["namespace"], s["key"])
                val = val.strip()
                is_optimized = (val == s["on_value"])
            
            self.perf_vars[s["key"]].set(is_optimized)

    # ── 공통 유틸 ────────────────────────────────────────

    def _select_all_dict(self, checkboxes: dict, state: bool):
        for _, (cb, var) in checkboxes.items():
            var.set(state)

    def _set_all_buttons(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        for btn in [self.app_clean_btn, self.app_restore_btn, self.svc_disable_btn, self.svc_enable_btn, self.perf_apply_btn, self.perf_reset_btn, self.refresh_btn]:
            btn.configure(state=state)

    # ── 앱 제거/복구 ────────────────────────────────────

    def _on_app_clean(self):
        packages = self._current_packages or COMMON_PACKAGES
        all_pkgs = {p: n for pkgs in packages.values() for p, n in pkgs}
        selected = [(pkg, all_pkgs.get(pkg, pkg)) for pkg, (_, var) in self.app_checkboxes.items() if var.get() and pkg in self.installed]
        if not selected:
            self._log("제거할 앱이 없습니다")
            return
        self._set_all_buttons(False)
        self._log(f"{len(selected)}개 앱 제거 시작...")
        threading.Thread(target=self._do_app_action, args=(selected, "uninstall"), daemon=True).start()

    def _on_app_restore(self):
        packages = self._current_packages or COMMON_PACKAGES
        all_pkgs = {p: n for pkgs in packages.values() for p, n in pkgs}
        selected = [(pkg, all_pkgs.get(pkg, pkg)) for pkg, (_, var) in self.app_checkboxes.items() if var.get() and pkg not in self.installed]
        if not selected:
            self._log("복구할 앱이 없습니다")
            return
        self._set_all_buttons(False)
        self._log(f"{len(selected)}개 앱 복구 시작...")
        threading.Thread(target=self._do_app_action, args=(selected, "restore"), daemon=True).start()

    def _do_app_action(self, targets: list[tuple[str, str]], action: str):
        success, fail = 0, 0
        for pkg, name in targets:
            if action == "uninstall":
                _, out = run_adb("shell", "pm", "uninstall", "-k", "--user", "0", pkg)
                ok = "Success" in out
            else:
                _, out = run_adb("shell", "cmd", "package", "install-existing", pkg)
                ok = "install" in out.lower()
            if ok:
                self.after(0, self._log, f"  [OK] {name} ({pkg})")
                success += 1
            else:
                self.after(0, self._log, f"  [FAIL] {name} — {out}")
                fail += 1
        label = "제거" if action == "uninstall" else "복구"
        self.after(0, self._log, f"{label} 완료: {success}개 성공, {fail}개 실패")
        self.after(0, self._set_all_buttons, True)
        self.after(0, self._refresh_all)

    # ── 서비스 비활성화/복구 ─────────────────────────────

    def _on_svc_disable(self):
        services = self._current_services or COMMON_SERVICES
        all_svcs = {p: n for svcs in services.values() for p, n in svcs}
        selected = [(pkg, all_svcs.get(pkg, pkg)) for pkg, (_, var) in self.svc_checkboxes.items() if var.get() and pkg in self.installed]
        if not selected:
            self._log("비활성화할 서비스가 없습니다")
            return
        self._set_all_buttons(False)
        self._log(f"{len(selected)}개 서비스 비활성화 시작...")
        threading.Thread(target=self._do_svc_action, args=(selected, "disable"), daemon=True).start()

    def _on_svc_enable(self):
        services = self._current_services or COMMON_SERVICES
        all_svcs = {p: n for svcs in services.values() for p, n in svcs}
        selected = [(pkg, all_svcs.get(pkg, pkg)) for pkg, (_, var) in self.svc_checkboxes.items() if var.get() and pkg not in self.installed]
        if not selected:
            self._log("복구할 서비스가 없습니다")
            return
        self._set_all_buttons(False)
        self._log(f"{len(selected)}개 서비스 복구 시작...")
        threading.Thread(target=self._do_svc_action, args=(selected, "enable"), daemon=True).start()

    def _do_svc_action(self, targets: list[tuple[str, str]], action: str):
        success, fail = 0, 0
        for pkg, name in targets:
            if action == "disable":
                _, out = run_adb("shell", "pm", "disable-user", "--user", "0", pkg)
                ok = "disabled" in out.lower()
            else:
                _, out = run_adb("shell", "pm", "enable", pkg)
                ok = "enabled" in out.lower()
            if ok:
                self.after(0, self._log, f"  [OK] {name} ({pkg})")
                success += 1
            else:
                self.after(0, self._log, f"  [FAIL] {name} — {out}")
                fail += 1
        label = "비활성화" if action == "disable" else "복구"
        self.after(0, self._log, f"{label} 완료: {success}개 성공, {fail}개 실패")
        self.after(0, self._set_all_buttons, True)
        self.after(0, self._refresh_all)

    # ── 성능 적용/초기화 ────────────────────────────────

    def _on_perf_apply(self):
        selected = [s for s in PERFORMANCE_SETTINGS if self.perf_vars[s["key"]].get()]
        if not selected:
            self._log("적용할 항목이 없습니다")
            return
        self._set_all_buttons(False)
        self._log(f"{len(selected)}개 성능 설정 적용 시작...")
        threading.Thread(target=self._do_perf, args=(selected, "apply"), daemon=True).start()

    def _on_perf_reset(self):
        selected = [s for s in PERFORMANCE_SETTINGS if self.perf_vars[s["key"]].get()]
        if not selected:
            self._log("초기화할 항목이 없습니다")
            return
        self._set_all_buttons(False)
        self._log(f"{len(selected)}개 성능 설정 초기화 시작...")
        threading.Thread(target=self._do_perf, args=(selected, "reset"), daemon=True).start()

    def _do_perf(self, settings: list[dict], action: str):
        success = 0
        for s in settings:
            value = s["on_value"] if action == "apply" else s["off_value"]
            if s["namespace"] == "custom" and s["key"] == "log_buffer_size":
                _, out = run_adb("shell", "logcat", "-G", value)
            elif value == "null":
                _, out = run_adb("shell", "settings", "delete", s["namespace"], s["key"])
            else:
                _, out = run_adb("shell", "settings", "put", s["namespace"], s["key"], value)
            self.after(0, self._log, f"  [OK] {s['name']} → {value}")
            success += 1
        label = "적용" if action == "apply" else "초기화"
        self.after(0, self._log, f"{label} 완료: {success}개")
        self.after(0, self._set_all_buttons, True)
        self.after(0, self._refresh_perf_status)


if __name__ == "__main__":
    app = App()
    app.mainloop()
