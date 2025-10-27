# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# Modify : 2025/8/10
# 使用账号密码登录慈云，进行签到获取积分
#
"""
new Env('慈云服务器签到');
12 9 * * * ciyun_bot.py
"""

import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
import logging
import wx_send
from notify import send

# 获取当前日期并格式化
today_str = datetime.now().strftime("%Y-%m-%d")


class ZovpsClient:
    def __init__(self, username: str = "", password: str = ""):
        self.username = username
        self.password = password
        self.token = ""
        self.session = requests.Session()
        self.logged_in = False
        self.send_msg = ""

    def get_token(self):
        session = requests.Session()
        login_page_url = "https://www.zovps.com/login?action=phone"
        try:
            resp = session.get(login_page_url, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            token_input = soup.find("input", {"name": "token"})
            if token_input and token_input.has_attr("value"):
                self.token = token_input["value"]
            else:
                logging.error("未找到token字段")
                return False
        except Exception as e:
            logging.error(f"获取token失败: {e}")
            return False
        return True

    def login(self, phone_code: str = "+86") -> bool:
        login_url = "https://www.zovps.com/login?action=phone"  # 替换成真实登录接口URL

        payload = {
            "token": self.token,
            "phone_code": phone_code,
            "phone": self.username,
            "password": self.password,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0",
            "referer": "https://www.zovps.com/login",
        }

        resp = self.session.post(login_url, data=payload)
        if resp.status_code == 200 or "登录成功" in resp.text:
            self.logged_in = True
            print(f"登录成功\n{self.session.cookies.get_dict()}")
            return True
        else:
            print(f"登录失败:{self.username} : {self.password}")
            self.send_msg += f"登录失败，状态码：{resp.status_code}，响应：{resp.text}"
            return False

    def sign_in(self) -> bool:
        if not self.logged_in:
            print("请先登录")
            return False

        sign_url = "https://www.zovps.com/addons?_plugin=points_mall&_controller=index&_action=sign"

        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "content-type": "application/json",
            "origin": "https://www.zovps.com",
            "referer": "https://www.zovps.com/addons?_plugin=points_mall&_controller=index&_action=signin",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
            "x-requested-with": "XMLHttpRequest",
        }

        payload = {"date": today_str}

        resp = self.session.post(sign_url, headers=headers, json=payload)

        print("签到状态码:", resp.status_code)
        print("签到响应内容:", resp.text)

        if resp.status_code == 200:
            # print("签到成功:", resp.text)
            self.send_msg += f"签到成功：{resp.text}"
            return True
        else:
            # print(f"签到失败，状态码：{resp.status_code}，响应：{resp.text}")
            self.send_msg += f"签到失败，状态码：{resp.status_code}，响应：{resp.text}"
            return False

    def sign_default(self) -> bool:
        # 目标 URL
        url = "https://www.zovps.com/addons?_plugin=points_mall&_controller=index&_action=sign"

        # 请求头（去掉 HTTP/2 的伪头部，requests 会自动处理 Content-Length）
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "content-type": "application/json",
            "origin": "https://www.zovps.com",
            "priority": "u=1, i",
            "referer": "https://www.zovps.com/addons?_plugin=points_mall&_controller=index&_action=signin",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Microsoft Edge";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0",
            "x-requested-with": "XMLHttpRequest",
            "Cookie": "Hm_lvt_316c915d291db3aea53c4e2c807af44e=1731496472,1731725772; PHPSESSID=pq4nenf0lgnb3mrg3191b96o0q; YOFDCRU=099a998e2909663168d240e38e2508ee; ZJMF_226527B9B10DA797=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyaW5mbyI6eyJpZCI6MzkwNiwidXNlcm5hbWUiOiJcdTllYzRcdTZmYjNcdTcwYWYifSwiaXNzIjoid3d3LmlkY1NtYXJ0LmNvbSIsImF1ZCI6Ind3dy5pZGNTbWFydC5jb20iLCJpcCI6IjM5LjE0OC4zMC4yNDgiLCJpYXQiOjE3NTQ3ODk2NzEsIm5iZiI6MTc1NDc4OTY3MSwiZXhwIjoxNzU0Nzk2ODcxfQ.n9NAu0hSQLvZZx1BvzktYTRPjWH1Ye4nQixCJGskzlQ; PointsMall=allowed",
        }

        # POST 请求的数据（JSON 格式）
        payload = {
            # 根据抓包填写实际参数
            "date": today_str
        }

        try:
            # 发送 POST 请求
            response = requests.post(url, headers=headers, json=payload, timeout=10)

            # 输出状态码和响应内容
            print("Status Code:", response.status_code)
            print("Response Text:", response.text)
            self.send_msg += response.text
            return True

        except requests.RequestException as e:
            print("请求出错:", e)
            return False

    def get_points(self):
        url = "https://www.zovps.com/addons?_plugin=points_mall&_controller=index&_action=task"

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
            # 其他必要头部可以加上，比如cookie会自动带
        }

        response = self.session.get(url, headers=headers)
        response.raise_for_status()  # 如果响应状态不是200，会抛异常

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # 找到 class 是 points-value 的 div
        points_div = soup.find("div", class_="points-value")
        if points_div:
            points_text = points_div.get_text(strip=True)
            print("当前积分:", points_text)
            self.send_msg += f"当前积分：{points_text} \n"
            return points_text
        else:
            print("没找到积分信息")
            return None
    def get_signin_days(self):
        url = "https://www.zovps.com/addons?_plugin=points_mall&_controller=index&_action=signin"

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9",
            "cache-control": "max-age=0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
        }

        response = self.session.get(url, headers=headers)
        response.raise_for_status()

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # 找累计签到天数
        total_days_span = soup.find("span", id="totalsignDays")
        total_days = total_days_span.get_text(strip=True) if total_days_span else None

        # 找连续签到天数
        consecutive_days_span = soup.find("span", id="consecutiveDays")
        consecutive_days = consecutive_days_span.get_text(strip=True) if consecutive_days_span else None

        if total_days or consecutive_days:
            msg = f"累计签到：{total_days} 天，连续签到：{consecutive_days} 天"
            print(msg)
            self.send_msg += msg + "\n"
            return total_days, consecutive_days
        else:
            print("没找到签到信息")
            return None, None


