#等待复现，重新敲一遍
# -*- coding: utf-8 -*-
import time

#习惯上注意，不要在代码中的单一程序块添加空白行
#定义核心数据，其中内容由ai总结出经典或热门正则表达式应用场景
REGEX_MENU = {
    #第一层,包含title和items名。 先进行第一层结果的编码再填充具体内容 如 "1":{"title":  , "items":  },"2":{"title":  , "items":  }
    "1" : {
        "title": "提取类(从长文段中抓取特定内容·)" ,
        "items":{
            #第二层 字典内容
            "1":{"name": "提取网址URL","pattern":r"https?://[^\s]+)"},
            "2": {"name": "提取电子邮箱 (Email)", "pattern": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"},
            "3": {"name": "提取连续的数字 (如提取验证码)", "pattern": r"\d+"}
        }
    },
    "2" : {
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
#定义一级菜单内最后一项，字典查询数据
REGEX_DICT = {
    r".": "匹配除换行符以外的任意字符",
    r"\w": "匹配字母、数字、下划线 (等同于[a-zA-Z0-9_])",
    r"\d": "匹配任意数字 (等同于[0-9])",
    r"\s": "匹配任意空白字符 (空格、制表符、换行符)",
    "^": "匹配字符串的开始位置",
    "$": "匹配字符串的结束位置",
    "*": "匹配前一个字符 0 次或多次",
    "+": "匹配前一个字符 1 次或多次",
    "?": "匹配前一个字符 0 次或 1 次",
    "{n,m}": "匹配前一个字符至少 n 次，至多 m 次"
}
#编写主函数
def main():
    #如果语句中使用了space间隔各部分，就要让代码上下文中相同部分间隔控制相同，保持整洁
    print("=" * 40)
    print("欢迎使用 正则表达式辅助器 V1.0")
    print("=" * 40)

    #主循环（一级菜单）
    while True:
        print("\n[主菜单] 请选择你需要处理的场景类别：")
        # 动态展示一级菜单,for循环展示
        for key, value in REGEX_MENU.items():
            print(f"[{key}] {value['title']}")
        print("[4] 正则字典库 (速查表)")
        print("[0] 退出程序")

        choice_1 = input("请输入你想使用的场景编号或功能编号： ").strip()

        # 处理退出
        if choice_1 == "0":
            print("感谢使用，再见！")
            break

            # 处理字典功能 (最后一项)
        elif choice_1 == "4":
            print("\n" + "-" * 30)
            print("【正则符号速查字典】")
            for symbol, desc in REGEX_DICT.items():
                print(f" {symbol:<8} ->  {desc}")
            print("-" * 30)
            input("按回车键返回主菜单...")
            continue

            # 处理一级菜单正常选项
        elif choice_1 in REGEX_MENU:
            category_data = REGEX_MENU[choice_1]

            # 二级菜单循环
            while True:
                print(f"\n【二级菜单 - {category_data['title']}】")
                for sub_key, sub_value in category_data["items"].items():
                    print(f"[{sub_key}] {sub_value['name']}")
                print("[0] 返回上一级")

                choice_2 = input("请输入具体需求: ").strip()

                if choice_2 == "0":
                    break  # 跳出二级循环，回到一级循环
                elif choice_2 in category_data["items"]:
                    target = category_data["items"][choice_2]
                    print("\n" + "★" * 30)
                    print(f"【目标】: {target['name']}")
                    print(f"【推荐正则表达式】: \n\n    {target['pattern']}\n")
                    print("★" * 30)

# 调用主函数
if __name__ == "__main__":
    main()