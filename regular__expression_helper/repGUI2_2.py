# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox

# ==================== 核心数据 ====================
REGEX_MENU = {
    "1": {
        "title": "提取类 (从长文段中抓取特定内容)",
        "items": {
            "1": {
                "name": "提取网址URL",
                "pattern": r"https?://[^\s]+",
                "example": "import re\ntext = '我的博客是 https://example.com 欢迎'\nurls = re.findall(r'https?://[^\\s]+', text)\nprint(urls)  # 输出: ['https://example.com']"
            },
            "2": {
                "name": "提取电子邮箱 (Email)",
                "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "example": "import re\ntext = '联系我：admin@test.com'\nemails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}', text)\nprint(emails)  # 输出:['admin@test.com']"
            },
            "3": {
                "name": "提取连续的数字 (如提取验证码)",
                "pattern": r"\d+",
                "example": "import re\ntext = '您的验证码是849201，5分钟内有效'\nnums = re.findall(r'\\d+', text)\nprint(nums)  # 输出:['849201', '5']"
            }
        }
    },
    "2": {
        "title": "验证类 (判断输入格式是否完全正确)",
        "items": {
            "1": {
                "name": "验证中国大陆手机号",
                "pattern": r"^1[3-9]\d{9}$",
                "example": "import re\nphone = '13812345678'\nif re.match(r'^1[3-9]\\d{9}$', phone):\n    print('手机号格式正确！')"
            },
            "2": {
                "name": "验证强密码 (字母+数字，至少8位)",
                "pattern": r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$",
                "example": "import re\npwd = 'Password123'\nif re.match(r'^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$', pwd):\n    print('密码强度合格！')"
            },
            "3": {
                "name": "验证身份证号 (18位)",
                "pattern": r"^\d{17}[\dXx]$",
                "example": "import re\nid_card = '11010519491231002X'\nif re.match(r'^\\d{17}[\\dXx]$', id_card):\n    print('身份证号校验通过！')"
            }
        }
    },
    "3": {
        "title": "替换/清洗类 (用于清理脏数据)",
        "items": {
            "1": {
                "name": "去除所有空白字符 (空格、换行等)",
                "pattern": r"\s+",
                "example": "import re\ntext = '这 是 一 段\\n脏 数 据'\nclean_text = re.sub(r'\\s+', '', text)\nprint(clean_text)  # 输出: 这是段脏数据"
            },
            "2": {
                "name": "去除HTML标签 (提取纯文本)",
                "pattern": r"<[^>]+>",
                "example": "import re\nhtml = '<p>提取<b>纯文本</b></p>'\nclean_text = re.sub(r'<[^>]+>', '', html)\nprint(clean_text)  # 输出: 提取纯文本"
            }
        }
    }
}

REGEX_DICT = {
    r".": "匹配除换行符以外的任意字符",
    r"\w": "匹配字母、数字、下划线",
    r"\d": "匹配任意数字 (等同于[0-9])",
    r"\s": "匹配任意空白字符",
    "^": "匹配字符串的开始位置",
    "$": "匹配字符串的结束位置",
    "*": "匹配前一个字符 0 次或多次",
    "+": "匹配前一个字符 1 次或多次",
    "?": "匹配前一个字符 0 次或 1 次",
    "{n,m}": "匹配前一个字符至少 n 次，至多 m 次"
}


class RegexHelperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("正则表达式辅助器 V2.2 (GUI 增强版)")

        # 初始窗口大小调整，为大字体留出空间
        self.base_width = 720
        self.base_height = 680
        self.root.geometry(f"{self.base_width}x{self.base_height}")
        self.root.resizable(False, False)
        self.root.eval('tk::PlaceWindow . center')

        # ==================== UI 样式配置 ====================
        self.style = ttk.Style()
        # 放大首页和菜单的按钮字体及内边距
        self.style.configure('Big.TButton', font=('Microsoft YaHei', 13), padding=12)
        # 放大底部操作按钮
        self.style.configure('Action.TButton', font=('Microsoft YaHei', 11), padding=8)
        # 放大 Treeview（表格）字体和行高
        self.style.configure("Treeview", font=('Microsoft YaHei', 11), rowheight=32)
        self.style.configure("Treeview.Heading", font=('Microsoft YaHei', 12, 'bold'))

        self.current_state = 'main'
        self.current_category = None
        self.is_drawer_open = False

        # ==================== 容器布局结构 ====================
        # 1. 左侧主容器（始终显示）
        self.left_container = tk.Frame(self.root)
        self.left_container.pack(side='left', fill='both', expand=True)

        self.main_frame = tk.Frame(self.left_container, padx=40, pady=25)
        self.main_frame.pack(expand=True, fill='both')

        # 2. 右侧抽屉容器（默认隐藏，用于展示速查表）
        self.drawer_frame = tk.Frame(self.root, width=500, bg="#f0f2f5", highlightbackground="#d9d9d9",
                                     highlightthickness=1)
        self.drawer_frame.pack_propagate(False)  # 锁定容器宽度，防止被内容撑开
        self.build_drawer_content()

        self.root.bind('<Key>', self.on_key_press)
        self.show_main_menu()

    def build_drawer_content(self):
        """预先构建右侧抽屉内的速查表内容"""
        tk.Label(self.drawer_frame, text="📖 正则符号速查表", font=("Microsoft YaHei", 15, "bold"), bg="#f0f2f5").pack(
            pady=(20, 15))

        columns = ("Symbol", "Description")
        drawer_tree = ttk.Treeview(self.drawer_frame, columns=columns, show="headings", height=15)
        drawer_tree.heading("Symbol", text="符号")
        drawer_tree.heading("Description", text="含义与说明")
        drawer_tree.column("Symbol", width=120, anchor='center')
        drawer_tree.column("Description", width=340, anchor='w')

        for sym, desc in REGEX_DICT.items():
            drawer_tree.insert("", "end", values=(sym, desc))

        drawer_tree.pack(fill='both', expand=True, padx=15, pady=(0, 20))

    def toggle_drawer(self):
        """控制右侧侧边栏的展开与收起"""
        if self.is_drawer_open:
            self.drawer_frame.pack_forget()
            self.root.geometry(f"{self.base_width}x{self.base_height}")
            self.toggle_btn.config(text="语法速查 ➔")
            self.is_drawer_open = False
        else:
            self.drawer_frame.pack(side='right', fill='y')
            # 展开后总宽度变为 主窗口+抽屉宽度
            self.root.geometry(f"{self.base_width + 500}x{self.base_height}")
            self.toggle_btn.config(text="收起速查 ⬅")
            self.is_drawer_open = True

    def close_drawer(self):
        """强制收起抽屉（用于切换页面时）"""
        if self.is_drawer_open:
            self.toggle_drawer()

    def clear_frame(self):
        """清空左侧主页面的内容"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ==================== 页面渲染逻辑 ====================
    def show_main_menu(self):
        self.close_drawer()  # 回到首页时自动收起右侧菜单
        self.clear_frame()
        self.current_state = 'main'
        self.current_category = None

        tk.Label(self.main_frame, text="欢迎使用 正则表达式辅助器", font=("Microsoft YaHei", 20, "bold")).pack(
            pady=(10, 30))

        # 使用 Big.TButton 样式，按钮变得更大更易点
        for key, value in REGEX_MENU.items():
            btn_text = f"[{key}] {value['title']}"
            btn = ttk.Button(self.main_frame, text=btn_text, style='Big.TButton',
                             command=lambda k=key: self.show_sub_menu(k))
            btn.pack(fill='x', pady=8)

        ttk.Button(self.main_frame, text="[4] 独立进入速查表", style='Big.TButton', command=self.show_dictionary).pack(
            fill='x', pady=8)
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=15)
        ttk.Button(self.main_frame, text="[0] 退出程序", style='Big.TButton', command=self.root.quit).pack(fill='x',
                                                                                                           pady=8)

        tk.Label(self.main_frame, text="提示: 您可以使用鼠标点击，也可以直接在键盘输入数字 [0-4]", fg="#888888",
                 font=("Microsoft YaHei", 10)).pack(side='bottom', pady=10)

    def show_sub_menu(self, category_id):
        self.close_drawer()
        self.clear_frame()
        self.current_state = 'sub'
        self.current_category = category_id
        category_data = REGEX_MENU[category_id]

        tk.Label(self.main_frame, text=f"【 {category_data['title']} 】", font=("Microsoft YaHei", 18, "bold"),
                 fg="#333333").pack(pady=(10, 30))

        for sub_key, sub_value in category_data["items"].items():
            btn_text = f"[{sub_key}] {sub_value['name']}"
            btn = ttk.Button(self.main_frame, text=btn_text, style='Big.TButton',
                             command=lambda sk=sub_key: self.show_result(sk))
            btn.pack(fill='x', pady=8)

        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=20)
        ttk.Button(self.main_frame, text="[0] 返回上一级", style='Big.TButton', command=self.show_main_menu).pack(
            fill='x', pady=8)

    def show_result(self, item_id):
        self.clear_frame()
        self.current_state = 'result'

        target = REGEX_MENU[self.current_category]["items"][item_id]

        tk.Label(self.main_frame, text="★ 目标需求 ★", font=("Microsoft YaHei", 13)).pack(pady=(5, 5))
        tk.Label(self.main_frame, text=target['name'], font=("Microsoft YaHei", 18, "bold"), fg="#0052cc").pack(
            pady=(0, 20))

        tk.Label(self.main_frame, text="★ 推荐正则表达式 ★", font=("Microsoft YaHei", 13)).pack(pady=5)
        pattern_var = tk.StringVar(value=target['pattern'])
        # 表达式字体升级到 18 加粗
        entry = tk.Entry(self.main_frame, textvariable=pattern_var, font=("Consolas", 18, "bold"), justify='center',
                         state='readonly', readonlybackground="#f0f0f0")
        entry.pack(fill='x', ipady=12, pady=(0, 20))

        tk.Label(self.main_frame, text="★ Python 使用示例 ★", font=("Microsoft YaHei", 13)).pack(pady=5)

        # 代码框字体升级到 12
        code_text = tk.Text(self.main_frame, height=5, font=("Consolas", 12), bg="#282c34", fg="#abb2bf", padx=15,
                            pady=15)
        code_text.insert(tk.END, target.get('example', '# 暂无示例代码'))
        code_text.bind("<Key>", lambda e: "break")
        code_text.pack(fill='x', pady=(0, 25))

        # ==================== 底部按钮网格布局 (等宽分布) ====================
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(target['pattern'])
            messagebox.showinfo("成功", "正则表达式已成功复制到剪贴板！\n可以直接去使用了。")

        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(fill='x', pady=5)

        # 将容器分成均匀的三列
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)

        ttk.Button(btn_frame, text="📋 一键复制", style='Action.TButton', command=copy_to_clipboard).grid(row=0,
                                                                                                         column=0,
                                                                                                         padx=5,
                                                                                                         sticky='ew')

        # 【新增】右拉抽屉开关按钮
        self.toggle_btn = ttk.Button(btn_frame, text="💡 语法速查 ➔", style='Action.TButton', command=self.toggle_drawer)
        self.toggle_btn.grid(row=0, column=1, padx=5, sticky='ew')

        ttk.Button(btn_frame, text="[0] 🔙 返回", style='Action.TButton',
                   command=lambda: self.show_sub_menu(self.current_category)).grid(row=0, column=2, padx=5, sticky='ew')

    def show_dictionary(self):
        """保留：首页直接独立进入的大速查表"""
        self.close_drawer()
        self.clear_frame()
        self.current_state = 'dict'

        tk.Label(self.main_frame, text="【正则符号速查字典】", font=("Microsoft YaHei", 18, "bold")).pack(pady=(0, 15))

        columns = ("Symbol", "Description")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=12)
        tree.heading("Symbol", text="符号")
        tree.heading("Description", text="含义与说明")
        tree.column("Symbol", width=150, anchor='center')
        tree.column("Description", width=450, anchor='w')

        for sym, desc in REGEX_DICT.items():
            tree.insert("", "end", values=(sym, desc))

        tree.pack(fill='both', expand=True, pady=10)
        ttk.Button(self.main_frame, text="[0] 返回主菜单", style='Big.TButton', command=self.show_main_menu).pack(
            fill='x', pady=10)

    # ==================== 键盘事件映射 ====================
    def on_key_press(self, event):
        char = event.char
        if not char.isdigit():
            return

        if self.current_state == 'main':
            if char in REGEX_MENU:
                self.show_sub_menu(char)
            elif char == '4':
                self.show_dictionary()
            elif char == '0':
                self.root.quit()
        elif self.current_state == 'sub':
            if char in REGEX_MENU[self.current_category]["items"]:
                self.show_result(char)
            elif char == '0':
                self.show_main_menu()
        elif self.current_state in ['result', 'dict']:
            if char == '0':
                if self.current_state == 'result':
                    self.show_sub_menu(self.current_category)
                else:
                    self.show_main_menu()


# 启动程序
if __name__ == "__main__":
    root = tk.Tk()
    app = RegexHelperApp(root)

    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass