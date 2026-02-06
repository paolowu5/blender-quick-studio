# Blender Add-ons

Professional workflow tools for Blender artists.

---

## Quick Studio Setup

**One-click professional studio lighting and camera system.**

Create complete studio environments instantly with properly configured 4-point lighting, camera controls, and render-ready settings.

### Features

| Feature | Description |
|---------|-------------|
| **4-Point Lighting** | Key, Fill, Rim, and Back lights with industry-standard positioning |
| **Camera System** | Lock to view, focal length, DOF controls, tracking targets |
| **Light Controls** | Independent energy, size, and color for each light |
| **Target System** | Point lights and camera at specific scene objects |
| **Background Control** | Color picker or transparent render option |
| **Non-Destructive** | Organized in dedicated collection, fully adjustable |

### Installation

```
Edit > Preferences > Add-ons > Install > Select quickstudio_addon.py > Enable
```

### Usage

1. Open the sidebar in 3D Viewport (`N`)
2. Navigate to **QuickStudio** tab
3. Click **CREATE STUDIO**
4. Adjust settings via the panel controls

### Requirements

- Blender 3.0+
- No external dependencies

---

## Camera From View

**Instant camera creation from viewport perspective.**

Transform your current view into a perfectly aligned camera with a single keystroke.

### Features

| Feature | Description |
|---------|-------------|
| **Viewport Matching** | Exact position, rotation, and perspective capture |
| **Auto Naming** | Sequential naming convention (CAM_001, CAM_002, etc.) |
| **Active Camera** | Automatically set as scene camera |
| **Immediate Selection** | Camera selected for instant parameter access |

### Installation

```
Edit > Preferences > Add-ons > Install > Select camerafromview_addon.py > Enable
```

### Usage

**Keyboard Shortcut**
```
Ctrl + Alt + Shift + C
```

**Menu Access**
```
View3D > Add > Camera > Camera From View
```

### Requirements

- Blender 3.3+
- No external dependencies

---

## Technical Specifications

| Add-on | Version | Size | Performance Impact |
|--------|---------|------|-------------------|
| Quick Studio Setup | 1.0 | ~15KB | Minimal |
| Camera From View | 1.0 | ~3KB | None |

Both add-ons use standard Blender APIs with no external dependencies.

---

## License

These add-ons are released as **free and open source** for personal and commercial use.

- Redistribution permitted with attribution
- Modification permitted
- No warranty provided

---

## Changelog

### Quick Studio Setup v1.0
- Initial release
- 4-point lighting system with driver-based controls
- Camera tracking and DOF systems
- Background color and transparency controls

### Camera From View v1.0
- Initial release
- One-click camera creation from viewport
- Automatic sequential naming
- Keyboard shortcut integration
