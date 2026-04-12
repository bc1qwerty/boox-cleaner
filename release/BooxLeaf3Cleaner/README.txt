═══════════════════════════════════════════════════════
  Boox Leaf3 Cleaner v1.0
═══════════════════════════════════════════════════════

■ 테스트 기기 정보
  모델      : ONYX Boox Leaf3 (코드명 D60)
  펌웨어    : D60_SMT_V02_2022_0309
  Android   : 11 (API 30)
  플랫폼    : Qualcomm Bengal (qcom)
  보안패치  : 2024-02-01
  제조사    : ONYX

■ 테스트 환경
  OS        : Windows 11 Pro (10.0.26100)
  ADB       : platform-tools 36.0.2

■ 사용법
  1. Boox Leaf3의 USB 디버깅을 활성화합니다.
     - Activity Launcher 앱에서 Settings > DeviceInfoSettings 열기
     - 빌드 번호 7회 탭 → "You are now a developer" 확인
     - Settings > DevelopmentSettings > USB 디버깅 켜기
  2. USB 케이블로 PC에 연결합니다.
  3. 기기에서 "USB 디버깅 허용" 팝업이 뜨면 허용합니다.
  4. BooxLeaf3Cleaner.exe를 실행합니다.
  5. 제거할 앱을 선택하고 "선택 앱 제거" 버튼을 누릅니다.

■ 주의사항
  - 이 도구는 위 기기/펌웨어 조합에서만 테스트되었습니다.
  - 다른 Boox 모델이나 펌웨어에서는 패키지명이 다를 수 있습니다.
  - 제거 방식: pm uninstall -k --user 0 (사용자 레벨 제거)
  - 공장초기화(Factory Reset) 시 제거된 앱이 자동 복구됩니다.
  - 프로그램 내 "선택 앱 복구" 버튼으로도 복구 가능합니다.

■ 폴더 구조
  BooxLeaf3Cleaner/
  ├── BooxLeaf3Cleaner.exe    (메인 프로그램)
  ├── platform-tools/          (ADB 포함)
  │   ├── adb.exe
  │   ├── AdbWinApi.dll
  │   └── AdbWinUsbApi.dll
  └── README.txt               (이 파일)

■ 복구 방법 (수동)
  명령 프롬프트에서:
  platform-tools\adb.exe shell cmd package install-existing <패키지명>
