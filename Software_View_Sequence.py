# 导入模块
import os
import sys
import re
import json
# 检查软件包
packages = {'requests': 'requests','pymysql': 'pymysql','selenium': 'selenium'}
missing = []
# 遍历检查
for name, install_name in packages.items():
    try:
        __import__(name)
        print(f"{name} installed")
    except ImportError:
        print(f"{name} not installed")
        missing.append(install_name)
# 检查结果
if missing:
    print(f"\n{len(missing)} packages are missing")
    print(f"Please run: pip install {' '.join(missing)}")
    sys.exit(1)
else:
    print("The required packages have been installed\n")

import requests
import pymysql
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
from time import sleep,localtime,strftime
# 初始参数
url='https://bbsmc.net/'
cookie_flag=False
# 执行时间
now = localtime()
print(f"Code run time:{strftime('%Y年%m月%d日 %H:%M:%S', now)}")

#初始化
# 连接数据库
try:
    connection=pymysql.connect(host='localhost',port=3306,user="root",password="")
    print("Primary:Mysql connect success")
    cursor=connection.cursor()
    print("Primary:Cursor create success")
    cursor.execute('drop database if exists softwarel')
    cursor.execute('create database softwarel')
    print("Primary:Database reset success")
    cursor.execute('use softwarel')
    cursor.execute('create table softwares('
                'name varchar(200),'
                'ico_url varchar(200),'
                'creater varchar(50),'
                'download varchar(10),'
                'upgrade_time varchar(50),'
                'intorduction varchar(300)'
                ')charset=utf8mb4 collate=utf8mb4_unicode_ci' )
    connection.commit()
    print("Primary:Table create success")
except pymysql.OperationalError as e:
    code=e.args[0] if e.args else 0
    message=e.args[1] if e.args else str("")
    print(f"Error code {code}\nError: {e}")
    print("Quit,plaease change the mysql username and password")
    sys.exit()
# 创建img文件夹
if os.path.exists('img'):
    for i in os.listdir('img'):
        os.remove(os.path.join('img',i))
    print('Dir(img) is exist')
else:
    os.mkdir('img')
    print('Dir(img) create success')
# 创建analysis文件夹
folder_name = 'analysis'
if not os.path.exists(folder_name):
    os.mkdir(folder_name)
    print('Dir(analysis) is exist')
else:
    print('Dir(analysis) create success')
# driver路径
driver1_path=r".\driver\Firefox\geckodriver.exe"
# 驱动
service=Service(executable_path=driver1_path)
driver=webdriver.Firefox(service=service)
# cookie处理
if not os.path.exists("Cookie.json"):
    print("File Cookie.json not found,please manual login or get cookie to Cookie.json first")
else:
    cookie_flag=True
if cookie_flag:
    try:
        with open("Cookie.json","r",encoding="utf-8") as f:
            cookies=json.loads(f.read())
    except Exception as e:
        print("Error:Cookie.json is not available,please manual login or get right cookie to Cookie.json first")
        cookie_flag=False
        print("Error:",e)
print("Primary:Done!")

#访问并操作
driver.get(url)
login_flag=False
# 登录
if cookie_flag:
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"cookie {cookie['name']} add failed:", e)
    driver.refresh()
    sleep(3)
    if driver.find_elements(By.CLASS_NAME,"user-menu"):
        print("Cookie login success")
        login_flag=True
    else:
        print("Cookie login failed,please manual login")
