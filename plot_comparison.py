import matplotlib.pyplot as plt
import matplotlib as mpl
import csv
import os

# 设置中文字体
mpl.rcParams['font.sans-serif'] = ['Arial Unicode MS']
mpl.rcParams['axes.unicode_minus'] = False

def plot_model_comparison(output_dir='test_results'):
    """从CSV文件读取数据并生成模型性能对比图表"""
    # 读取CSV文件
    csv_path = os.path.join(output_dir, 'speed_ranking.csv')
    if not os.path.exists(csv_path):
        print(f"错误：找不到文件 {csv_path}")
        return

    providers = []
    models = []
    avg_speeds = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            providers.append(row['提供商'])
            models.append(row['模型名称'])
            avg_speeds.append(float(row['平均速率（字符/秒）']))

    if not providers:
        print("错误：CSV文件中没有数据")
        return

    # 创建水平柱状图
    plt.figure(figsize=(10, 8))  # 调整图表尺寸以适应水平布局
    bars = plt.barh(range(len(providers)), avg_speeds)

    # 设置颜色
    colors = ['#2ecc71', '#3498db', '#9b59b6']
    for bar, color in zip(bars, colors[:len(bars)]):
        bar.set_color(color)

    # 添加数值标签
    for i, v in enumerate(avg_speeds):
        plt.text(v + 1, i, f'{v:.2f}', va='center')

    # 自定义Y轴标签
    plt.yticks(range(len(providers)), [f'{p}\n{m}' for p, m in zip(providers, models)])

    # 添加标题和标签
    plt.title('不同模型的平均响应速率对比', fontsize=14, pad=20)
    plt.xlabel('平均速率（字符/秒）', fontsize=12)

    # 添加网格线
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)

    # 调整布局
    plt.tight_layout()

    # 保存图表
    plt.savefig(os.path.join(output_dir, 'speed_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    plot_model_comparison()