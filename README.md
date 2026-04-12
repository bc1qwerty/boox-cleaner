# Boox Cleaner

Boox E-ink 기기 블로트웨어 제거 도구 (GUI)

기기를 자동 감지하여 모델별 제거 대상을 표시합니다.

![Windows](https://img.shields.io/badge/Windows-11-blue) ![Python](https://img.shields.io/badge/Python-3.11+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 지원 기기

| 항목 | Boox Leaf3 | Boox Palma2 Pro |
|---|---|---|
| 코드명 | D60 | Palma2_Pro_C |
| 펌웨어 | D60_SMT_V02_2022_0309 | 4.1.1-rel (2025-12-27) |
| Android | 11 (API 30) | 15 (API 35) |
| 플랫폼 | Qualcomm Bengal | Qualcomm Lito |
| 보안패치 | 2024-02-01 | 2025-10-01 |

> **주의**: 이 도구는 위 기기/펌웨어 조합에서만 테스트되었습니다.
> 다른 Boox 모델도 연결 시 공통 패키지가 표시되지만, 패키지명이 다를 수 있습니다.

## 기능

- 기기 자동 감지 — USB 연결 시 모델을 자동 인식하여 맞춤 목록 표시
- 블로트웨어 카테고리별 분류 및 선택 제거/복구
- USB 연결 상태 실시간 모니터링 (3초 폴링)
- 실시간 작업 로그
- `com.onyx` (런처/코어), OTA 업데이트 보호

## 제거 대상

### 공통 (모든 Boox 기기)

**Boox 블로트웨어** — 사전, 메일, 시계, Boox 스토어, 음악 플레이어, 갤러리, AI 어시스턴트, 녹음기, 앱마켓, 계산기, EasyTransfer, KSync, 프로덕션 테스트

**Boox 키보드** — 한글 키보드, 영문 키보드 (Google 키보드 사용 시)

**Boox 기타** — 플로팅 버튼, 내장 리더

**Android 불필요 앱** — Chrome, 캘린더, 연락처, 검색, 인쇄, MMS/SMS, 배경화면, 스크린세이버 등

### Palma2 Pro 추가

노트, TS 캘리브레이션, 카메라(SnapCam), 다이얼러, 연락처 앱, 문자/MMS, SIM 툴킷, Google Books, Google TTS, 긴급 정보, 저장공간 관리, 소리 선택기

## 다운로드

[Releases](../../releases) 페이지에서 최신 zip을 다운로드하세요.

Python 설치 불필요 — exe + ADB가 포함되어 있습니다.

## 사용법

### 사전 준비: USB 디버깅 활성화

Boox 기기는 일반적인 Android와 달리, 설정 > 기기 정보 > 빌드 번호 7회 탭으로 개발자 옵션을 활성화할 수 없는 경우가 있습니다.
이 경우 **Activity Launcher** 앱을 이용해 접근합니다:

1. Google Play 스토어 또는 Boox 앱스토어에서 **Activity Launcher** 설치
2. Activity Launcher 실행 → **"Settings"** 검색 → 하위 Activity 목록 펼치기
3. **"DeviceInfoSettings"** 또는 **"About"** 이 포함된 Activity 실행
4. **빌드 번호(Build Number)** 7회 탭 → "You are now a developer!" 확인
5. Activity Launcher에서 **"DevelopmentSettings"** 실행 → **USB 디버깅** 켜기
6. USB 케이블로 PC 연결 → "USB 디버깅 허용" 팝업 → **허용**

### 프로그램 실행

1. zip 압축 해제
2. USB 케이블로 PC에 연결 (USB 디버깅 활성화 상태)
3. `BooxCleaner.exe` 실행 — 기기가 자동 감지됨
4. 앱 선택 후 "선택 앱 제거" 클릭

### 복구

- 프로그램 내 "선택 앱 복구" 버튼 사용
- 또는 공장초기화 시 자동 복구됨
- 수동: `adb shell cmd package install-existing <패키지명>`

## 제거 방식

```
adb shell pm uninstall -k --user 0 <패키지명>
```

사용자 레벨에서만 제거되며, 시스템 파티션은 건드리지 않습니다.
공장초기화(Factory Reset) 시 모든 앱이 자동 복구됩니다.

## 폴더 구조

```
BooxCleaner/
├── BooxCleaner.exe          # GUI 프로그램
├── platform-tools/           # ADB 동봉
│   ├── adb.exe
│   ├── AdbWinApi.dll
│   └── AdbWinUsbApi.dll
└── README.txt                # 사용법
```

## License

MIT
