import flet as ft
import yt_dlp
import threading
import os
import requests

# --- CONFIGURATION (ඔයාගේ අලුත් Repository විස්තර මෙතනට දාන්න) ---
CURRENT_VERSION = "1.4"
# GitHub 'Raw' link එක මෙතනට දාන්න
VERSION_URL = "https://raw.githubusercontent.com/salithamihiranga01-art/Universal-Downloader-Mobile-/refs/heads/main/version.txt"
# APK එක ඩවුන්ලෝඩ් වෙන සෘජු Link එක (GitHub Release හෝ Main branch එකේ link එක)
APK_URL = "https://github.com/ඔයාගේ_USERNAME/ඔයාගේ_REPO_NAME/raw/main/UniversalDownloader.apk"

def main(page: ft.Page):
    page.title = f"Universal Downloader v{CURRENT_VERSION}"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 550
    page.window_height = 850
    page.scroll = "auto"
    page.padding = 30
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # --- UPDATE LOGIC ---
    def check_updates(e=None):
        try:
            response = requests.get(VERSION_URL, timeout=5)
            latest_version = response.text.strip()
            
            if latest_version != CURRENT_VERSION:
                def start_update(e):
                    page.launch_url(APK_URL) # Browser එක හරහා APK එක බාගත වේ
                    page.dialog.open = False
                    page.update()

                page.dialog = ft.AlertDialog(
                    title=ft.Text("New Update Available! 🚀"),
                    content=ft.Text(f"Version {latest_version} is now available.\nDo you want to download it now?"),
                    actions=[
                        ft.TextButton("Update Now", on_click=start_update),
                        ft.TextButton("Later", on_click=lambda _: setattr(page.dialog, "open", False) or page.update()),
                    ],
                )
                page.dialog.open = True
            elif e: # Button එකෙන් චෙක් කළොත් පමණක් පෙන්වන්න
                status_text.value = "You are up to date! ✅"
                status_text.color = "green"
            page.update()
        except:
            if e:
                status_text.value = "Update check failed! ❌"
                page.update()

    # --- UI CONTROLS ---
    def show_about(e):
        page.dialog = ft.AlertDialog(
            title=ft.Text("About App"),
            content=ft.Text(f"Universal Downloader v{CURRENT_VERSION}\nPowered by Salitha_M"),
        )
        page.dialog.open = True
        page.update()

    page.appbar = ft.AppBar(
        title=ft.Text("Universal Downloader"),
        center_title=True,
        bgcolor="#2b2b2b",
        actions=[
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(content=ft.Text("Check for Updates"), on_click=check_updates),
                    ft.PopupMenuItem(content=ft.Text("About"), on_click=show_about),
                ]
            ),
        ],
    )

    url_input = ft.TextField(label="Enter YouTube link here...", border_radius=10)
    
    # Android වලට ගැලපෙන path එක
    default_path = "/storage/emulated/0/Download" if page.platform == ft.PagePlatform.ANDROID else os.path.join(os.path.expanduser("~"), "Desktop")
    path_input = ft.TextField(label="Download Path", value=default_path, border_radius=10)
    
    quality_dropdown = ft.Dropdown(
        label="Video Quality",
        options=[ft.dropdown.Option("720p"), ft.dropdown.Option("1080p")],
        value="720p", width=200
    )
    audio_switch = ft.Switch(label="Audio Only (MP3)", value=False)
    
    pb = ft.ProgressBar(width=450, color="#3b8ed0", value=0, visible=False)
    progress_text = ft.Text("0%", visible=False)
    status_text = ft.Text("Ready", italic=True, color="#aaaaaa")
    speed_text = ft.Text("", size=11)
    size_text = ft.Text("", size=11)

    # --- DOWNLOAD LOGIC ---
    def progress_hook(d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%', '').strip()
            try:
                pb.value = float(p) / 100
                progress_text.value = f"Downloading: {int(float(p))}%"
                speed_text.value = f"Speed: {d.get('_speed_str', 'N/A')}"
                size_text.value = f"Size: {d.get('_total_bytes_str', 'N/A')}"
                page.update()
            except: pass
        elif d['status'] == 'finished':
            status_text.value = "Download Complete! ✅"
            status_text.color = "#4CAF50"
            page.update()

    def start_download(e):
        url = url_input.value.strip()
        if not url: return
        status_text.value = "Starting..."
        pb.visible, progress_text.visible = True, True
        page.update()

        def run_dl():
            quality = quality_dropdown.value.replace("p","")
            opts = {
                'format': 'bestaudio/best' if audio_switch.value else f'bestvideo[height<={quality}]+bestaudio/best',
                'progress_hooks': [progress_hook],
                'outtmpl': f"{path_input.value}/%(title)s.%(ext)s",
                'merge_output_format': 'mp4',
            }
            if audio_switch.value:
                opts['postprocessors'] = [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]
            try:
                with yt_dlp.YoutubeDL(opts) as ydl: ydl.download([url])
            except:
                status_text.value = "Error! Check connection."
                status_text.color = "red"
                page.update()

        threading.Thread(target=run_dl, daemon=True).start()

    # --- LAYOUT ---
    page.add(
        ft.Column([
            ft.Divider(height=10, color="transparent"),
            url_input,
            path_input,
            ft.Row([quality_dropdown, audio_switch], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=10, color="transparent"),
            ft.Row([
                ft.ElevatedButton("DOWNLOAD", on_click=start_download, bgcolor="#3b8ed0", color="white", width=180, height=50),
                ft.ElevatedButton("RESET", on_click=lambda _: page.go(page.route), bgcolor="#d32f2f", color="white", width=180, height=50),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Divider(height=20),
            status_text,
            pb,
            ft.Row([progress_text, speed_text, size_text], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=40),
            ft.Text("Powered by Salitha_M", italic=True, color="#555555")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
    
    # App එක ඕපන් වෙනකොටම update චෙක් කරනවා
    check_updates()

ft.app(target=main)