class QQClient:
    def __init__(self):
        self.url_root = "http://127.0.0.1:25733"

    def send_group_msg(self, title, msg, qq_id: str = "455219596"):
        """
        发送一个带两个参数的 GET 请求
        :param url: 目标 URL
        :param param1: 第一个参数值
        :param param2: 第二个参数值
        :return: 响应对象
        """
        url = self.url_root + "/send_group_msg"
        params = {"group_id": "455219596", "message": title + "\n\n" + msg}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # 如果状态码不是 200-399，会抛异常
            return response.text
        except requests.RequestException as e:
            print(f"请求出错: {e}")
            return None


def main1():

    client = ZovpsClient()
    client.get_token()

    username = ""
    password = ""
    try:
        if "ciyun_info" in os.environ:
            ciyun_info = os.environ["ciyun_info"]
            parts = ciyun_info.split("@")
            if len(parts) != 3:
                print("字符串必须包含且仅包含两个@，分成三个部分")
                return
            username, password, token = ciyun_info.split("@")  # 最多拆成两部分
            print(f"检测到一个用户【{username}】,现在开始签到......\n")
            client.send_msg += f"检测到一个用户【{username}】,现在开始签到......\n"
        else:
            username = "15565362938"
            password = "Y102111079"
            print("使用默认账户签到")
            client.send_msg += "使用默认账户签到\n"
    except Exception as e:
        print(f"【getCookie Error】{e}")
        return

    # 使用签到客户端

    client.username = username
    client.password = password
    # if client.sign_default():
    #     print(client.send_msg)
    # elif client.login(token=token):
    #     client.sign_in()
    if client.login():
        time.sleep(random.randint(10, 30))
        client.sign_in()
        client.get_points()
    qq_client = QQClient()
    # print(qq_client.send_group_msg("慈云签到通知", client.send_msg))
    print(client.send_msg)
    wx_send.WxPusher_send_message(title="慈云签到通知", content=client.send_msg)

def main():
    # 初始化QQ客户端和消息内容（所有账号共用）
    qq_client = QQClient()
    total_send_msg = "慈云签到结果汇总：\n\n"

    try:
        if "ciyun_info" in os.environ:
            ciyun_info = os.environ["ciyun_info"]
            accounts = ciyun_info.split("&")  # 用&分割多个账号
            
            for account in accounts:
                # 为每个账号创建新的客户端实例
                client = ZovpsClient()
                client.get_token()
                
                parts = account.split("@")
                if len(parts) != 3:
                    error_msg = f"账号信息格式错误，必须包含且仅包含两个@，分成三个部分: {account}\n"
                    print(error_msg)
                    total_send_msg += error_msg
                    continue
                
                username, password, token = parts
                print(f"检测到用户【{username}】，现在开始签到......\n")
                client.send_msg = f"检测到用户【{username}】，现在开始签到......\n"
                
                # 使用签到客户端
                client.username = username
                client.password = password
                if client.login():
                    time.sleep(random.randint(10, 30))
                    client.sign_in()
                    client.get_points()
                    client.get_signin_days()
                else:
                    client.send_msg += f"用户【{username}】登录失败\n"
                
                # 收集每个账号的结果
                total_send_msg += client.send_msg + "\n------------------------\n"
                
        else:
            # 如果没有环境变量，使用默认账户
            client = ZovpsClient()
            client.get_token()
            
            username = "15565362938"
            password = "Y102111079"
            print("使用默认账户签到")
            client.send_msg = "使用默认账户签到\n"
            
            client.username = username
            client.password = password
            if client.login():
                time.sleep(random.randint(10, 30))
                client.sign_in()
                client.get_points()
                client.get_signin_days()
            
            total_send_msg += client.send_msg
                
    except Exception as e:
        error_msg = f"【getCookie Error】{e}\n"
        print(error_msg)
        total_send_msg += error_msg

    # 发送通知
    # print(qq_client.send_group_msg("慈云签到通知", total_send_msg))
    print(total_send_msg)
    wx_send.WxPusher_send_message(title="慈云签到通知", content=total_send_msg)
    send("慈云 签到", total_send_msg)
    
# 使用示例
if __name__ == "__main__":
    main()
