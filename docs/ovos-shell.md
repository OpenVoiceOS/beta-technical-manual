# OVOS Shell

!!! abstract "In a nutshell"
    `ovos-shell` is the old on-screen interface for OVOS. It is the full-screen app that draws the assistant's face, status, settings panel, and skill screens on devices with a display (like the Mark 2). It is the *legacy* GUI: deprecated, effectively broken today, and being replaced by a ground-up rework. This page is kept mainly for reference and for maintaining existing Mark 2 devices. See the [Glossary](glossary.md) for unfamiliar terms.

!!! danger "Maturity: Deprecated ⚠️ ⬤◯◯◯◯ — see [Screens on OVOS Today](gui-status.md) for the full picture"
    This component's repository is archived and no longer maintained. See the
    [Maturity Scale](maturity.md) and this page's own notes for what replaces it.
    `ovos-shell` is part of the legacy stack. There is no generally usable OVOS GUI,
    and a replacement is **Upcoming**.

[ovos-shell](https://github.com/OpenVoiceOS/ovos-shell) is the **legacy Qt5/[Kirigami](qt5-gui.md)
shell application** for OVOS on embedded and desktop devices (Mark 2, Raspberry Pi with
touchscreen, laptop). It wraps the `mycroft-gui-qt5` library (`Mycroft 1.0` [QML](qt5-gui.md) module)
inside a full-screen, frameless Kirigami application window.

It is distinct from the standalone `mycroft-gui-qt5` developer app. `ovos-shell` provides
the production UI chrome (status indicator, sliding quick-settings panel, notifications,
OSD, splash screen, pairing/OAuth loaders, and shutdown dialog), while it delegates all skill
rendering to `Mycroft.SkillView`. A homescreen skill supplies the idle screen itself
(see [Home Screen](homescreen.md)), not the shell.

> **Voice First.** The visual interface is always secondary to the voice interface.
> All interactions should be completable with voice alone. Touchscreen controls supplement
> but never replace voice.

---

## Architecture

```bash
ovos-shell/
├── application/             ← Main executable (ovos-shell binary)
│   ├── main.cpp             ← QApplication entry point
│   ├── plugins/             ← EnvironmentSummary, ResetOperations
│   ├── qml/                 ← Shell QML
│   │   ├── main.qml             ← Root window (Kirigami.AbstractApplicationWindow)
│   │   ├── panel/               ← Sliding quick-settings panel (+ quicksettings/)
│   │   ├── osd/                 ← On-screen display (volume, etc.)
│   │   ├── StatusIndicator.qml, ListenerAnimation.qml
│   │   ├── SplashScreen.qml, ShutdownOptions.qml, ServiceWatcher.qml
│   │   ├── NotificationsSystem.qml, NotificationPop*.qml
│   │   ├── OAuthLoader.qml, OAuthQrCodeLoader.qml, PairingArea.qml
│   │   └── Keyboard.qml, FactoryResetUI.qml, KdeConnect.qml
├── lib/                     ← OVOSPlugin 1.0 QML module (Configuration, PlacesModel)
├── theme/                   ← OVOS Kirigami theme plugin (KF5 ≥ 5.91)
├── theme-legacy/            ← OVOS Kirigami theme plugin (KF5 < 5.91)
└── schemes/                 ← Colour scheme files

```

### Dependencies

| Dependency | Role |
|---|---|
| `mycroft-gui-qt5` | `Mycroft 1.0` QML module: `SkillView`, `MycroftController`, system templates |
| Qt5 (≥ 5.12) | Core, Quick, WebView, Widgets, DBus |
| KF5 Kirigami2 | Application window, theme, layouts |
| KF5 DBusAddons | D-Bus service registration |
| KF5 Config / ConfigWidgets | Settings persistence |

`ovos-shell` does not bundle skill-page QML itself. The `Mycroft.SkillView` runtime from
`mycroft-gui-qt5` resolves skill pages and the built-in `SYSTEM_*` pages.

---

## Component Responsibilities

### `main.qml`

- Root `Kirigami.AbstractApplicationWindow`: full screen, frameless


- Monitors `Mycroft.MycroftController.status` to restart GUI/skill service watchers


- Embeds `Mycroft.SkillView` for skill rendering


- Hosts `StatusIndicator`, `ListenerAnimation`, `SlidingPanel`, notification popups, OSD


- When the skill stack is empty, the shell shows a plain background image. A homescreen skill
  draws the actual idle screen, rendered through `Mycroft.SkillView`:

```qml
Image {
    source: "background.png"
    fillMode: Image.PreserveAspectFit
    anchors.fill: parent
    opacity: !mainView.currentItem && serviceWatcher.guiServiceAlive
}

```

### `Mycroft.SkillView` (from `mycroft-gui-qt5`)

- Displays the active namespace stack


- Loads QML pages from the resolved `url` paths `ovos-gui` sends, falling back to local resolution by `namespace`/`page` name when `url` is unresolved


- Manages namespace transitions and animations

### `SlidingPanel` / `QuickSettings`

- Swipe-up panel with mute, volume, brightness, wireless, reboot, shutdown controls


- Uses `OVOSPlugin.Configuration` for reading current device state

### `StatusIndicator` / `ListenerAnimation`

- `StatusIndicator` reacts to `ovos.wifi.setup.started` / `ovos.wifi.setup.completed` /
  `ovos.shell.status.ok` to show pairing/Wi-Fi setup and general status.


- `ListenerAnimation` drives the listening animation, reacting to
  `recognizer_loop:wakeword` (show) and `mycroft.mic.listen` (show). The QML also
  has cases for `recognizer_loop:record_end` (hide) and `mycroft.speech.recognition.unknown`
  (hide), but ovos-gui forwards those two events under their spec names
  (`ovos.listener.record.ended`, `ovos.speech.recognition.unknown`) rather than the
  legacy strings the QML switches on, so neither branch currently fires. The
  component is embedded once, persistently, and writes `visible` in no other
  place, so as shipped it has no verified way to hide once shown (tracked
  upstream by the unmerged `fix/listener-animation-spec-events` branch).

---

## Homescreen (Idle Screen)

The shell does not draw the idle screen itself. When the namespace stack is empty it shows
a plain background image. A skill (default `ovos-skill-homescreen.openvoiceos`) provides the
actual homescreen, and its resting-screen page renders through
`Mycroft.SkillView`. Skills register idle screens with `@resting_screen_handler`. See
[Home Screen](homescreen.md) for the configuration and the resting-screen API.

!!! warning "Upcoming — unreleased"
    The GUI rework (specified by the
    [OVOS-GUI-1](https://github.com/OpenVoiceOS/architecture/blob/dev/gui-1.md) spec)
    moves homescreen data coordination into a `HomescreenManager` inside
    `ovos-legacy-mycroft-gui-plugin`, which subscribes to datetime, weather, wallpaper,
    notification, app, example, connectivity, and widget sources and re-emits them as
    `homescreen.data.*` / `homescreen.widget.*` bus messages for a client to render. This
    is **not** in any released shell and the shell itself contains no `homescreen/` QML on
    `master`. The resting-screen skill API (`@resting_screen_handler`, `idle_display_skill`)
    remains the supported mechanism on released OVOS. A Qt6 client successor is in development.

---

## Configuration

### Theme / Color (`OvosTheme` KConfig)

The `OVOSPlugin.Configuration` QML singleton reads and writes `~/.config/OvosTheme`
(standard KConfig format).

!!! tip "Start here"
    Most users only ever touch the `[ColorScheme]` group (`primaryColor`, `secondaryColor`,
    `textColor`, and `themeStyle`) either directly in this file or through the quick-settings
    panel. The `[SelectedScheme]` keys are managed automatically and rarely need to be edited
    by hand.

```ini
[ColorScheme]
primaryColor=#313131
secondaryColor=#F70D1A
textColor=#F1F1F1
themeStyle=dark

[SelectedScheme]
name=default
path=/usr/share/OVOS/ColorSchemes/default.json

```

| Group | Key | Default | Description |
|---|---|---|---|
| `ColorScheme` | `primaryColor` | `#313131` | Primary UI background color (ARGB hex) |
| `ColorScheme` | `secondaryColor` | `#F70D1A` | Accent color (OVOS red) |
| `ColorScheme` | `textColor` | `#F1F1F1` | Primary text color |
| `ColorScheme` | `themeStyle` | `dark` | Kirigami theme style: `dark` or `light` |
| `SelectedScheme` | `name` | `default` | Display name of the active color scheme |
| `SelectedScheme` | `path` | `default` | Filesystem path to the active scheme's `.json` file |

When individual colors are set via the quick-settings panel, `SelectedScheme` is set to
`name=custom`, `path=custom`.

### Color Scheme Files

Scheme `.json` files are loaded from (in priority order):

1. `/usr/local/share/OVOS/ColorSchemes/*.json`


2. `/usr/share/OVOS/ColorSchemes/*.json`


3. `$XDG_DATA_HOME/OVOS/ColorSchemes/` (typically `~/.local/share/OVOS/ColorSchemes/`)

Minimum required keys:

```json
{
  "name": "My Scheme",
  "primaryColor": "#FF1a1a2e",
  "secondaryColor": "#FFe94560",
  "textColor": "#FFffffff"
}

```

Colors must include an alpha prefix (e.g. `FF` for fully opaque).

The `Configuration` class watches all three directories with `QFileSystemWatcher` and
emits `schemeListChanged()` when files are added or removed.

The `Configuration` QML singleton (`OVOSPlugin.Configuration`) is implemented in
`lib/configuration.cpp` and exposes these read/write properties to QML.

---

## GUI Screenshots

Display settings panel:

![Animated demo of the ovos-shell display settings panel](https://github.com/OpenVoiceOS/ovos_assets/raw/master/Images/shell_settings.gif)

Color theme editor:

![Animated demo of the ovos-shell color theme editor](https://github.com/OpenVoiceOS/ovos_assets/raw/master/Images/shell_theme.gif)

*(Both GIFs are hosted in the [OpenVoiceOS/ovos_assets](https://github.com/OpenVoiceOS/ovos_assets) repo and verified reachable.)*

---

## Companion Plugins

To enable full functionality, configure `ovos-gui-plugin-shell-companion` in
`mycroft.conf`. This plugin integrates with `ovos-gui` to provide:

- Color scheme manager


- Notification widgets


- Configuration provider (settings UI)


- Brightness control (night mode, etc.)

```json
{
  "gui": {
    "extension": "ovos-gui-plugin-shell-companion"
  }
}

```

`ovos-shell` is tightly coupled to [PHAL](phal.md). The following PHAL plugins
should also be installed for a fully functional shell:

- `ovos-PHAL-plugin-network-manager`


- `ovos-PHAL-plugin-alsa`


- `ovos-PHAL-plugin-system`

!!! note "Some companion repos are archived"
    `ovos-gui-plugin-shell-companion`, `ovos-PHAL-plugin-gui-network-client`, and
    `ovos-PHAL-plugin-wifi-setup` are **archived** repositories. They may still work on an
    existing Mark 2 install, but treat them as unmaintained rather than as an install
    recommendation for new setups.

---

## Building

```bash
mkdir build && cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/usr
make -j$(nproc)
sudo make install

```

The `Mycroft 1.0` QML module (from `mycroft-gui-qt5`) must be installed before building
`ovos-shell`.

---

## Qt Version Policy

This repository targets **Qt5** and links against `mycroft-gui-qt5`. Do not introduce
Qt6-only API into this repository. A `mycroft-gui-qt6` client is developed as its own
project (see the [GUI Adapter Plugins](gui-adapters.md) rework) rather than as a fork of
`ovos-shell` itself.

---
**Read next:** [Qt5 GUI](qt5-gui.md)
**Related:** [GUI Protocol](gui-protocol.md) · [Home Screen](homescreen.md)
