import csv
import time
import os
import json
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import markdown2
from openai import OpenAI
from plot_comparison import plot_model_comparison

# 设置中文字体
mpl.rcParams['font.sans-serif'] = ['Arial Unicode MS']
mpl.rcParams['axes.unicode_minus'] = False

def load_models():
    """从CSV文件加载模型配置信息"""
    models = []
    with open('models.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            models.append({
                'provider': row['provider'],
                'base_url': row['base_url'],
                'model_name': row['model_name'],
                'api_key': row['api_key'],
                'price_per_1k_tokens': row['price_per_1k_tokens']
            })
    return models

def test_model(model_info, test_prompt):
    """测试单个模型的性能"""
    client = OpenAI(
        api_key=model_info['api_key'],
        base_url=model_info['base_url']
    )
    
    start_time = time.time()
    first_token_time = None
    total_chars = 0
    timestamps = []
    token_speeds = []
    last_time = start_time
    last_chars = 0
    full_response = ""

    response = client.chat.completions.create(
        model=model_info['model_name'],
        messages=[{'role': 'user', 'content': test_prompt}],
        stream=True
    )
    
    for chunk in response:
        current_time = time.time()
        content = chunk.choices[0].delta.content
        if content:
            if first_token_time is None:
                first_token_time = current_time
            total_chars += len(content)
            full_response += content
            
            time_diff = current_time - last_time
            if time_diff >= 0.1:
                char_diff = total_chars - last_chars
                current_speed = char_diff / time_diff
                timestamps.append(current_time - start_time)
                token_speeds.append(current_speed)
                last_time = current_time
                last_chars = total_chars
    
    end_time = time.time()
    
    return {
        'provider': model_info['provider'],
        'model_name': model_info['model_name'],
        'first_token_latency': (first_token_time - start_time) * 1000 if first_token_time else 0,
        'total_time': end_time - start_time,
        'average_speed': total_chars / (end_time - start_time) if end_time > start_time else 0,
        'total_chars': total_chars,
        'response_text': full_response,
        'timestamps': timestamps,
        'token_speeds': token_speeds,
        'price_per_1k_tokens': model_info['price_per_1k_tokens']
    }

def plot_speed_curve(results, output_dir):
    """绘制速率曲线并保存"""
    plt.figure(figsize=(10, 6))
    plt.plot(results['timestamps'], results['token_speeds'], 
            color='tab:blue', label=f"{results['model_name']}")
    
    plt.xlabel('时间 (秒)')
    plt.ylabel('Token速率 (字符/秒)')
    plt.title(f"{results['provider']} - {results['model_name']} 响应速率曲线")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    output_path = os.path.join(output_dir, f"{results['provider']}_{results['model_name'].replace('/', '_')}.png")
    plt.savefig(output_path)
    plt.close()

