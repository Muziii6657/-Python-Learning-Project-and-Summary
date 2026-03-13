import os
import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pynput import keyboard
import pygame


class MaNongApp:
    def __init__(self, root):
        self.root = root
        self.root.title("码农 (Coder Flow) - 沉浸式打字音乐")
        self.root.geometry("450x300")
        self.root.resizable(False, False)

        # 核心逻辑变量
        self.playlist_dir = ""
        self.playlist = []
        self.current_index = 0
        self.last_type_time = 0
        self.is_playing = False
        self.is_paused = False

        # 初始化 pygame 音频模块
        pygame.mixer.init()

        # 构建 UI 界面
        self.build_ui()

        # 启动后台工作线程
        self.running = True
        self.start_background_tasks()

    def build_ui(self):
        """构建图形界面"""
        # 1. 顶部：文件夹选择
        frame_top = tk.Frame(self.root, pady=10)
        frame_top.pack(fill=tk.X)

        self.btn_folder = tk.Button(frame_top, text="选择歌单文件夹", command=self.select_folder, font=("微软雅黑", 10))
        self.btn_folder.pack(side=tk.LEFT, padx=20)

        self.lbl_folder = tk.Label(frame_top, text="尚未选择文件夹", fg="gray", font=("微软雅黑", 9))
        self.lbl_folder.pack(side=tk.LEFT, padx=5)

        # 2. 中部：歌曲信息展示
        frame_middle = tk.Frame(self.root, pady=30)
        frame_middle.pack(fill=tk.X)

        self.song_var = tk.StringVar()
        self.song_var.set("等待加载音乐...")
        self.lbl_song = tk.Label(frame_middle, textvariable=self.song_var, font=("微软雅黑", 14, "bold"), fg="#333333",
                                 wraplength=400)
        self.lbl_song.pack()

        # 3. 底部控制区：上一首、下一首、音量
        frame_bottom = tk.Frame(self.root, pady=10)
        frame_bottom.pack(fill=tk.X)

        # 切歌按钮
        frame_btns = tk.Frame(frame_bottom)
        frame_btns.pack(pady=10)

        self.btn_prev = tk.Button(frame_btns, text="⏮ 上一首", command=self.prev_song, font=("微软雅黑", 10), width=10)
        self.btn_prev.pack(side=tk.LEFT, padx=20)

        self.btn_next = tk.Button(frame_btns, text="下一首 ⏭", command=self.next_song, font=("微软雅黑", 10), width=10)
        self.btn_next.pack(side=tk.LEFT, padx=20)

        # 音量滑块
        frame_vol = tk.Frame(frame_bottom)
        frame_vol.pack(pady=10)

        tk.Label(frame_vol, text="音量:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=5)
        self.scale_vol = tk.Scale(frame_vol, from_=0, to=100, orient=tk.HORIZONTAL, length=200, command=self.set_volume)
        self.scale_vol.set(50)  # 默认音量 50%
        self.scale_vol.pack(side=tk.LEFT)

    # ================== 界面交互逻辑 ==================

    def select_folder(self):
        """打开文件夹选择对话框"""
        folder_path = filedialog.askdirectory(title="选择包含 MP3 的文件夹")
        if folder_path:
            self.playlist_dir = folder_path
            self.lbl_folder.config(text=os.path.basename(folder_path))  # 仅显示文件夹名
            self.load_playlist()

    def set_volume(self, val):
        """设置音量 (0.0 到 1.0)"""
        volume = float(val) / 100
        pygame.mixer.music.set_volume(volume)

    def prev_song(self):
        """上一首"""
        if not self.playlist: return
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_current()
        self.last_type_time = time.time()  # 假装敲击了键盘，防止马上暂停

    def next_song(self):
        """下一首"""
        if not self.playlist: return
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_current()
        self.last_type_time = time.time()

    # ================== 核心播放与监听逻辑 ==================

    def load_playlist(self):
        """读取目录下的所有mp3文件"""
        self.playlist = [f for f in os.listdir(self.playlist_dir) if f.lower().endswith('.mp3')]
        if not self.playlist:
            messagebox.showwarning("警告", "该文件夹下没有找到 MP3 文件！")
            self.song_var.set("无 MP3 文件")
        else:
            self.current_index = 0
            self.song_var.set("准备就绪，请敲击键盘开始...")
            print(f"成功加载 {len(self.playlist)} 首歌曲。")

    def play_current(self):
        """播放当前索引的歌曲"""
        if not self.playlist: return
        song_name = self.playlist[self.current_index]
        song_path = os.path.join(self.playlist_dir, song_name)

        try:
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False

            # 更新界面文字（去掉 .mp3 后缀让显示更美观）
            display_name = song_name[:-4] if song_name.lower().endswith('.mp3') else song_name
            self.song_var.set(f"正在播放: {display_name}")
        except Exception as e:
            print(f"播放失败: {e}")

    def on_key_press(self, key):
        """键盘按下的回调函数"""
        self.last_type_time = time.time()

        if not self.playlist: return

        if not self.is_playing:
            self.play_current()
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.song_var.set(f"正在播放: {self.playlist[self.current_index][:-4]}")

    def check_status_loop(self):
        """后台检测线程：负责检查停顿超时与自动切歌"""
        while self.running:
            time.sleep(0.1)

            if not self.playlist: continue

            # 1. 检查是否停顿超过 2 秒
            if self.is_playing and not self.is_paused:
                if time.time() - self.last_type_time > 2.0:
                    pygame.mixer.music.pause()
                    self.is_paused = True
                    self.song_var.set(f"暂停中... (等待敲击)")

            # 2. 检查歌曲是否自然播放完毕
            # get_busy() 为 False 意味着音乐停止了。但如果我们在暂停状态，它也是 False 或 True（取决于底层），
            # 所以确保是 is_playing 且没被 is_paused 时才切歌。
            if self.is_playing and not self.is_paused and not pygame.mixer.music.get_busy():
                # 自动下一首
                self.current_index = (self.current_index + 1) % len(self.playlist)
                self.play_current()

    def start_background_tasks(self):
        """启动后台的键盘监听和状态检测线程"""
        # 启动状态检测线程
        self.status_thread = threading.Thread(target=self.check_status_loop, daemon=True)
        self.status_thread.start()

        # 启动键盘监听线程
        self.listener = keyboard.Listener(on_press=self.on_key_press)
        self.listener.start()

    def on_closing(self):
        """关闭窗口时的清理工作"""
        self.running = False
        if self.listener:
            self.listener.stop()
        pygame.mixer.quit()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MaNongApp(root)
    # 绑定关闭窗口事件，确保后台线程随之结束
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    # 启动图形界面主循环
    root.mainloop()