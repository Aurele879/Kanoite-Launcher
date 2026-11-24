## 🔶 Kanoite Launcher : _Formerly Astro Launcher 2_

<p align="center">
  <img src="app/assets/logo.png" alt="Kanoite Launcher Logo" width="180" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Minecraft-Any%20Version-blue?style=for-the-badge&logo=minecraft&logoColor=white" alt="Minecraft Version" />
  <img src="https://img.shields.io/badge/Status-In%20Development-success?style=for-the-badge" alt="Status" />
</p>

## 📖 Overview
A minecraft launcher written in python. It can run any version of the game, whether vanilla or modded.
The software is made to separate profiles made by the player. To make it simple, when you want to launch the game, you first need to create a profile with a name and a version. When this is done, you can launch it and all files will be isolated from your others profiles. If you use different texture packs or mods in different versions, every world is only accessible from the profile you used to create it.
### Features
| Feature | Implementation |
| :--- | :--- |
| **GUI** | ✅ |
| **Microsoft Authentication** | ✅ |
| **Profiles** | ✅ |
| **Customizable settings** | ✅ |
| **Discord Rich Presence** | ✅ |
| **Runtime Data Isolation** | ✅ |
#### Login page
<img src="docs/preview/login_preview.png"></img>
#### Main Page
<img src="docs/preview/main_preview.png"></img>
#### Loading animation
<img src="docs/preview/loading_preview.png"></img>
#### Settings page
<img src="docs/preview/settings_preview.png"></img>
#### Profile Managment pages
<img src="docs/preview/pc_preview.png"></img>
<img src="docs/preview/pe_preview.png"></img>

## 📜 Versions History
0.1, 0.2, and 0.3 : Added the profiling system

1.0 : Fixed bugs, added downloading label

1.1 : First refactoring, fixed bugs, GUI improvements

1.2 : Added RAM selection options, fixed bugs

1.3 : Total refactor to separate jobs

2.0 / 2.1 : Added turnkey official Microsoft account authentication (OAuth2 Device Code Flow, token refresh, Xbox Live & Minecraft Services integration)

## ⚙️ Installation & Usage
1. Install dependencies:
   ```bash
   pip install customtkinter minecraft-launcher-lib requests Pillow pypresence
   ```
2. Run the launcher:
   ```bash
   python app/main.py
   ```
3. Click **"SIGN IN WITH MICROSOFT"**, validate the displayed code on the Microsoft page, and start playing!