def save_results(all_results, output_dir):
    """保存测试结果"""
    with open(os.path.join(output_dir, 'detailed_results.json'), 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    summary_data = []
    for result in all_results:
        summary_data.append({
            'provider': result['provider'],
            'model_name': result['model_name'],
            'average_speed': result['average_speed'],
            'first_token_latency': result['first_token_latency'],
            'total_time': result['total_time'],
            'total_chars': result['total_chars'],
            'price_per_1k_tokens': result['price_per_1k_tokens']
        })
    
    with open(os.path.join(output_dir, 'speed_ranking.csv'), 'w', encoding='utf-8') as f:
        f.write('提供商,模型名称,平均速率（字符/秒）,首个token延迟（ms）,总用时（秒）,总字符数,每千token价格\n')
        for data in sorted(summary_data, key=lambda x: x['average_speed'], reverse=True):
            f.write(f"{data['provider']},{data['model_name']},{data['average_speed']:.2f},{data['first_token_latency']:.2f},{data['total_time']:.2f},{data['total_chars']},{data['price_per_1k_tokens']}\n")

def analyze_results(data):
    """使用第一个模型分析测试结果并生成报告"""
    # 从models.csv加载第一个模型的配置
    with open('models.csv', 'r') as file:
        reader = csv.DictReader(file)
        model_config = next(reader)
    
    # 使用模型配置创建客户端
    client = OpenAI(
        base_url=model_config['base_url'],
        api_key=model_config['api_key']
    )
    
    # 准备提示词
    prompt = f"""请分析以下LLM性能测试数据并生成一篇专业的分析报告。数据如下：

{data.to_string()}

请从以下几个方面进行分析：
1. 各模型的性能对比（包括速度、延迟等指标）
2. 价格效益分析
3. 综合评估和建议

请用Markdown格式输出分析报告。"""

    # 调用API
    response = client.chat.completions.create(
        model=model_config['model_name'],
        messages=[
            {"role": "system", "content": "你是一个专业的AI性能分析师，擅长数据分析和撰写技术报告。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def generate_html(markdown_content):
    """将Markdown内容转换为HTML，使用markdown2提供更好的表格支持"""
    html_content = markdown2.markdown(markdown_content, extras=['tables', 'fenced-code-blocks'])
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LLM性能测试分析报告</title>
        <style>
            :root {{
                --primary-color: #2c3e50;
                --border-color: #e1e4e8;
                --bg-color: #ffffff;
                --text-color: #24292e;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                max-width: 1000px;
                margin: 0 auto;
                padding: 2rem;
                color: var(--text-color);
                background-color: var(--bg-color);
            }}
            h1, h2, h3 {{
                color: var(--primary-color);
                margin-top: 2rem;
                margin-bottom: 1rem;
            }}
            table {{
                border-collapse: separate;
                border-spacing: 0;
                width: 100%;
                margin: 2rem 0;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            th, td {{
                border: 1px solid var(--border-color);
                padding: 12px 16px;
                text-align: left;
            }}
            th {{
                background-color: #f6f8fa;
                font-weight: 600;
                border-bottom: 2px solid var(--border-color);
            }}
            tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            tr:hover {{
                background-color: #f1f4f8;
            }}
            code {{
                background-color: #f6f8fa;
                padding: 0.2em 0.4em;
                border-radius: 3px;
                font-family: SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
            }}
            pre {{
                background-color: #f6f8fa;
                padding: 16px;
                border-radius: 8px;
                overflow-x: auto;
            }}
            @media (max-width: 768px) {{
                body {{
                    padding: 1rem;
                }}
                table {{
                    display: block;
                    overflow-x: auto;
                    -webkit-overflow-scrolling: touch;
                }}
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return html_template

def main():
    output_dir = 'test_results'
    os.makedirs(output_dir, exist_ok=True)
    
    test_prompt = "给我写一篇1000字的如何利用大模型加速自媒体创作者效率的博文。"
    models = load_models()
    all_results = []
    
    print("开始性能测试...\n")
    for model in models:
        print(f"测试 {model['provider']} 的 {model['model_name']}...")
        try:
            result = test_model(model, test_prompt)
            all_results.append(result)
            
            print(f"首个token延迟: {result['first_token_latency']:.2f}ms")
            print(f"平均速率: {result['average_speed']:.2f}字符/秒")
            print(f"总用时: {result['total_time']:.2f}秒")
            print(f"总字符数: {result['total_chars']}")
            print(f"价格说明: {result['price_per_1k_tokens']}")
            print(f"回答: {result['response_text']}\n")
            
            plot_speed_curve(result, output_dir)
        except Exception as e:
            print(f"测试失败: {str(e)}\n")
    
    save_results(all_results, output_dir)
    plot_model_comparison(output_dir)
    
    # 读取测试结果并生成分析报告
    df = pd.read_csv(os.path.join(output_dir, 'speed_ranking.csv'), encoding='utf-8')
    markdown_content = analyze_results(df)
    
    # 保存Markdown文件
    with open(os.path.join(output_dir, 'analysis_report.md'), 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    # 生成并保存HTML文件
    html_content = generate_html(markdown_content)
    with open(os.path.join(output_dir, 'analysis_report.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("\n所有测试完成，结果已保存到test_results目录")

if __name__ == "__main__":
    main()