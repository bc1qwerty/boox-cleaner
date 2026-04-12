═══════════════════════════════════════════════════════
  Boox Cleaner v2.0
═══════════════════════════════════════════════════════

■ 지원 기기

  [1] Boox Leaf3
      코드명    : D60
      펌웨어    : D60_SMT_V02_2022_0309
      Android   : 11 (API 30)
      플랫폼    : Qualcomm Bengal
      보안패치  : 2024-02-01

  [2] Boox Palma2 Pro
      코드명    : Palma2_Pro_C
      펌웨어    : 4.1.1-rel (2025-12-27)
      Android   : 15 (API 35)
      플랫폼    : Qualcomm Lito
      보안패치  : 2025-10-01

  * 다른 Boox 모델도 연결 시 공통 패키지가 표시됩니다.

■ 사용법
  1. USB 디버깅을 활성화합니다.
     - Google Play 스토어에서 Activity Launcher 설치
     - Activity Launcher > Settings > DeviceInfoSettings 실행
     - 빌드 번호 7회 탭 → "You are now a developer!" 확인
     - Activity Launcher > Settings > DevelopmentSettings > USB 디버깅 켜기
  2. USB 케이블로 PC에 연결합니다.
  3. 기기에서 "USB 디버깅 허용" 팝업이 뜨면 허용합니다.
  4. BooxCleaner.exe를 실행합니다.
  5. 기기가 자동 감지되면 제거할 앱을 선택하고 "선택 앱 제거" 클릭.

■ 주의사항
  - 위 기기/펌웨어 조합에서만 테스트되었습니다.
  - 제거 방식: pm uninstall -k --user 0 (사용자 레벨 제거)
  - 공장초기화(Factory Reset) 시 제거된 앱이 자동 복구됩니다.
  - 프로그램 내 "선택 앱 복구" 버튼으로도 복구 가능합니다.

■ 폴더 구조
  BooxCleaner/
  ├── BooxCleaner.exe           (메인 프로그램)
  ├── platform-tools/            (ADB 포함)
  │   ├── adb.exe
  │   ├── AdbWinApi.dll
  │   └── AdbWinUsbApi.dll
  └── README.txt                 (이 파일)

■ 복구 방법 (수동)
  명령 프롬프트에서:
  platform-tools\adb.exe shell cmd package install-existing <패키지명>
