'''
cron:  30 */2 * * * linkAI.py
new Env('Link AI签到');
'''
import requests
import os
# from wx_notify import send
from notify import send

Authorization = os.getenv("linkBearer")


url = 'https://link-ai.tech/api/chat/web/app/user/sign/in'  # 请求的URL

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Authorization': Authorization,
    'Connection': 'keep-alive',
    'Cookie': '_gcl_au=1.1.1119734332.1703317262',
    'Host': 'link-ai.tech',
    'Referer': 'https://link-ai.tech/console/account',
    'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
}

response = requests.get(url, headers=headers)

print(response.status_code)  # 打印状态码
datas=response.json()
if response.status_code == 200:
    if datas['success'] == 'True' or  datas['success'] == True:
        send("LinkAI 签到",f"打卡成功：获得积分{datas['data']['score']}")
    else:
        send("LinkAI 签到",f"打卡成功：{datas['message']}")
else:
    send("LinkAI 签到",f"签到失败：{datas['message']}")
print(response.json())  # 打印响应的JSON内容