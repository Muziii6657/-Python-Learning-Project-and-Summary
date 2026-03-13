import os
import time
import threading
import json
import webbrowser  # 新增：用于打开浏览器网页
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pynput import keyboard
import pygame
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item

# 设置外观
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class MaNongApp:
    def __init__(self, root):
        self.root = root
        self.root.title("码农 (Coding On Track)")
        self.root.geometry("700x450") # 稍微调宽一点点，容纳新按钮
        self.root.resizable(False, False)

        # 设置窗口左上角图标
        try:
            self.root.iconbitmap("logo.ico")
        except Exception as e:
            print(f"窗口图标加载失败: {e}")

        # 核心逻辑变量
        self.playlist_dir = ""
        self.playlist = []
        self.current_index = 0
        self.last_type_time = 0
        self.is_playing = False
        self.is_paused = False
        self.running = True

        pygame.mixer.init()

        self.build_ui()
        self.start_background_tasks()

        # 绑定关闭窗口事件为“彻底退出程序”
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        # 启动托盘图标线程
        self.create_tray_icon()

        # 全局记忆功能加载
        self.load_settings()

    def save_settings(self, path):
        try:
            with open("config.txt", "w", encoding="utf-8") as f:
                f.write(path)
        except:
            pass

    def load_settings(self):
        if os.path.exists("config.txt"):
            try:
                with open("config.txt", "r", encoding="utf-8") as f:
                    path = f.read().strip()
                    if os.path.exists(path):
                        self.playlist_dir = path
                        self.lbl_folder.configure(text=os.path.basename(path))
                        self.root.after(500, self.load_playlist)
            except:
                pass

    def open_download_site(self):
        """新增：跳转到音乐下载网站"""
        webbrowser.open("https://www.gequhai.com/")

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="选择包含 MP3 的文件夹")
        if folder_path:
            self.playlist_dir = folder_path
            self.lbl_folder.configure(text=os.path.basename(folder_path))
            self.save_settings(folder_path)  # 选完自动保存
            self.load_playlist()

    def build_ui(self):
        """构建 UI"""
        # --- 顶部区域 ---
        self.frame_top = ctk.CTkFrame(self.root, fg_color="transparent")
        self.frame_top.pack(fill="x", pady=(40, 20), padx=40)

        # 选择文件夹按钮
        self.btn_folder = ctk.CTkButton(self.frame_top, text="📁 选择歌单文件夹", command=self.select_folder,
                                        font=("Microsoft YaHei", 15, "bold"), width=180, height=45, corner_radius=10)
        self.btn_folder.pack(side="left")

        # 文件夹路径展示
        self.lbl_folder = ctk.CTkLabel(self.frame_top, text="尚未选择文件夹", font=("Microsoft YaHei", 15, "bold"),
                                       text_color="#555555")
        self.lbl_folder.pack(side="left", padx=25)

        # 【新增按钮】跳转下载网站
        self.btn_get_music = ctk.CTkButton(
            self.frame_top,
            text="🔍 获取音乐资源",
            command=self.open_download_site,
            font=("Microsoft YaHei", 13),
            width=120,
            height=35,
            corner_radius=10,
            fg_color="#2E7D32",  # 绿色系，代表下载和获取
            hover_color="#1B5E20"
        )
        self.btn_get_music.pack(side="right")

        # --- 中部区域 ---
        self.frame_middle = ctk.CTkFrame(self.root, fg_color="transparent")
        self.frame_middle.pack(fill="both", expand=True, pady=10)

        self.lbl_song = ctk.CTkLabel(self.frame_middle, text="等待加载音乐...", font=("Microsoft YaHei", 26, "bold"),
                                     text_color="#222222", wraplength=550)
        self.lbl_song.pack(expand=True)

        # --- 底部区域 ---
        self.frame_bottom = ctk.CTkFrame(self.root, fg_color="transparent")
        self.frame_bottom.pack(fill="x", pady=(0, 50), padx=40)

        self.frame_btns = ctk.CTkFrame(self.frame_bottom, fg_color="transparent")
        self.frame_btns.pack(pady=(0, 25))

        button_style = {"width": 80, "height": 50, "corner_radius": 12, "fg_color": "#EBEBEB", "text_color": "#333",
                        "hover_color": "#D5D5D5"}
        self.btn_prev = ctk.CTkButton(self.frame_btns, text="⏮", command=self.prev_song, font=("Arial", 24),
                                      **button_style)
        self.btn_prev.pack(side="left", padx=15)

        self.btn_next = ctk.CTkButton(self.frame_btns, text="⏭", command=self.next_song, font=("Arial", 24),
                                      **button_style)
        self.btn_next.pack(side="left", padx=15)

        self.frame_vol = ctk.CTkFrame(self.frame_bottom, fg_color="transparent")
        self.frame_vol.pack()
        self.lbl_vol_icon = ctk.CTkLabel(self.frame_vol, text="🔈", font=("Arial", 20))
        self.lbl_vol_icon.pack(side="left", padx=(0, 10))
        self.scale_vol = ctk.CTkSlider(self.frame_vol, from_=0.0, to=1.0, command=self.set_volume, width=300, height=18)
        self.scale_vol.set(0.5)
        self.scale_vol.pack(side="left")

    # ================== 逻辑部分 (保持不变) ==================

    def create_tray_icon(self):
        icon_path = "logo.ico"
        try:
            image = Image.open(icon_path)
        except:
            width, height = 64, 64
            image = Image.new('RGB', (width, height), (255, 255, 255))
            dc = ImageDraw.Draw(image)
            dc.ellipse([10, 10, 54, 54], fill=(31, 106, 165))

        menu = (
            item('显示界面', self.show_window, default=True),
            item('下一首', self.next_song),
            item('上一首', self.prev_song),
            pystray.Menu.SEPARATOR,
            item('退出程序', self.quit_app)
        )
        self.tray = pystray.Icon("MaNong", image, "码农 (Coding On Track)", menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def show_window(self):
        self.root.deiconify()
        self.root.focus_force()

    def quit_app(self):
        self.running = False
        if hasattr(self, 'tray'):
            self.tray.stop()
        if hasattr(self, 'listener'):
            self.listener.stop()
        pygame.mixer.quit()
        self.root.quit()
        self.root.destroy()

    def update_song_label(self, text, color="#222222"):
        self.root.after(0, lambda: self.lbl_song.configure(text=text, text_color=color))

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

    def prev_song(self, icon=None, item=None):
        if not self.playlist: return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_current()
        self.last_type_time = time.time()

    def next_song(self, icon=None, item=None):
        if not self.playlist: return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_current()
        self.last_type_time = time.time()

    def load_playlist(self):
        try:
            self.playlist = [f for f in os.listdir(self.playlist_dir) if f.lower().endswith('.mp3')]
            if not self.playlist:
                messagebox.showwarning("提示", "该文件夹下没有找到 MP3 文件！")
                self.update_song_label("无 MP3 文件", color="#CC3333")
            else:
                self.current_index = 0
                self.update_song_label("准备就绪，开始输入吧...", color="#1f6AA5")
        except:
            pass

    def play_current(self):
        if not self.playlist: return
        song_name = self.playlist[self.current_index]
        song_path = os.path.join(self.playlist_dir, song_name)
        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            display_name = song_name[:-4] if song_name.lower().endswith('.mp3') else song_name
            self.update_song_label(display_name, color="#222222")
        except Exception as e:
            print(f"播放失败: {e}")

    def on_key_press(self, key):
        self.last_type_time = time.time()
        if not self.playlist: return
        if not self.is_playing:
            self.play_current()
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            display_name = self.playlist[self.current_index][:-4]
            self.update_song_label(display_name, color="#222222")

    def check_status_loop(self):
        while self.running:
            time.sleep(0.1)
            if not self.playlist: continue
            if self.is_playing and not self.is_paused:
                if time.time() - self.last_type_time > 2.0:
                    pygame.mixer.music.pause()
                    self.is_paused = True
                    self.update_song_label("⏸ 暂停中", color="#AAAAAA")
            if self.is_playing and not self.is_paused and not pygame.mixer.music.get_busy():
                self.current_index = (self.current_index + 1) % len(self.playlist)
                self.play_current()

    def start_background_tasks(self):
        self.status_thread = threading.Thread(target=self.check_status_loop, daemon=True)
        self.status_thread.start()
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()


if __name__ == "__main__":
    root = ctk.CTk()
    app = MaNongApp(root)
    root.mainloop()