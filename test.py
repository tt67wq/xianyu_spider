from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

def safe_get(data, *keys, default="暂无"):
    """安全获取嵌套字典值"""
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError):
            return default
    return data

def save_to_excel(data_list, filename="商品数据.xlsx"):
    """保存数据到Excel文件"""
    df = pd.DataFrame(data_list)
    
    # 设置输出路径（桌面）
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    filepath = os.path.join(desktop, filename)
    
    # 使用xlsxwriter引擎美化格式
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='商品列表')
    
    # 获取工作表对象
    workbook = writer.book
    worksheet = writer.sheets['商品列表']
    
    # 设置格式
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'fg_color': '#4F81BD',
        'font_color': 'white',
        'border': 1
    })
    
    # 设置列宽（字符单位）
    col_widths = {
        '商品标题': 50,
        '当前售价': 12,
        '发货地区': 12,
        '卖家昵称': 20,
        '商品链接': 60,
        '发布时间': 18
    }
    
    # 应用格式
    for col_num, (col_name, width) in enumerate(col_widths.items()):
        worksheet.set_column(col_num, col_num, width)
    
    # 设置标题行格式
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    writer.close()
    print(f"\n数据已保存到：{filepath}")

def on_response(response):
    data_list = []  # 用于收集所有商品数据
    
    if "https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/" in response.url:
        try:
            result_json = response.json()
            items = result_json.get("data", {}).get("resultList", [])
            
            for item in items:
                main_data = safe_get(item, "data", "item", "main", "exContent", default={})
                click_params = safe_get(item, "data", "item", "main", "clickParam", "args", default={})
                
                # 商品基础信息
                title = safe_get(main_data, "title", default="未知标题")
                
                # 价格处理
                price_parts = safe_get(main_data, "price", default=[])
                price = "".join([p.get("text", "") for p in price_parts if isinstance(p, dict)])
                
                # 地区信息
                area = safe_get(main_data, "area", default="地区未知")
                
                # 卖家信息
                seller = safe_get(main_data, "userNickName", default="匿名卖家")
                
                # 商品链接
                raw_link = safe_get(item, "data", "item", "main", "targetUrl", default="")
                clean_link = raw_link.split("?")[0] if raw_link else ""
                
                # 发布时间（时间戳转换）
                publish_time = safe_get(click_params, "publishTime", default="")
                if publish_time.isdigit():
                    dt = datetime.fromtimestamp(int(publish_time)/1000)
                    publish_date = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    publish_date = "未知时间"
                
                # 收集数据
                data_list.append({
                    "商品标题": title,
                    "当前售价": price if price != "" else "价格未知",
                    "发货地区": area,
                    "卖家昵称": seller,
                    "商品链接": clean_link,
                    "发布时间": publish_date
                })
            
            # 每次响应都保存最新数据（可选实时保存）
            if data_list:
                save_to_excel(data_list, filename=f"闲鱼商品_{datetime.now().strftime('%Y%m%d%H%M')}.xlsx")
                
        except Exception as e:
            print(f"处理数据时发生错误: {str(e)}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    try:
        # 访问页面
        page.goto("https://www.goofish.com", wait_until="networkidle")
        
        # 输入搜索词
        page.fill('input[class="search-input--WY2l9QD3"]', "iphone13mini")
        # 注册响应事件
        page.on("response", on_response)
        # 点击搜索按钮
        page.click('button[type="submit"]')
        page.wait_for_timeout(3000)
        
    except Exception as e:
        # 错误处理
        print(f"发生错误: {str(e)}")
        page.screenshot(path='error_screenshot.png')
        print("已保存错误截图：error_screenshot.png")
        
    finally:
        browser.close()