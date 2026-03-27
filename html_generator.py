#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML生成器 - 通用的HTML页面生成功能
"""

from datetime import datetime


class HTMLGenerator:
    """HTML页面生成器"""
    
    def __init__(self):
        self.base_styles = """
        body {
            font-family: 'Microsoft YaHei', 'SimHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .chart-container {
            margin: 30px 0;
            text-align: center;
        }
        .chart-container img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .purchase-links {
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            padding: 20px;
            margin-top: 30px;
        }
        .purchase-links h3 {
            margin-top: 0;
            color: #856404;
        }
        .purchase-links ul {
            list-style: none;
            padding: 0;
        }
        .purchase-links li {
            padding: 10px 0;
            border-bottom: 1px solid #ffeeba;
        }
        .purchase-links li:last-child {
            border-bottom: none;
        }
        .purchase-links a {
            display: inline-block;
            margin: 0 5px;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
            transition: all 0.3s;
        }
        .purchase-links a:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .link-京东 {
            background-color: #e4393c;
            color: white;
        }
        .link-京东:hover {
            background-color: #c92a2d;
        }
        .link-天猫 {
            background-color: #ff0036;
            color: white;
        }
        .link-天猫:hover {
            background-color: #d9002e;
        }
        .link-淘宝 {
            background-color: #ff5000;
            color: white;
        }
        .link-淘宝:hover {
            background-color: #d94000;
        }
        .link-拼多多 {
            background-color: #e02e24;
            color: white;
        }
        .link-拼多多:hover {
            background-color: #bf261e;
        }
        .link-官方 {
            background-color: #2196F3;
            color: white;
        }
        .link-官方:hover {
            background-color: #1976D2;
        }
        .link-其他 {
            background-color: #9E9E9E;
            color: white;
        }
        .link-其他:hover {
            background-color: #757575;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 14px;
        }
        """
        
        self.platform_colors = {
            '京东': '#e4393c',
            '天猫': '#ff0036',
            '淘宝': '#ff5000',
            '拼多多': '#e02e24',
            '官方': '#2196F3',
            '官方商城': '#2196F3',
            '苏宁': '#F90',
            '其他': '#9E9E9E'
        }
    
    def _generate_platform_styles(self):
        """生成平台样式"""
        styles = ""
        for platform, color in self.platform_colors.items():
            hover_color = self._darken_color(color)
            styles += f"""
        .link-{platform} {{
            background-color: {color};
            color: white;
        }}
        .link-{platform}:hover {{
            background-color: {hover_color};
        }}
"""
        return styles
    
    def _darken_color(self, hex_color):
        """加深颜色"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * 0.85)) for c in rgb)
        return f'#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}'
    
    def generate_html_header(self, title):
        """生成HTML头部"""
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
{self.base_styles}
{self._generate_platform_styles()}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
"""
    
    def generate_html_footer(self, extra_info=None):
        """生成HTML尾部"""
        footer = f"""
        <div class="footer">
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>所有数据都是从网络实时获取的真实数据</p>
"""
        if extra_info:
            footer += f"            <p>{extra_info}</p>\n"
        
        footer += """        </div>
    </div>
</body>
</html>
"""
        return footer
    
    def generate_chart_section(self, chart_files):
        """生成图表部分"""
        sections = ""
        for chart_file in chart_files:
            chart_name = chart_file if isinstance(chart_file, str) else chart_file.name
            sections += f"""        <div class='chart-container'>
            <img src='{chart_name}' alt='{chart_name}'>
        </div>
"""
        return sections
    
    def generate_purchase_links_section(self, items, link_key='purchase_links', name_format=None):
        """生成购买链接部分"""
        html = """<div class='purchase-links'>
<h3>🔗 购买链接</h3>
<ul>
"""
        
        for i, item in enumerate(items, 1):
            links = item.get(link_key, {})
            if links:
                if name_format:
                    name = name_format(item)
                else:
                    name = f"{item.get('brand', '')} {item.get('model', '')}"
                
                html += f"<li><strong>{i}. {name}</strong>: "
                for platform, link in links.items():
                    html += f"<a href='{link}' target='_blank' class='link-{platform}'>{platform}</a> "
                html += "</li>\n"
        
        html += """</ul>
</div>
"""
        return html
    
    def generate_html_page(self, title, chart_files=None, items=None, link_key='purchase_links', name_format=None, extra_info=None):
        """生成完整的HTML页面"""
        html = self.generate_html_header(title)
        
        if chart_files:
            html += self.generate_chart_section(chart_files)
        
        if items:
            html += self.generate_purchase_links_section(items, link_key, name_format)
        
        html += self.generate_html_footer(extra_info)
        
        return html
    
    def save_html(self, html, output_file):
        """保存HTML文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            return True
        except Exception as e:
            print(f"保存HTML文件失败: {e}")
            return False