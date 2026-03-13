import os
import time
import threading
from pynput import keyboard
import pygame


class MaNongPlayer:
    def __init__(self, playlist_dir="playlist"):
        self.playlist_dir = playlist_dir
        self.playlist = []
        self.current_index = 0
        self.last_type_time = 0
        self.is_playing = False
        self.is_paused = False

        # 初始化 pygame 的音频混合器
        pygame.mixer.init()
        # 加载歌单
        self.load_playlist()

    def load_playlist(self):
        """读取目录下的所有mp3文件"""
        if not os.path.exists(self.playlist_dir):
            os.makedirs(self.playlist_dir)
            print(f"请在 {self.playlist_dir} 文件夹中放入MP3文件！")
            return

        self.playlist = [f for f in os.listdir(self.playlist_dir) if f.endswith('.mp3')]
        if not self.playlist:
            print("歌单为空，请添加MP3文件！")
        else:
            print(f"成功加载 {len(self.playlist)} 首歌曲。")

    def play_current(self):
        """播放当前索引的歌曲"""
        if not self.playlist: return
        song_path = os.path.join(self.playlist_dir, self.playlist[self.current_index])
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        self.is_playing = True
        self.is_paused = False
        print(f"正在播放: {self.playlist[self.current_index]}")

    def on_key_press(self, key):
        """键盘按下的回调函数"""
        self.last_type_time = time.time()

        if not self.playlist: return

        # 如果当前没在播放，说明是刚启动或者切歌了
        if not self.is_playing:
            self.play_current()
        # 如果是暂停状态，则恢复播放
        elif self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def check_status_loop(self):
        """后台检测线程：负责检查是否停顿超时，以及是否需要切歌"""
        while True:
            time.sleep(0.1)

            # 1. 检查是否停顿超过2秒
            if self.is_playing and not self.is_paused:
                if time.time() - self.last_type_time > 2.0:
                    pygame.mixer.music.pause()
                    self.is_paused = True
                    # print("停止敲击超2秒，已暂停...")

            # 2. 检查歌曲是否自然播放完毕（没在暂停，且mixer不忙碌）
            if self.is_playing and not self.is_paused and not pygame.mixer.music.get_busy():
                # 切到下一首
                self.current_index = (self.current_index + 1) % len(self.playlist)
                self.play_current()

    def start(self):
        """启动程序"""
        print("====== 码农 (Coder Flow) 已启动 ======")
        print("请开始敲击键盘...")

        # 启动后台检测线程
        status_thread = threading.Thread(target=self.check_status_loop, daemon=True)
        status_thread.start()

        # 启动键盘监听（阻塞主线程）
        with keyboard.Listener(on_press=self.on_key_press) as listener:
            listener.join()


if __name__ == "__main__":
    app = MaNongPlayer()
    app.start()