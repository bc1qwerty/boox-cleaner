# Boox Leaf3 Cleaner

Boox Leaf3 블로트웨어 제거 도구 (GUI)

![Windows](https://img.shields.io/badge/Windows-11-blue) ![Python](https://img.shields.io/badge/Python-3.11+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 테스트 기기 정보

| 항목 | 값 |
|---|---|
| 모델 | ONYX Boox Leaf3 (코드명 D60) |
| 펌웨어 | D60_SMT_V02_2022_0309 |
| Android | 11 (API 30) |
| 플랫폼 | Qualcomm Bengal (qcom) |
| 보안패치 | 2024-02-01 |
| 제조사 | ONYX |

> **주의**: 이 도구는 위 기기/펌웨어 조합에서만 테스트되었습니다.
> 다른 Boox 모델이나 펌웨어에서는 패키지명이 다를 수 있습니다.

## 기능

- 34개 블로트웨어 카테고리별 분류 및 선택 제거
- 제거한 앱 원클릭 복구
- USB 기기 자동 감지 (3초 폴링)
- 실시간 작업 로그
- `com.onyx` (런처/코어), OTA 업데이트 보호

## 제거 대상

### Boox 블로트웨어
사전, 메일, 시계, Boox 스토어, 음악 플레이어, 갤러리, AI 어시스턴트, 녹음기, 앱마켓, 계산기, EasyTransfer, KSync, 프로덕션 테스트

### Boox 키보드 (Google 키보드 사용 시)
한글 키보드, 영문 키보드

### Boox 기타
플로팅 버튼, 내장 리더

### Android 불필요 앱
Chrome, 캘린더, 연락처, 검색, 인쇄, MMS/SMS, 배경화면, 스크린세이버 등

## 다운로드

[Releases](../../releases) 페이지에서 `BooxLeaf3Cleaner_v1.0.zip`을 다운로드하세요.

Python 설치 불필요 — exe + ADB가 포함되어 있습니다.

## 사용법

### 사전 준비: USB 디버깅 활성화

Boox Leaf3는 기본 설정에서 개발자 옵션 접근이 제한되어 있습니다.
**Activity Launcher** 앱을 설치하여 아래 순서로 진행하세요:

1. Boox 앱스토어 또는 Play 스토어에서 **Activity Launcher** 설치
2. Activity Launcher에서 **Settings** 앱의 하위 Activity 중 **DeviceInfoSettings** (또는 About 관련 항목) 실행
3. **빌드 번호** 7회 탭 → "You are now a developer" 확인
4. Activity Launcher에서 **DevelopmentSettings** 실행 → **USB 디버깅** 켜기

### 프로그램 실행

1. zip 압축 해제
2. USB 케이블로 PC에 연결
3. 기기에서 "USB 디버깅 허용" → 허용
4. `BooxLeaf3Cleaner.exe` 실행
5. 앱 선택 후 "선택 앱 제거" 클릭

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

## CLI 버전

GUI 없이 CLI로도 사용 가능합니다:

```bash
py boox_cleaner.py              # 대화형 모드
py boox_cleaner.py --list       # 제거 대상 목록
py boox_cleaner.py --clean      # 전체 제거
py boox_cleaner.py --restore    # 복구
```

## 폴더 구조

```
BooxLeaf3Cleaner/
├── BooxLeaf3Cleaner.exe     # GUI 프로그램
├── platform-tools/           # ADB 동봉
│   ├── adb.exe
│   ├── AdbWinApi.dll
│   └── AdbWinUsbApi.dll
└── README.txt                # 사용법
```

## License

MIT
