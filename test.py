from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import os

def safe_get(data, *keys, default="暂无"):
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, IndexError):
            return default
    return data

def save_to_excel(data_list, filename="商品数据.xlsx"):
    if not data_list:
        print("没有需要保存的数据")
        return

    # 创建DataFrame并去重
    df = pd.DataFrame(data_list).drop_duplicates(subset=["商品链接"], keep="first")
    
    # 设置输出路径（桌面）
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    filepath = os.path.join(desktop, filename)
    
    # 使用xlsxwriter引擎
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='商品列表')
    
    # 获取工作表对象
    workbook = writer.book
    worksheet = writer.sheets['商品列表']
    
    # 设置标题格式
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
        '当前售价': 15,
        '发货地区': 15,
        '卖家昵称': 20,
        '商品链接': 60,
        '商品图片链接': 60,  # 新增列宽设置
        '发布时间': 20
    }
    
    # 应用格式
    for col_num, (col_name, width) in enumerate(col_widths.items()):
        worksheet.set_column(col_num, col_num, width)
    
    # 设置标题行格式
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    writer.close()
    print(f"数据已保存到：{filepath}")

def scrape_xianyu(keyword, max_pages=1):
    data_list = []  # 统一存储所有数据
    
    def on_response(response):
        if "h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search" in response.url:
            try:
                result_json = response.json()
                items = result_json.get("data", {}).get("resultList", [])
                
                for item in items:
                    main_data = safe_get(item, "data", "item", "main", "exContent", default={})
                    click_params = safe_get(item, "data", "item", "main", "clickParam", "args", default={})
                    
                    # 解析商品信息
                    title = safe_get(main_data, "title", default="未知标题")
                    
                    # 价格处理
                    price_parts = safe_get(main_data, "price", default=[])
                    if isinstance(price_parts, list):
                        price = "".join([str(p.get("text", "")) for p in price_parts if isinstance(p, dict)])
                    else:
                        price = "价格异常"

                    if "当前价" in price:
                        price = price.replace("当前价", "")
                    
                    if "万" in price:
                        price = "¥" + str(int(float(price.replace("¥", "").replace("万", "")) * 10000))

                    # 其他信息
                    area = safe_get(main_data, "area", default="地区未知")
                    seller = safe_get(main_data, "userNickName", default="匿名卖家")
                    
                    # 链接处理
                    raw_link = safe_get(item, "data", "item", "main", "targetUrl", default="")
                    clean_link = raw_link.replace("fleamarket://", "https://www.goofish.com/")
                    
                    # 新增图片链接获取
                    image_url = safe_get(main_data, "picUrl", default="")
                    if image_url and not image_url.startswith("http"):
                        image_url = f"https:{image_url}"
                    
                    # 时间转换
                    publish_time = safe_get(click_params, "publishTime", default="")
                    publish_date = "未知时间"
                    if publish_time.isdigit():
                        try:
                            dt = datetime.fromtimestamp(int(publish_time)/1000)
                            publish_date = dt.strftime("%Y-%m-%d %H:%M")
                        except:
                            pass
                    
                    data_list.append({
                        "商品标题": title,
                        "当前售价": price,
                        "发货地区": area,
                        "卖家昵称": seller,
                        "商品链接": clean_link,
                        "商品图片链接": image_url,  # 新增图片链接字段
                        "发布时间": publish_date
                    })

            except Exception as e:
                print(f"数据处理异常: {str(e)}")


    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # 访问闲鱼首页
            page.goto("https://www.goofish.com")
            # page.wait_for_timeout(1000)
            # page.wait_for_selector('input[class*="search-input"]', timeout=10000)

            # 如果页面有包含closeIconBg的元素，说明有弹窗广告，点击关闭
            try:
                page.click("[class*='closeIconBg']", timeout=1000)
            except:
                pass

            # 执行搜索
            print("正在搜索商品，请稍等...")
            page.fill('input[class*="search-input"]', keyword)
            page.click('button[type="submit"]')

            # 设置最新排序
            page.click('text=新发布')
            page.click('text=最新')

            # 注册响应监听
            page.on("response", on_response)

            # 分页爬取
            current_page = 1
            while current_page <= max_pages:
                print(f"正在处理第 {current_page}/{max_pages} 页...")
                
                try:
                    page.wait_for_selector("[class*='search-pagination-container']", timeout=1000)
                except:
                    print("未找到分页器，可能只有单页结果")
                    break

                try:
                 # 查找下一页按钮，div class属性字段中包括search-pagination-arrow-right
                    next_btn = page.query_selector("[class*='search-pagination-arrow-right']")
                
                # 如果没有找到下一页按钮，或者下一页按钮的cursor为not-allowed，则终止爬取
                    if (next_btn is None) or ("disabled" in next_btn.get_attribute("class")):
                        print(f"无法找到第 {current_page + 1} 页，终止爬取")
                        break

                    page.click("[class*='search-pagination-arrow-right']", timeout=1000)

                    

                except:
                    print(f"无法找到第 {current_page + 1} 页，终止爬取")
                    current_page += 1
                    break

                current_page += 1
                
                # 等待新页面加载
                # page.wait_for_timeout(1000)
                
                
            # 最终保存数据
            if data_list:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                # 去除keyword中的特殊字符
                keyword = ''.join(e for e in keyword if e.isalnum())
                filename = f"闲鱼爬取结果_{keyword}_共{current_page - 1}页_{timestamp}.xlsx"
                save_to_excel(data_list, filename)
            else:
                print("没有采集到任何商品数据")

        except Exception as e:
            print(f"爬取中断: {str(e)}")
            # 异常时保存已有数据
            if data_list:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                save_to_excel(data_list, f"闲鱼_异常中断_{timestamp}.xlsx")
            page.screenshot(path='xianyu_error.png')
            print("错误截图已保存至目录")

        finally:
            browser.close()

if __name__ == "__main__":
    keyword = input("请输入要搜索的商品关键词：").strip()
    pages = int(input("请输入要爬取的最大页数：").strip() or 1)
    print(f"开始爬取 {keyword} 的前 {pages} 页数据...")
    scrape_xianyu(keyword, max_pages=pages)
    print("爬取任务结束")