"""
Boox Leaf3 블로트웨어 제거 도구
================================
⚠️ 환경 제한사항:
  - 대상 기기: Boox Leaf3 (D60_SMT_V02_2022_0309, Android 11)
  - 테스트 환경: Windows 11, ADB platform-tools
  - 다른 Boox 모델/펌웨어에서는 패키지명이 다를 수 있음
  - 제거 방식: pm uninstall -k --user 0 (사용자 레벨, 공장초기화 시 복구됨)

사용법:
  py boox_cleaner.py              # 대화형 모드
  py boox_cleaner.py --list       # 제거 대상 목록만 출력
  py boox_cleaner.py --clean      # 전체 제거 실행
  py boox_cleaner.py --restore    # 제거한 앱 복구
"""

import subprocess
import sys
import shutil
import os

# Windows 콘솔 UTF-8 설정
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ADB 경로 (환경에 맞게 수정)
ADB_PATHS = [
    "adb",
    r"C:\Users\SEO\platform-tools\adb.exe",
]

# ── 제거 대상 패키지 ──────────────────────────────────────
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
        ("com.onyx.kime", "Boox 한글 키보드"),
        ("com.onyx.latinime", "Boox 영문 키보드"),
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

# ── 유지해야 할 패키지 (참고용) ───────────────────────────
KEEP_PACKAGES = {
    "com.onyx": "Boox 런처/코어 (시스템 기능 포함, 제거 금지)",
    "com.onyx.android.onyxotaservice": "펌웨어 업데이트",
}


def find_adb() -> str:
    """사용 가능한 ADB 경로를 찾는다."""
    for path in ADB_PATHS:
        if shutil.which(path) or shutil.which(path.replace("/", "\\")):
            return path
    # 직접 존재 확인
    import os
    for path in ADB_PATHS:
        if os.path.isfile(path):
            return path
    return ""


def run_adb(*args) -> tuple[int, str]:
    """ADB 명령 실행 후 (returncode, stdout) 반환."""
    adb = find_adb()
    if not adb:
        print("[ERROR] ADB를 찾을 수 없습니다. platform-tools 경로를 확인하세요.")
        sys.exit(1)
    try:
        r = subprocess.run(
            [adb, *args],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        return r.returncode, r.stdout.strip()
    except subprocess.TimeoutExpired:
        return 1, "timeout"


def check_device() -> bool:
    """기기 연결 상태 확인."""
    code, out = run_adb("devices")
    lines = [l for l in out.splitlines() if "\tdevice" in l]
    if not lines:
        print("[ERROR] 연결된 기기가 없습니다.")
        print("  - USB 케이블 연결 확인")
        print("  - USB 디버깅 활성화 확인")
        print("  - 'USB 디버깅 허용' 팝업에서 허용 클릭")
        return False
    device_id = lines[0].split("\t")[0]
    print(f"[OK] 기기 연결됨: {device_id}")
    return True


def get_installed_packages() -> set[str]:
    """현재 설치된(활성) 패키지 목록."""
    _, out = run_adb("shell", "pm", "list", "packages", "-e")
    return {line.replace("package:", "") for line in out.splitlines()}


def list_packages():
    """제거 대상 목록 출력."""
    installed = get_installed_packages()
    total = 0
    for category, pkgs in PACKAGES.items():
        targets = [(p, n) for p, n in pkgs if p in installed]
        if not targets:
            continue
        print(f"\n── {category} ({len(targets)}개) ──")
        for pkg, name in targets:
            print(f"  {name:<20s}  {pkg}")
            total += 1
    if total == 0:
        print("\n이미 모두 제거되었습니다!")
    else:
        print(f"\n총 {total}개 제거 가능")
    print(f"\n── 유지 권장 ──")
    for pkg, desc in KEEP_PACKAGES.items():
        status = "설치됨" if pkg in installed else "없음"
        print(f"  [{status}] {desc}  ({pkg})")


def clean_packages():
    """블로트웨어 제거 실행."""
    installed = get_installed_packages()
    all_pkgs = [(p, n, c) for c, pkgs in PACKAGES.items() for p, n in pkgs]
    targets = [(p, n, c) for p, n, c in all_pkgs if p in installed]

    if not targets:
        print("제거할 앱이 없습니다. 이미 정리 완료!")
        return

    print(f"\n{len(targets)}개 앱을 제거합니다...\n")
    success, fail = 0, 0
    for pkg, name, category in targets:
        code, out = run_adb("shell", "pm", "uninstall", "-k", "--user", "0", pkg)
        if "Success" in out:
            print(f"  [OK] {name} ({pkg})")
            success += 1
        else:
            print(f"  [FAIL] {name} ({pkg}) - {out}")
            fail += 1

    print(f"\n완료: {success}개 제거, {fail}개 실패")
    if success > 0:
        print("복구하려면: py boox_cleaner.py --restore")


def restore_packages():
    """제거한 앱 복구."""
    installed = get_installed_packages()
    all_pkgs = [(p, n) for pkgs in PACKAGES.values() for p, n in pkgs]
    removed = [(p, n) for p, n in all_pkgs if p not in installed]

    if not removed:
        print("복구할 앱이 없습니다.")
        return

    print(f"\n{len(removed)}개 앱을 복구합니다...\n")
    success, fail = 0, 0
    for pkg, name in removed:
        code, out = run_adb("shell", "cmd", "package", "install-existing", pkg)
        if code == 0 and "install" in out.lower():
            print(f"  [OK] {name} ({pkg})")
            success += 1
        else:
            print(f"  [FAIL] {name} ({pkg}) - {out}")
            fail += 1

    print(f"\n완료: {success}개 복구, {fail}개 실패")


def interactive_mode():
    """대화형 모드."""
    print("=" * 50)
    print("  Boox Leaf3 블로트웨어 제거 도구")
    print("=" * 50)
    print()
    print("⚠️  이 도구는 아래 환경에서 테스트되었습니다:")
    print("    기기: Boox Leaf3 (D60_SMT, Android 11)")
    print("    PC: Windows 11 + ADB platform-tools")
    print("    다른 기기/펌웨어에서는 결과가 다를 수 있습니다.")
    print()

    if not check_device():
        return

    print()
    print("[1] 제거 대상 목록 보기")
    print("[2] 블로트웨어 제거 실행")
    print("[3] 제거한 앱 복구")
    print("[q] 종료")
    print()

    choice = input("선택: ").strip()
    if choice == "1":
        list_packages()
    elif choice == "2":
        list_packages()
        print()
        confirm = input("위 앱들을 제거하시겠습니까? (y/N): ").strip().lower()
        if confirm == "y":
            clean_packages()
        else:
            print("취소됨.")
    elif choice == "3":
        restore_packages()
    elif choice == "q":
        print("종료.")
    else:
        print("잘못된 선택입니다.")


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--list":
            if check_device():
                list_packages()
        elif arg == "--clean":
            if check_device():
                clean_packages()
        elif arg == "--restore":
            if check_device():
                restore_packages()
        elif arg in ("--help", "-h"):
            print(__doc__)
        else:
            print(f"알 수 없는 옵션: {arg}")
            print("사용법: py boox_cleaner.py [--list|--clean|--restore]")
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
