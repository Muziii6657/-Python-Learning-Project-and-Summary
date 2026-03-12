# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox

# ==================== 1. 扩充核心数据 ====================
# 给每个功能项新增了 'example' 字段，提供直观的 Python 代码演示
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
        self.root.title("正则表达式辅助器 V2.1 (GUI版)")
        # 增大了窗口高度，以容纳代码示例区
        self.root.geometry("650x620")
        self.root.resizable(False, False)

        self.root.eval('tk::PlaceWindow . center')

        self.current_state = 'main'
        self.current_category = None

        self.main_frame = tk.Frame(self.root, padx=30, pady=20)
        self.main_frame.pack(expand=True, fill='both')

        self.root.bind('<Key>', self.on_key_press)
        self.show_main_menu()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_frame()
        self.current_state = 'main'
        self.current_category = None

        tk.Label(self.main_frame, text="欢迎使用 正则表达式辅助器", font=("Microsoft YaHei", 18, "bold")).pack(
            pady=(0, 20))

        for key, value in REGEX_MENU.items():
            btn_text = f"[{key}] {value['title']}"
            btn = ttk.Button(self.main_frame, text=btn_text, command=lambda k=key: self.show_sub_menu(k))
            btn.pack(fill='x', ipady=5, pady=5)

        ttk.Button(self.main_frame, text="[4] 正则字典库 (速查表)", command=self.show_dictionary).pack(fill='x',
                                                                                                       ipady=5, pady=5)
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=10)
        ttk.Button(self.main_frame, text="[0] 退出程序", command=self.root.quit).pack(fill='x', ipady=5, pady=5)

        tk.Label(self.main_frame, text="提示: 您可以使用鼠标点击，也可以直接在键盘输入数字 [0-4]", fg="gray").pack(
            side='bottom')

    def show_sub_menu(self, category_id):
        self.clear_frame()
        self.current_state = 'sub'
        self.current_category = category_id
        category_data = REGEX_MENU[category_id]

        tk.Label(self.main_frame, text=f"【 {category_data['title']} 】", font=("Microsoft YaHei", 16, "bold"),
                 fg="#333333").pack(pady=(0, 20))

        for sub_key, sub_value in category_data["items"].items():
            btn_text = f"[{sub_key}] {sub_value['name']}"
            btn = ttk.Button(self.main_frame, text=btn_text, command=lambda sk=sub_key: self.show_result(sk))
            btn.pack(fill='x', ipady=5, pady=5)

        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=15)
        ttk.Button(self.main_frame, text="[0] 返回上一级", command=self.show_main_menu).pack(fill='x', ipady=5, pady=5)

    def show_result(self, item_id):
        self.clear_frame()
        self.current_state = 'result'

        target = REGEX_MENU[self.current_category]["items"][item_id]

        # 1. 目标需求与正则展示区
        tk.Label(self.main_frame, text="★ 目标需求 ★", font=("Microsoft YaHei", 12)).pack(pady=(5, 5))
        tk.Label(self.main_frame, text=target['name'], font=("Microsoft YaHei", 15, "bold"), fg="#0052cc").pack(
            pady=(0, 15))

        tk.Label(self.main_frame, text="★ 推荐正则表达式 ★", font=("Microsoft YaHei", 12)).pack(pady=5)
        pattern_var = tk.StringVar(value=target['pattern'])
        entry = tk.Entry(self.main_frame, textvariable=pattern_var, font=("Consolas", 15), justify='center',
                         state='readonly', readonlybackground="#f0f0f0")
        entry.pack(fill='x', ipady=8, pady=(0, 15))

        # ==================== 2. 新增：Python代码示例区 ====================
        tk.Label(self.main_frame, text="★ Python 使用示例 ★", font=("Microsoft YaHei", 12)).pack(pady=5)

        # 使用深色背景的 Text 控件模拟代码编辑器风格
        code_text = tk.Text(self.main_frame, height=5, font=("Consolas", 11), bg="#282c34", fg="#abb2bf", padx=10,
                            pady=10)
        code_text.insert(tk.END, target.get('example', '# 暂无示例代码'))

        # 禁用输入，防止用户修改代码框内容，但允许鼠标框选复制
        code_text.bind("<Key>", lambda e: "break")
        code_text.pack(fill='x', pady=(0, 15))

        # =================================================================

        # 3. 底部按钮区 (保留原版一键复制正则功能)
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(target['pattern'])
            messagebox.showinfo("成功", "正则表达式已成功复制到剪贴板！\n可以直接去使用了。")

        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(fill='x', pady=5)

        ttk.Button(btn_frame, text="一键复制正则表达式", command=copy_to_clipboard).pack(side='left', expand=True,
                                                                                         fill='x', padx=5, ipady=5)
        ttk.Button(btn_frame, text="[0] 返回上一级", command=lambda: self.show_sub_menu(self.current_category)).pack(
            side='right', expand=True, fill='x', padx=5, ipady=5)

    def show_dictionary(self):
        self.clear_frame()
        self.current_state = 'dict'

        tk.Label(self.main_frame, text="【正则符号速查字典】", font=("Microsoft YaHei", 16, "bold")).pack(pady=(0, 10))

        columns = ("Symbol", "Description")
        tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=10)
        tree.heading("Symbol", text="符号")
        tree.heading("Description", text="含义与说明")
        tree.column("Symbol", width=120, anchor='center')
        tree.column("Description", width=400, anchor='w')

        for sym, desc in REGEX_DICT.items():
            tree.insert("", "end", values=(sym, desc))

        tree.pack(fill='both', expand=True, pady=10)
        ttk.Button(self.main_frame, text="[0] 返回主菜单", command=self.show_main_menu).pack(fill='x', ipady=5, pady=5)

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
        print("\n检测到强制中断，程序已优雅退出。再见！")