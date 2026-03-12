# -*- codi
# ng:
# utf-8 -*-
# ===== 第一部分：全局字体配置 =====

import matplotlib
import matplotlib.pyplot as plt

# 强制使用微软雅黑
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 可选：检查字体是否可用
import matplotlib.font_manager as fm
fonts = [f.name for f in fm.fontManager.ttflist if 'YaHei' in f.name]
if fonts:
    print(f"微软雅黑可用: {fonts[0]}")
else:
    print("微软雅黑不可用，尝试使用其他字体")
    plt.rcParams['font.sans-serif'] = ['SimHei', 'KaiTi', 'FangSong']

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import csv
import time
import re

# 目标URL
url = "https://www.shanghairanking.cn/rankings/bcur/2025"

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://www.shanghairanking.cn/',
    'Connection': 'keep-alive',
}

all_universities = []

print(f"正在爬取: {url}")

try:
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    resp.encoding = 'utf-8'
    html_code = resp.text

    # 保存页面用于调试
    with open("debug_page.html", "w", encoding="utf-8") as f:
        f.write(html_code)
    print("页面已保存到 debug_page.html")

    bs = BeautifulSoup(html_code, "html.parser")

    table = bs.find("table")
    if not table:
        table = bs.find("table", class_=lambda x: x and "rk-table" in str(x))

    if table:
        rows = table.find_all("tr")[1:]
        print(f"在表格中找到 {len(rows)} 行数据")
    else:
        rows = bs.find_all("tr")
        rows = [row for row in rows if row.find("td")]

    count = 0
    for row in rows:
        if count >= 30:
            break

        try:
            cells = row.find_all("td")
            if len(cells) < 5:
                continue

            rank = cells[0].get_text(strip=True)

            name_cell = cells[1]
            name = "N/A"
            name_span = name_cell.find("span")
            if name_span:
                name = name_span.get_text(strip=True)
            else:
                name_text = name_cell.get_text(strip=True)
                chinese_match = re.search(r'^[\u4e00-\u9fa5]+(?:大学|学院)', name_text)
                if chinese_match:
                    name = chinese_match.group()
                else:
                    name = name_text.split('\n')[0] if '\n' in name_text else name_text

            tags = []
            name_text = name_cell.get_text()
            if "双一流" in name_text:
                tags.append("双一流")
            if "985" in name_text:
                tags.append("985")
            if "211" in name_text:
                tags.append("211")
            tags_str = " | ".join(tags) if tags else "N/A"

            province_cell = cells[2] if len(cells) > 2 else None
            province = province_cell.get_text(strip=True) if province_cell else "N/A"

            type_cell = cells[3] if len(cells) > 3 else None
            type_uni = type_cell.get_text(strip=True) if type_cell else "N/A"

            score_cell = cells[4] if len(cells) > 4 else None
            total_score = score_cell.get_text(strip=True) if score_cell else "N/A"

            if rank and name != "N/A":
                all_universities.append([rank, name, tags_str, province, type_uni, total_score])
                print(f"已获取: {rank} - {name} - 总分: {total_score}")
                count += 1

        except Exception as e:
            print(f"解析条目时出错: {str(e)}")
            continue

    if len(all_universities) < 30:
        print("\n使用正则表达式进行二次提取...")
        pattern = r'<tr>\s*<td[^>]*>\s*(\d+)\s*</td>\s*<td[^>]*>.*?([\u4e00-\u9fa5]+(?:大学|学院)).*?</td>\s*<td[^>]*>([\u4e00-\u9fa5]+)</td>\s*<td[^>]*>([\u4e00-\u9fa5]+)</td>\s*<td[^>]*>([\d.]+)</td>'
        matches = re.findall(pattern, html_code, re.DOTALL)

        for match in matches[:30]:
            rank, name, province, type_uni, total_score = match
            start = html_code.find(match[0])
            end = min(start + 300, len(html_code))
            block = html_code[start:end]

            tags = []
            if "双一流" in block:
                tags.append("双一流")
            if "985" in block:
                tags.append("985")
            if "211" in block:
                tags.append("211")
            tags_str = " | ".join(tags) if tags else "N/A"

            all_universities.append([rank, name, tags_str, province, type_uni, total_score])
            print(f"正则提取: {rank} - {name} - 总分: {total_score}")

except Exception as e:
    print(f"爬取出错: {str(e)}")
    import traceback

    traceback.print_exc()

