# Boox Cleaner (v2.3)

Bloatware removal GUI for Boox E Ink devices, now with **System Optimization**.

The tool auto-detects the connected device and shows a per-model removal list.

![Windows](https://img.shields.io/badge/Windows-11-blue) ![Python](https://img.shields.io/badge/Python-3.11+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 📱 Supported Devices

| Field | Boox Leaf3 | Boox Palma2 Pro |
|---|---|---|
| Codename | D60 | Palma2_Pro_C |
| Firmware | D60_SMT_V02_2022_0309 | 4.1.1-rel (2025-12-27) |
| Android | 11 (API 30) | 13-15 (API 33-35) |
| Platform | Qualcomm Bengal | Qualcomm Lito |
| Security patch | 2024-02-01 | 2025-10-01 |

> **Note**: This tool was validated against the device/firmware combinations above. Other Boox models (including Palma, Poke, Max Series) are also supported.

## ✨ New in v2.3: System Optimization

Beyond removing apps, v2.3 introduces **System Speed-up** features specifically for E Ink:

- **Animation Removal (0.0x)**: Disables window/transition animations to eliminate ghosting and make UI interactions feel instant.
- **Log Buffer Expansion (16M)**: Expands the system log buffer to prevent CPU bottlenecks caused by constant logcat writing.
- **Improved Palma 2 Pro Support**: Added SnapCam, Dialer, and SIM Toolkit to the removal list for cellular-enabled models.

## 🚀 Features

- **Automatic device detection** — model is recognized instantly when the device is connected
- **System Acceleration** — One-click optimization for animations and logging
- **Bloatware grouped into categories** with per-item selection, removal, and restore
- **Live USB connection monitoring** (3-second polling)
- **Real-time action log**
- **Built-in protection** for `com.onyx` (launcher / core) and the OTA updater

## 🛠 Usage

### Prerequisite: Enable USB Debugging

1. Go to **Settings** > **About Device**.
2. Tap **Build number** 7 times to enable Developer Options.
3. Go to **Settings** > **Developer Options** and enable **USB debugging**.

### Running the Program

1. Extract the zip.
2. Launch `BooxCleaner.exe`.
3. Go to the **Performance** tab to apply System Optimization.
4. Go to the **Apps** tab to select and remove bloatware.

## Removal Method

```bash
adb shell pm uninstall -k --user 0 <package>
```

This operates at the user level and never touches the system partition. A factory reset restores every removed package automatically.

## License

MIT
