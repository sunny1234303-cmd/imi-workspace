# Local Checklist Popup

A minimal Chrome extension that adds a floating button to every browser tab.  
Click it to open your locally-running web app as a popup — without switching tabs.

![Chrome MV3](https://img.shields.io/badge/Chrome-MV3-4285F4?logo=googlechrome&logoColor=white)

---

## What it does

- Injects a small ● button in the bottom-right corner of every page
- Click → your local app opens as a floating popup (800 × 620 px)
- Click outside or press `Esc` to close
- The target URL is configurable — works with any localhost app

---

## Install

1. Clone or download this folder
2. Open Chrome and go to `chrome://extensions`
3. Enable **Developer mode** (top-right toggle)
4. Click **Load unpacked** and select this folder

The button appears immediately on all tabs.

---

## Configure

Right-click the extension icon in the toolbar → **Options**,  
or go to `chrome://extensions` → Details → Extension options.

Set your server URL (default: `http://localhost:3737`).

---

## Icons

Add your own PNG files to the `icons/` folder:

```
icons/icon16.png   — 16 × 16 px
icons/icon48.png   — 48 × 48 px
icons/icon128.png  — 128 × 128 px
```

---

## Use case

Designed for personal productivity tools (checklists, dashboards, note apps)  
running on localhost — accessible from any tab without breaking your flow.

---

## License

MIT
