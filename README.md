# Boox Cleaner

Bloatware removal GUI for Boox E Ink devices.

The tool auto-detects the connected device and shows a per-model removal list.

![Windows](https://img.shields.io/badge/Windows-11-blue) ![Python](https://img.shields.io/badge/Python-3.11+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## Supported Devices

| Field | Boox Leaf3 | Boox Palma2 Pro |
|---|---|---|
| Codename | D60 | Palma2_Pro_C |
| Firmware | D60_SMT_V02_2022_0309 | 4.1.1-rel (2025-12-27) |
| Android | 11 (API 30) | 15 (API 35) |
| Platform | Qualcomm Bengal | Qualcomm Lito |
| Security patch | 2024-02-01 | 2025-10-01 |

> **Note**: This tool was validated against the device/firmware combinations above. Other Boox models will still show the shared package list when connected, but package names may differ.

## Features

- Automatic device detection — model is recognized instantly when the device is connected
- Bloatware grouped into categories with per-item selection, removal, and restore
- Live USB connection monitoring (3-second polling)
- Real-time action log
- Built-in protection for `com.onyx` (launcher / core) and the OTA updater

## Removal Targets

### Shared (all Boox devices)

**Boox bloatware** — Mail, Clock, Boox Store, Music Player, Gallery, AI Assistant, Voice Recorder, App Market, Calculator, EasyTransfer, KSync, production test

**Boox keyboards** — Korean keyboard, English keyboard (useful to remove when using Gboard)

**Boox misc** — Floating button, built-in reader

**Android unnecessary apps** — Chrome, Calendar, Contacts, Search, Print, MMS/SMS, Wallpaper, Screensaver, and more

### Palma2 Pro extras

Notes, TS calibration, Camera (SnapCam), Dialer, Contacts app, Messaging / MMS, SIM Toolkit, Google Books, Google TTS, Emergency info, Storage manager, Sound picker

## Download

Grab the latest zip from the [Releases](../../releases) page.

No Python required — the exe and ADB binaries are bundled.

## Usage

### Prerequisite: Enable USB Debugging

Boox devices don't always expose the standard "tap Build number 7 times" flow, so you may need to use **Activity Launcher** to reach the hidden screens:

1. Install **Activity Launcher** from Google Play or the Boox App Market
2. Open Activity Launcher → search for **"Settings"** → expand the sub-activity list
3. Launch the activity that includes **"DeviceInfoSettings"** or **"About"**
4. Tap **Build number** seven times → confirm "You are now a developer!"
5. Back in Activity Launcher, launch **"DevelopmentSettings"** → enable **USB debugging**
6. Connect via USB → tap **Allow** on the "Allow USB debugging?" dialog

### Running the Program

1. Extract the zip
2. Connect the device via USB with USB debugging enabled
3. Launch `BooxCleaner.exe` — the device is auto-detected
4. Select apps and click **Remove Selected**

### Restoring

- Use the **Restore Selected** button inside the program
- A factory reset also restores everything automatically
- Manual: `adb shell cmd package install-existing <package>`

## Removal Method

```
adb shell pm uninstall -k --user 0 <package>
```

This operates at the user level and never touches the system partition. A factory reset restores every removed package automatically.

## Folder Layout

```
BooxCleaner/
├── BooxCleaner.exe          # GUI executable
├── platform-tools/          # Bundled ADB
│   ├── adb.exe
│   ├── AdbWinApi.dll
│   └── AdbWinUsbApi.dll
└── README.txt               # Quick reference
```

## Safety Principles

The v2.2 release carries a hard-won lesson. In v2.1, removing `com.onyx.kreader` caused `com.onyx` (ContentBrowser) to throw a `SecurityException` from `FilesChangedReceiverAction`, which cascaded into a `system_server` binder failure and put the device into a recovery-mode boot loop.

Static analysis of `kcb.apk` (dex string dump cross-checked against `dumpsys package providers`) confirmed three packages that `com.onyx` hard-depends on through ContentProviders. These are now guarded in `KEEP_PACKAGES` and will never appear in the removal list:

| Package | Provided ContentProviders |
|---|---|
| `com.onyx.kreader` | `com.onyx.content.database.ContentProvider`, `kreader.note.provider`, `kreader.statistics.provider`, `kreader.feature_list.ContentProvider`, `account.database.ContentProvider` |
| `com.onyx.android.ksync` | `cloudstorage.ContentProvider`, `group.ContentProvider`, `KReaderRecordContentProvider`, `KSyncRecordContentProvider` + six KSync/KNote services |
| `com.onyx.dict` | `com.onyx.dict.DictionaryProvider`, `OnyxNewWordProvider` |

General principles:

- Every action runs at the user level (`--user 0`)
- Launcher and core packages are guarded by `KEEP_PACKAGES`
- Every change reverts automatically on factory reset
- New device support must cross-check ContentProvider ownership before adding packages

## License

MIT
