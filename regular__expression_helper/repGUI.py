# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox

# 定义核心数据
REGEX_MENU = {
    "1": {
        "title": "提取类 (从长文段中抓取特定内容)",
        "items": {
            "1": {"name": "提取网址URL", "pattern": r"https?://[^\s]+"},  # 顺手修复了原代码多出的右括号
            "2": {"name": "提取电子邮箱 (Email)", "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"},
            "3": {"name": "提取连续的数字 (如提取验证码)", "pattern": r"\d+"}
        }
    },
    "2": {
        "title": "验证类 (判断输入格式是否完全正确)",
        "items": {
            "1": {"name": "验证中国大陆手机号", "pattern": r"^1[3-9]\d{9}$"},
            "2": {"name": "验证强密码 (字母+数字，至少8位)", "pattern": r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"},
            "3": {"name": "验证身份证号 (18位)", "pattern": r"^\d{17}[\dXx]$"}
        }
    },
    "3": {
        "title": "替换/清洗类 (用于清理脏数据)",
        "items": {
            "1": {"name": "去除所有空白字符 (空格、换行等)", "pattern": r"\s+"},
            "2": {"name": "去除HTML标签 (提取纯文本)", "pattern": r"<[^>]+>"}
        }
    }
}

# 定义正则字典数据
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
        self.root.title("正则表达式辅助器 V2.0 (GUI版)")
        self.root.geometry("600x450")
        self.root.resizable(False, False)  # 固定窗口大小保持美观

        # 居中显示窗口
        self.root.eval('tk::PlaceWindow . center')

        # 状态管理 (用于键盘快捷键)
        self.current_state = 'main'
        self.current_category = None

        # 主容器
        self.main_frame = tk.Frame(self.root, padx=30, pady=20)
        self.main_frame.pack(expand=True, fill='both')

        # 绑定键盘事件
        self.root.bind('<Key>', self.on_key_press)

        # 启动显示主菜单
        self.show_main_menu()

    def clear_frame(self):
        """清空当前界面内容，为切换界面做准备"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        """显示一级菜单"""
        self.clear_frame()
        self.current_state = 'main'
        self.current_category = None

        tk.Label(self.main_frame, text="欢迎使用 正则表达式辅助器", font=("Microsoft YaHei", 18, "bold")).pack(
            pady=(0, 20))

        # 动态生成分类按钮
        for key, value in REGEX_MENU.items():
            btn_text = f"[{key}] {value['title']}"
            btn = ttk.Button(self.main_frame, text=btn_text, command=lambda k=key: self.show_sub_menu(k))
            btn.pack(fill='x', ipady=5, pady=5)

        ttk.Button(self.main_frame, text="[4] 正则字典库 (速查表)", command=self.show_dictionary).pack(fill='x',
                                                                                                       ipady=5, pady=5)

        # 分割线
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=10)

        ttk.Button(self.main_frame, text="[0] 退出程序", command=self.root.quit).pack(fill='x', ipady=5, pady=5)
        tk.Label(self.main_frame, text="提示: 您可以使用鼠标点击，也可以直接在键盘输入数字 [0-4]", fg="gray").pack(
            side='bottom')

    def show_sub_menu(self, category_id):
        """显示二级菜单"""
        self.clear_frame()
        self.current_state = 'sub'
        self.current_category = category_id
        category_data = REGEX_MENU[category_id]

        tk.Label(self.main_frame, text=f"【 {category_data['title']} 】", font=("Microsoft YaHei", 16, "bold"),
                 fg="#333333").pack(pady=(0, 20))

        # 动态生成具体功能按钮
        for sub_key, sub_value in category_data["items"].items():
            btn_text = f"[{sub_key}] {sub_value['name']}"
            btn = ttk.Button(self.main_frame, text=btn_text,
                             command=lambda sk=sub_key: self.show_result(sk))
            btn.pack(fill='x', ipady=5, pady=5)

        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=15)
        ttk.Button(self.main_frame, text="[0] 返回上一级", command=self.show_main_menu).pack(fill='x', ipady=5, pady=5)

    def show_result(self, item_id):
        """显示正则结果及复制功能"""
        self.clear_frame()
        self.current_state = 'result'

        target = REGEX_MENU[self.current_category]["items"][item_id]

        tk.Label(self.main_frame, text="★ 目标需求 ★", font=("Microsoft YaHei", 12)).pack(pady=(10, 5))
        tk.Label(self.main_frame, text=target['name'], font=("Microsoft YaHei", 15, "bold"), fg="#0052cc").pack(
            pady=(0, 20))

        tk.Label(self.main_frame, text="★ 推荐正则表达式 ★", font=("Microsoft YaHei", 12)).pack(pady=5)

        # 使用只读的Entry输入框，方便用户查看且支持直接框选复制
        pattern_var = tk.StringVar(value=target['pattern'])
        entry = tk.Entry(self.main_frame, textvariable=pattern_var, font=("Consolas", 16), justify='center',
                         state='readonly', readonlybackground="#f0f0f0")
        entry.pack(fill='x', ipady=10, pady=(0, 20))

        # 复制到剪贴板功能
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(target['pattern'])
            messagebox.showinfo("成功", "正则表达式已成功复制到剪贴板！\n可以直接去使用了。")

        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(fill='x', pady=10)

        ttk.Button(btn_frame, text="一键复制到剪贴板", command=copy_to_clipboard).pack(side='left', expand=True,
                                                                                       fill='x', padx=5, ipady=5)
        ttk.Button(btn_frame, text="[0] 返回上一级", command=lambda: self.show_sub_menu(self.current_category)).pack(
            side='right', expand=True, fill='x', padx=5, ipady=5)

    def show_dictionary(self):
        """显示正则字典 (使用表格组件)"""
        self.clear_frame()
        self.current_state = 'dict'

        tk.Label(self.main_frame, text="【正则符号速查字典】", font=("Microsoft YaHei", 16, "bold")).pack(pady=(0, 10))

        # 创建表格结构显示字典
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
        """处理键盘数字快捷键"""
        char = event.char
        if not char.isdigit():
            return

        # 在主菜单下
        if self.current_state == 'main':
            if char in REGEX_MENU:
                self.show_sub_menu(char)
            elif char == '4':
                self.show_dictionary()
            elif char == '0':
                self.root.quit()

        # 在二级菜单下
        elif self.current_state == 'sub':
            if char in REGEX_MENU[self.current_category]["items"]:
                self.show_result(char)
            elif char == '0':
                self.show_main_menu()

        # 在结果页或字典页下
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
    root.mainloop()