# 直接写入爬取到的原始数据
if all_universities:
    with open("top30_universities_with_score.csv", 'w', newline='', encoding='utf-8-sig') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["排名", "大学名称", "标签", "省份", "类型", "总分"])

        # 按排名排序
        all_universities.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 999)
        csv_writer.writerows(all_universities)

    print(f"\n爬取完成，共保存 {len(all_universities)} 所大学数据到 top30_universities_with_score.csv")

    print("\n数据预览（纯爬虫数据，无备份补充）:")
    print("-" * 90)
    print(f"{'排名':<4} {'大学名称':<12} {'标签':<18} {'省份':<6} {'类型':<6} {'总分':<8}")
    print("-" * 90)

    # 统计缺失数据
    missing_scores = 0
    missing_provinces = 0
    missing_types = 0

    for uni in all_universities[:30]:
        print(f"{uni[0]:<4} {uni[1]:<12} {uni[2]:<18} {uni[3]:<6} {uni[4]:<6} {uni[5]:<8}")

        if uni[5] == "N/A":
            missing_scores += 1
        if uni[3] == "N/A":
            missing_provinces += 1
        if uni[4] == "N/A":
            missing_types += 1

    print("-" * 90)
    print(f"\n数据完整性统计:")
    print(f"  总分缺失: {missing_scores} 条")
    print(f"  省份缺失: {missing_provinces} 条")
    print(f"  类型缺失: {missing_types} 条")

    if missing_scores > 0 or missing_provinces > 0 or missing_types > 0:
        print("\n⚠️ 注意: 部分数据缺失，建议检查:")
        print("  1. debug_page.html 文件查看实际页面结构")
        print("  2. 网页是否包含所需数据")
        print("  3. 选择器是否需要调整")
else:
    print("未获取到任何数据，请检查网络连接或网站结构")

print("\n开始数据分析和可视化")
print("=" * 60)


# def setup_visualization():
#     plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
#     plt.rcParams['axes.unicode_minus'] = False
#     plt.style.use('seaborn-v0_8-darkgrid')
#
#
# setup_visualization()
def setup_visualization():
    # 1. 必须先应用主题样式（否则会覆盖掉后面的字体设置）
    plt.style.use('seaborn-v0_8-darkgrid')

    # 2. 然后再配置中文字体和负号
    # 加入了 macOS 的 PingFang SC 以增加跨平台兼容性
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'PingFang SC', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False


setup_visualization()

try:
    df = pd.read_csv("top30_universities_with_score.csv", encoding='utf-8-sig')
    print(f"成功读取数据，共 {len(df)} 条记录")

    # 数据预处理：将"N/A"转换为NaN，确保总分是数值类型
    df['总分'] = pd.to_numeric(df['总分'], errors='coerce')

    print("\n生成各省份Top30大学数量对比饼图...")
    # 过滤掉省份为N/A的数据
    df_valid_province = df[df['省份'] != 'N/A']
    province_counts = df_valid_province['省份'].value_counts()

    if len(province_counts) > 0:
        colors = plt.cm.Set3(np.linspace(0, 1, len(province_counts)))

        fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        wedges, texts, autotexts = ax1.pie(province_counts.values, labels=province_counts.index,
                                           colors=colors, autopct='%1.1f%%', startangle=90)
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
        ax1.set_title('各省份Top30大学数量分布', fontsize=14, fontweight='bold', pad=20)
        ax1.axis('equal')

        bars = ax2.bar(range(len(province_counts)), province_counts.values, color=colors)
        ax2.set_title('各省份Top30大学数量（精确值）', fontsize=14, fontweight='bold', pad=20)
        ax2.set_xlabel('省份')
        ax2.set_ylabel('大学数量')
        ax2.set_xticks(range(len(province_counts)))
        ax2.set_xticklabels(province_counts.index, rotation=45, ha='right')
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width() / 2., height + 0.1, f'{int(height)}',
                     ha='center', va='bottom', fontweight='bold')
        plt.tight_layout()
        plt.savefig('省份大学数量分布.png', dpi=300, bbox_inches='tight')
        plt.show()
    else:
        print("  无有效的省份数据，跳过此图表")

    print("生成各省份Top30大学总分对比柱状图...")
    # 过滤掉总分或省份为N/A的数据
    df_valid_score = df[(df['总分'].notna()) & (df['省份'] != 'N/A')]

    if len(df_valid_score) > 0:
        province_scores = df_valid_score.groupby('省份')['总分'].sum().sort_values(ascending=False)

        if len(province_scores) > 0:
            fig2, ax3 = plt.subplots(figsize=(14, 8))
            score_colors = plt.cm.YlOrRd(np.linspace(0.4, 0.9, len(province_scores)))
            bars2 = ax3.bar(province_scores.index, province_scores.values, color=score_colors, edgecolor='black')
            ax3.set_title('各省份Top30大学总分对比', fontsize=16, fontweight='bold', pad=20)
            ax3.set_xlabel('省份', fontsize=12)
            ax3.set_ylabel('总分（求和）', fontsize=12)
            ax3.tick_params(axis='x', rotation=45)
            for i, bar in enumerate(bars2):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width() / 2., height + 20, f'{height:.1f}',
                         ha='center', va='bottom', fontweight='bold', fontsize=10)
            avg_score = province_scores.mean()
            ax3.axhline(y=avg_score, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
            ax3.text(len(province_scores) - 0.5, avg_score + 20, f'平均: {avg_score:.1f}',
                     color='red', fontweight='bold', va='center')
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.savefig('各省份大学总分对比.png', dpi=300, bbox_inches='tight')
            plt.show()
        else:
            print("  无有效的省份总分数据，跳过此图表")
    else:
        print("  无有效的总分数据，跳过此图表")

    print("生成各省份Top30大学类别分布柱状图...")
    # 过滤掉省份或类型为N/A的数据
    df_valid_type = df[(df['省份'] != 'N/A') & (df['类型'] != 'N/A')]

    if len(df_valid_type) > 0:
        cross_tab = pd.crosstab(df_valid_type['省份'], df_valid_type['类型'])
        provinces_with_data = df_valid_type['省份'].value_counts().index
        cross_tab = cross_tab.loc[provinces_with_data]

        if len(cross_tab) > 0:
            fig3, ax4 = plt.subplots(figsize=(16, 9))
            categories = cross_tab.columns.tolist()
            provinces = cross_tab.index.tolist()
            type_colors = {
                '综合': '#1f77b4', '理工': '#ff7f0e', '师范': '#2ca02c',
                '农业': '#d62728', '医药': '#9467bd', '财经': '#8c564b',
                '政法': '#e377c2', '艺术': '#7f7f7f', '体育': '#bcbd22',
                '民族': '#17becf'
            }
            bottom = np.zeros(len(provinces))
            for i, type_name in enumerate(categories):
                color = type_colors.get(type_name, plt.cm.tab20(i / len(categories)))
                values = cross_tab[type_name].values
                ax4.bar(provinces, values, bottom=bottom, label=type_name, color=color,
                        edgecolor='white', width=0.7)
                for j, value in enumerate(values):
                    if value > 0:
                        ax4.text(j, bottom[j] + value / 2, str(int(value)),
                                 ha='center', va='center', fontsize=9, fontweight='bold', color='white')
                bottom += values
            ax4.set_title('各省份Top30大学类型分布', fontsize=16, fontweight='bold', pad=20)
            ax4.set_xlabel('省份', fontsize=12)
            ax4.set_ylabel('大学数量', fontsize=12)
            ax4.tick_params(axis='x', rotation=45)
            ax4.legend(title='大学类型', bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.tight_layout()
            plt.savefig('各省份大学类型分布.png', dpi=300, bbox_inches='tight')
            plt.show()
        else:
            print("  无有效的类型分布数据，跳过此图表")
    else:
        print("  无有效的类型数据，跳过此图表")

    print("\n" + "=" * 60)
    print("数据统计摘要（纯爬虫数据）")
    print("=" * 60)

    print(f"\nTop30大学基本统计:")
    print(f"  大学总数: {len(df)}")
    print(f"  涉及省份数: {df[df['省份'] != 'N/A']['省份'].nunique()} (有效)")
    print(f"  大学类型数: {df[df['类型'] != 'N/A']['类型'].nunique()} (有效)")
    print(f"  有效总分数量: {df['总分'].notna().sum()} / {len(df)}")

    valid_scores = df['总分'].dropna()
    if len(valid_scores) > 0:
        print(f"  平均总分: {valid_scores.mean():.1f}")
        print(f"  总分范围: {valid_scores.min():.1f} - {valid_scores.max():.1f}")

    print(f"\n各省份表现（仅统计有效数据）:")
    print("-" * 40)
    for province, count in province_counts.items() if 'province_counts' in locals() and len(
            province_counts) > 0 else []:
        province_data = df[df['省份'] == province]
        valid_scores_province = province_data['总分'].dropna()
        if len(valid_scores_province) > 0:
            avg_score = valid_scores_province.mean()
            print(f"  {province:5}：{count:2}所大学，有效总分{len(valid_scores_province)}所，平均分：{avg_score:.1f}")
        else:
            print(f"  {province:5}：{count:2}所大学，无有效总分数据")

    print(f"\n大学类型分布:")
    print("-" * 40)
    type_counts = df[df['类型'] != 'N/A']['类型'].value_counts()
    for type_name, count in type_counts.items():
        percentage = count / len(df[df['类型'] != 'N/A']) * 100
        print(f"  {type_name:5}：{count:2}所（{percentage:.1f}%）")

    print(f"\n已生成的可视化文件:")
    print("  1. 省份大学数量分布.png")
    print("  2. 各省份大学总分对比.png")
    print("  3. 各省份大学类型分布.png")

except Exception as e:
    print(f"数据分析和可视化过程中出错: {str(e)}")
    import traceback

    traceback.print_exc()

print("\n数据分析和可视化完成！")
print("注意：以上数据完全来自爬虫，未使用任何备份数据补充")