if not login_flag:
    driver.find_element(By.LINK_TEXT,'登录').click()
    while True:
        try:
            WebDriverWait(driver,10,2).until(EC.presence_of_element_located((By.ID,'email')))
        except TimeoutException:
            print("Timeout,please check your network")
            driver.quit()
            sys.exit()
        driver.find_element(By.ID,'email').clear()
        driver.find_element(By.ID,'email').send_keys(input("Account:"))
        driver.find_element(By.ID,'password').clear()
        driver.find_element(By.ID,'password').send_keys(input("Password:"))
        driver.find_element(By.CSS_SELECTOR,'.captcha-btn.captcha-btn-start').click()
        while True:
            try:
                WebDriverWait(driver,30,5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.btn.btn-primary.continue-btn.full-width-btn')))
                driver.find_element(By.CSS_SELECTOR,'.btn.btn-primary.continue-btn.full-width-btn').click()
                break
            except TimeoutException:
                print("Login timeout,again")
        sleep(5)
        if driver.find_elements(By.CLASS_NAME,'vue-notification-wrapper'):
            print("Account or password error,please check your account and password")
            if input("Do you want to continue trying to login? (y/n)")!="n":
                continue
            else:
                print("Quit")
                driver.quit()
                sys.exit()
        else:
            print("Login success!")
            login_flag=True
            # 保存cookie
            with open("Cookie.json", "w", encoding="utf-8") as f:
                driver_cookies = driver.get_cookies()
                cookies=[]
                n={"domain":"bbsmc.net","path":"/"}
                for i in driver_cookies:
                    d={}
                    d["name"]=i["name"]
                    d["value"]=i["value"]
                    d.update(n)
                    cookies.append(d)
                f.write(json.dumps(cookies))
            print("Cookie saved to Cookie.json")
            break
#s_name为所要爬取的页面
sleep(5)
s_name='软件'
driver.find_element(By.LINK_TEXT,s_name).click()
sleep(5)
body = driver.find_element(By.TAG_NAME, "body")
# 最大页数
page_max=3
# 页数容器
n=0
driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
page_t =int(driver.find_elements(By.CLASS_NAME,"page-number-container")[-1].text)
print(f"Page total:{page_t}")
if page_t>page_max:
    page_t=page_max
sleep(2)
name_l=[]
while True:
    # 检测页数
    page_contians=driver.find_elements(By.CLASS_NAME,"page-number-container")
    page_contians[n].click()
    # 容器数量检测
    if len(page_contians)>=7:
        n-=1
    #初始到顶部
    driver.execute_script("window.scrollTo(0, 0)")
    sleep(5)
    # 循环检测，到底部停止
    while True:
        # 检测是否到底部
        is_bottom = driver.execute_script("""
            var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            var scrollHeight = document.body.scrollHeight;
            var windowHeight = window.innerHeight;
            return (scrollTop + windowHeight) >= scrollHeight - 10;
        """)
        try:
            softwares = driver.find_elements(By.CSS_SELECTOR, '.project-card.base-card.padding-bg')
            for i in softwares:  # 获取信息
                name = i.find_element(By.TAG_NAME, 'h2').text
                safe_name = name.replace('|', '_').replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_')
                if safe_name in name_l:
                    continue
                else:
                    name_l.append(safe_name)
                    urls = i.find_elements(By.TAG_NAME, "img")
                    if len(urls) == 0:
                        continue
                    url = urls[0].get_attribute('src')
                    if not url:
                        continue
                    print(f"Download:{url}")
                    with open(rf".\img\{safe_name}.webp", 'wb') as f:
                        f.write(requests.get(url).content)
                    print("Done!")
                    url_path = rf"./img/{safe_name}.webp"
                    creaters = i.find_elements(By.CLASS_NAME, 'title-link')
                    if len(creaters)==0:
                        creater = "未知作者"
                    else:
                        creater=creaters[0].text
                    download = i.find_elements(By.TAG_NAME, 'strong')[0].text
                    updatetime = ''.join(i.find_element(By.CSS_SELECTOR, '.stat.date.v-popper--has-tooltip').text.replace('\n', '').replace('\r', '').split())
                    describe = i.find_element(By.CLASS_NAME, 'description').text.replace('\\','/')
                    sql = 'insert into softwares values(%s, %s, %s, %s, %s, %s)'
                    cursor.execute(sql, (safe_name, url_path, creater, download, updatetime, describe))
                    print(f"Save:{safe_name}")
                    connection.commit()
        except Exception as e:
            print("Error_get_information:", e)
            pass
        if is_bottom:
            break
        body.send_keys(Keys.PAGE_DOWN)
        sleep(2)
    # 限制可爬页数
    page_contians = driver.find_elements(By.CLASS_NAME, "page-number-container")
    if n!=0:
        n_page=int(page_contians[n].text)
        if n_page==page_t:
            break
    # 翻页
    n+=1
#退出
sleep(5)
cursor.close()
print("Cursor closed")
connection.close()
print("Connection closed")
driver.quit()
print("Web closed")
# 可视化
# 获取数据
conn = pymysql.connect(host='localhost',port=3306,user='root',password='',database='softwarel')
cursor = conn.cursor()
cursor.execute("select name, creater, download, upgrade_time, ico_url from softwares")
data = cursor.fetchall()
conn.close()
# 数据统计
total = len(data)
# 下载量处理
downloads = []
for row in data:
    val = row[2]
    if '万' in val:
        val = float(val.replace('万', '')) * 10000
    else:
        val = float(val.replace(',', ''))
    downloads.append(val)
# 总下载量
total_downloads = sum(downloads)
avg_downloads = total_downloads / total if total > 0 else 0
max_download = max(downloads) if downloads else 0
max_name = data[downloads.index(max_download)][0] if downloads else ''
# 时间处理
times = {'1个月内': 0, '1-3个月': 0, '3-6个月': 0, '6-12个月': 0, '1年以上': 0}
for row in data:
    t = row[3]
    numbers = re.findall(r'\d+', t)
    if not numbers:
        continue
    num = int(numbers[0])
    if '天前' in t:
        if num <= 30:
            times['1个月内'] += 1
        else:
            times['1-3个月'] += 1
    elif '个月前' in t:
        if num <= 3:
            times['1-3个月'] += 1
        elif num <= 6:
            times['3-6个月'] += 1
        elif num <= 12:
            times['6-12个月'] += 1
        else:
            times['1年以上'] += 1
    elif '年前' in t:
        times['1年以上'] += 1
    # 返回值
    stats={'total': total,'total_downloads': total_downloads,'avg_downloads': avg_downloads,'max_download': max_download,'max_name': max_name,'times': times,'data': data}
# 生成HTML
    # 条形图
    bar_html = ''
    total = stats['total']
    for key, value in stats['times'].items():
        if total > 0:
            percent = value / total * 100
        else:
            percent = 0
        bar_html += f'<div class="bar"><span class="label">{key}</span><div class="track"><div class="fill" style="width:{percent}%;">{value} ({percent:.1f}%)</div></div></div>'
# 表格
table_html = ''
for i, row in enumerate(stats['data'], 1):
    name = row[0]
    creater = row[1]
    download = row[2]
    upgrade_time = row[3]
    ico_url = row[4]
    # 图片
    if ico_url:
        img_path = '.'+ico_url
        img_tag = f'<img src="{img_path}" style="width:32px;height:32px;object-fit:contain;border-radius:4px;" alt="{name}">'
    else:
        img_tag = '<span style="color:#999;">无图标</span>'

    table_html += f'<tr><td>{i}</td><td>{img_tag} {name}</td><td>{creater}</td><td>{download}</td><td>{upgrade_time}</td></tr>'
html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{s_name}分析报告</title>
    <style>
        body {{ font-family: "Microsoft YaHei", sans-serif; padding: 30px; background: #f5f5f5; }}
        .box {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ text-align: center; color: #333; }}
        .info {{ display: flex; gap: 20px; justify-content: center; margin: 20px 0; flex-wrap: wrap; }}
        .info-item {{ background: #f0f4ff; padding: 15px 30px; border-radius: 6px; text-align: center; }}
        .info-item .num {{ font-size: 28px; font-weight: bold; color: #4a90d9; }}
        .info-item .label {{ color: #666; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th {{ background: #4a90d9; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #eee; vertical-align: middle; }}
        tr:hover {{ background: #f8f9fa; }}
        .bar {{ display: flex; align-items: center; margin: 5px 0; }}
        .bar .label {{ width: 100px; font-size: 14px; }}
        .bar .track {{ flex: 1; height: 22px; background: #e9ecef; border-radius: 4px; overflow: hidden; }}
        .bar .fill {{ height: 100%; background: #4a90d9; border-radius: 4px; display: flex; align-items: center; justify-content: flex-end; padding-right: 8px; color: white; font-size: 12px; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 20px; }}
        td img {{ vertical-align: middle; margin-right: 8px; }}
    </style>
</head>
<body>
<div class="box">
    <h1>{s_name}数据分析报告</h1>
    <p style="text-align:center;color:#999;">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <div class="info">
        <div class="info-item"><div class="num">{stats['total']}</div><div class="label">{s_name}总数</div></div>
        <div class="info-item"><div class="num">{stats['total_downloads']:,.0f}</div><div class="label">总下载量</div></div>
        <div class="info-item"><div class="num">{stats['avg_downloads']:,.0f}</div><div class="label">平均下载量</div></div>
        <div class="info-item"><div class="num">{stats['max_download']:,.0f}</div><div class="label">最高下载量<br><span style="font-size:12px;color:#999;">{stats['max_name']}</span></div></div>
    </div>
    <h2>更新时间分布</h2>
    {bar_html}
    <h2>{s_name}列表</h2>
    <table>
        <tr><th>序号</th><th>{s_name}名</th><th>创建者</th><th>下载量</th><th>更新时间</th></tr>
        {table_html}
    </table>
    <div class="footer">数据来源: softwarel 数据库 | 共 {stats['total']} 条记录</div>
</div>
</body>
</html>'''
file_path = os.path.join('analysis', 'analysis_report.html')
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f"HTML报告已生成: {file_path}")
