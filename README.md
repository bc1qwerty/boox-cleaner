# Boox Cleaner (v2.3)

Onyx Boox E-ink 기기 전용 블로트웨어 제거 및 **시스템 가속 최적화** 도구입니다.

![Windows](https://img.shields.io/badge/Windows-11-blue) ![Python](https://img.shields.io/badge/Python-3.13-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ v2.3 업데이트 하이라이트

이번 버전은 단순한 앱 제거를 넘어 **E-ink 기기의 실제 반응 속도**를 높이는 데 집중했습니다.

- **🚀 시스템 가속 기능**:
  - **애니메이션 제거 (0.0x)**: 창 전환 및 팝업 애니메이션을 완전히 꺼서 잔상을 줄이고 반응 속도를 즉각적으로 만듭니다.
  - **로그 버퍼 확장 (16M)**: 시스템 로그 기록으로 인한 CPU 병목 현상을 방지하여 전반적인 시스템 지연을 줄입니다.
- **📱 Palma 2 Pro 완벽 지원**:
  - 최신 펌웨어(Android 13-15) 대응 및 Palma 전용 블로트웨어(카메라, 통신 관련 앱 등) 목록 보강.
- **🛡 안전성 강화 (Hard-Skip)**:
  - `com.onyx.kreader`, `com.onyx.android.ksync`, `com.onyx.dict` 등 시스템 핵심 패키지에 대한 **삭제 강제 차단** 로직이 추가되었습니다. 이제 실수로 해당 항목을 체크하더라도 프로그램이 자동으로 건너뜁니다.

## 📱 지원 기기

- **Boox Palma 1 / 2 Pro** (전 모델 지원)
- **Boox Leaf3 / Page**
- **Boox Poke / Note / Max** 시리즈 (안드로이드 기반 전 모델)

## 🛠 사용 방법

### 1. USB 디버깅 활성화
- 기기 **설정 > 단말기 정보 > 빌드 번호**를 7번 연타하여 개발자 옵션을 켭니다.
- **설정 > 개발자 옵션 > USB 디버깅**을 활성화합니다.

### 2. 프로그램 실행 및 최적화
- `BooxCleaner.exe`를 실행합니다.
- **성능(Performance) 탭**: '창 애니메이션 끄기', '로그 버퍼 확장' 등을 체크하고 **적용(Apply)**을 누릅니다.
- **앱(Apps) 탭**: 제거할 블로트웨어를 선택하고 **선택 항목 제거(Remove Selected)**를 누릅니다.

## 🆘 복구 방법 (크래시 발생 시)

이전 버전(v2.2 이하)을 사용하여 `kreader` 등이 삭제되어 부팅 루프가 발생한 경우, ADB가 연결된 상태에서 다음 명령어를 입력하세요:

```bash
adb shell cmd package install-existing --user 0 com.onyx.kreader
adb shell cmd package install-existing --user 0 com.onyx.android.ksync
adb shell cmd package install-existing --user 0 com.onyx.dict
adb reboot
```

## ⚖ License
MIT License. 본 도구는 사용자 레벨(`--user 0`)에서만 작동하며, 공장 초기화 시 모든 변경 사항이 복구됩니다.

---

# Boox Cleaner (v2.3) - English

Bloatware removal and **System Optimization** tool for Onyx Boox E-ink devices.

## ✨ v2.3 Highlights
- **🚀 System Acceleration**: Disable animations (0.0x) and expand log buffer (16M) for better E-ink responsiveness.
- **📱 Palma 2 Pro Support**: Full support for Android 13-15 and Palma-specific apps.
- **🛡 Safety Enhancement**: Hard-skip logic added for critical packages (`kreader`, `ksync`, `dict`) to prevent boot loops.
