import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import urllib3

# 禁用 InsecureRequestWarning 警告（防止政务网站证书问题导致报错）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 配置区域 =================
# 目标网址
URL = 'https://www.miit-eidc.org.cn/col/col1576/index.html'

# 第一条公告的 CSS 选择器
SELECTOR = 'body > div.wrapper > div.r_content > div > div.r_content_right > div:nth-child(2) > ul > li:nth-child(1) > a'
# ============================================

def send_email(subject, body):
    sender = os.environ['SENDER_EMAIL']
    password = os.environ['SENDER_PASSWORD'] # 这是QQ邮箱的授权码
    receiver = os.environ['RECEIVER_EMAIL']

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    # 使用 QQ 邮箱的 SMTP 服务器，SSL 模式，端口 465
    try:
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("邮件发送成功！")
    except Exception as e:
        print(f"邮件发送失败: {e}")

def main():
    # 模拟真实浏览器，防止被拦截
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    
    try:
        # verify=False 防止部分国内网站 SSL 证书未被广泛信任导致报错
        response = requests.get(URL, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        # 自动识别并转换编码，防止中文乱码 (GBK/UTF-8)
        response.encoding = response.apparent_encoding 
    except Exception as e:
        print(f"获取网页失败: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 尝试提取第一条公告
    element = soup.select_one(SELECTOR)
    
    if not element:
        print(f"未找到对应的网页元素，请检查 SELECTOR 是否正确。你设置的 SELECTOR 是: {SELECTOR}")
        return

    current_data = element.text.strip()

    # 读取旧数据
    old_data = ""
    if os.path.exists('last_data.txt'):
        with open('last_data.txt', 'r', encoding='utf-8') as f:
            old_data = f.read().strip()

    # 对比数据
    if current_data != old_data:
        print(f"发现更新！\n新内容: {current_data}\n旧内容: {old_data}")
        
        subject = "🔔 工信部车辆准入许可公告更新提醒"
        body = f"网站发布了新公告！\n\n最新公告标题:\n{current_data}\n\n快速查看链接: {URL}"
        send_email(subject, body)

        # 保存新数据
        with open('last_data.txt', 'w', encoding='utf-8') as f:
            f.write(current_data)
    else:
        print(f"网页内容没有变化，最新公告依然是: {current_data}")

if __name__ == '__main__':
    main()
