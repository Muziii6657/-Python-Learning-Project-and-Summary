import os
import time
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pynput import keyboard
import pygame

# 设置外观
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")


class MaNongApp:
    def __init__(self, root):
        self.root = root
        self.root.title("码农 (Coder Flow) - 沉浸式打字音乐")

        # 调整窗口大小，给组件更多呼吸空间
        self.root.geometry("650x450")
        self.root.resizable(False, False)

        # 核心逻辑变量
        self.playlist_dir = ""
        self.playlist = []
        self.current_index = 0
        self.last_type_time = 0
        self.is_playing = False
        self.is_paused = False

        pygame.mixer.init()

        self.build_ui()

        self.running = True
        self.start_background_tasks()

    def build_ui(self):
        """构建更大气、更细腻的 UI 界面"""

        # --- 1. 顶部：文件夹选择区 (加大、加深) ---
        self.frame_top = ctk.CTkFrame(self.root, fg_color="transparent")
        self.frame_top.pack(fill="x", pady=(40, 20), padx=40)

        self.btn_folder = ctk.CTkButton(
            self.frame_top,
            text="📁 选择歌单文件夹",
            command=self.select_folder,
            font=("Microsoft YaHei", 15, "bold"),  # 字号加大
            width=180,
            height=45,  # 高度增加，更有点击感
            corner_radius=10
        )
        self.btn_folder.pack(side="left")

        self.lbl_folder = ctk.CTkLabel(
            self.frame_top,
            text="尚未选择文件夹",
            font=("Microsoft YaHei", 15, "bold"),  # 加大并加粗文件夹名
            text_color="#555555"
        )
        self.lbl_folder.pack(side="left", padx=25)

        # --- 2. 中部：歌曲信息展示区 (重点突出) ---
        self.frame_middle = ctk.CTkFrame(self.root, fg_color="transparent")
        self.frame_middle.pack(fill="both", expand=True, pady=10)

        self.lbl_song = ctk.CTkLabel(
            self.frame_middle,
            text="等待加载音乐...",
            font=("Microsoft YaHei", 26, "bold"),  # 歌曲名大幅加大
            text_color="#222222",
            wraplength=550
        )
        self.lbl_song.pack(expand=True)

        # --- 3. 底部：控制区 ---
        self.frame_bottom = ctk.CTkFrame(self.root, fg_color="transparent")
        self.frame_bottom.pack(fill="x", pady=(0, 50), padx=40)

        # 切歌按钮组 (更大、更圆润)
        self.frame_btns = ctk.CTkFrame(self.frame_bottom, fg_color="transparent")
        self.frame_btns.pack(pady=(0, 25))

        button_style = {
            "width": 80,
            "height": 50,
            "corner_radius": 12,
            "fg_color": "#EBEBEB",
            "text_color": "#333",
            "hover_color": "#D5D5D5"
        }

        self.btn_prev = ctk.CTkButton(
            self.frame_btns, text="⏮", command=self.prev_song,
            font=("Arial", 24), **button_style  # 增大图标尺寸
        )
        self.btn_prev.pack(side="left", padx=15)

        self.btn_next = ctk.CTkButton(
            self.frame_btns, text="⏭", command=self.next_song,
            font=("Arial", 24), **button_style
        )
        self.btn_next.pack(side="left", padx=15)

        # 音量控制区 (加长滑块)
        self.frame_vol = ctk.CTkFrame(self.frame_bottom, fg_color="transparent")
        self.frame_vol.pack()

        self.lbl_vol_icon = ctk.CTkLabel(self.frame_vol, text="🔈", font=("Arial", 20))  # 音量图标加大
        self.lbl_vol_icon.pack(side="left", padx=(0, 10))

        self.scale_vol = ctk.CTkSlider(
            self.frame_vol, from_=0.0, to=1.0,
            command=self.set_volume,
            width=300,  # 滑块拉长，控制更细腻
            height=18
        )
        self.scale_vol.set(0.5)
        self.scale_vol.pack(side="left")

    # ================== 核心逻辑 ==================

    def update_song_label(self, text, color="#222222"):
        self.lbl_song.configure(text=text, text_color=color)

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="选择包含 MP3 的文件夹")
        if folder_path:
            self.playlist_dir = folder_path
            # 获取文件夹名并显示，加粗加大
            folder_name = os.path.basename(folder_path)
            self.lbl_folder.configure(text=folder_name)
            self.load_playlist()

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

    def prev_song(self):
        if not self.playlist: return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_current()
        self.last_type_time = time.time()

    def next_song(self):
        if not self.playlist: return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_current()
        self.last_type_time = time.time()

    def load_playlist(self):
        self.playlist = [f for f in os.listdir(self.playlist_dir) if f.lower().endswith('.mp3')]
        if not self.playlist:
            messagebox.showwarning("提示", "该文件夹下没有找到 MP3 文件！")
            self.update_song_label("无 MP3 文件", color="#CC3333")
        else:
            self.current_index = 0
            self.update_song_label("准备就绪，开始输入吧...", color="#1f6AA5")

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

    def on_closing(self):
        self.running = False
        if hasattr(self, 'listener'):
            self.listener.stop()
        pygame.mixer.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = MaNongApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()