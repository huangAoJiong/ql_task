#多号换行，变量名：sfsyUrl
# const $ = new Env('顺丰速运')
import hashlib
import json
import os
import random
import time
from datetime import datetime, timedelta
from sys import exit
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from urllib.parse import unquote

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 全局消息变量
send_msg = ''
one_msg = ''

def Log(cont=''):
    """日志输出函数"""
    global send_msg, one_msg
    print(cont)
    if cont:
        one_msg += f'{cont}\n'
        send_msg += f'{cont}\n'

def sunquote(sfurl):
    """双重URL解码函数，兼容多种编码格式"""
    decode = unquote(sfurl)
    if "%3A%2F%2F" in decode.upper():
        decode = unquote(decode)
    return decode

# 邀请ID列表 (所有活动ID合并)
inviteId = list(set(['15B892B84AA3418B8BE6856D5A4F1119','54BC6335A52A4197ACA8E32BB57CCFE5', '076CFC24BDE249BB8E7994DDE85E605F']))


class RUN:
    def __init__(self, info, index):
        global one_msg
        one_msg = ''
        split_info = info.split('@')
        url = sunquote(split_info[0])
        len_split_info = len(split_info)
        last_info = split_info[len_split_info - 1]
        self.send_UID = None
        if len_split_info > 0 and "UID_" in last_info:
            self.send_UID = last_info
        self.index = index + 1
        Log(f"\n---------开始执行第{self.index}个账号>>>>>")
        self.s = requests.session()
        self.s.verify = False
        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090551) XWEB/6945 Flue',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh',
            'platform': 'MINI_PROGRAM',
        }
        self.login_res = self.login(url)
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.max_level = 8
        self.packet_threshold = 1 << (self.max_level - 1)
        
        # 为中秋活动初始化属性
        self.midautumn_activity_code = 'MIDAUTUMN_2025'
        self.midautumn_recommend_tasks = []

    def get_deviceId(self, characters='abcdef0123456789'):
        result = ''
        for char in 'xxxxxxxx-xxxx-xxxx':
            if char == 'x': result += random.choice(characters)
            else: result += char
        return result

    def login(self, sfsyUrl):
        ress = self.s.get(sfsyUrl, headers=self.headers)
        self.user_id = self.s.cookies.get_dict().get('_login_user_id_', '')
        self.phone = self.s.cookies.get_dict().get('_login_mobile_', '')
        self.mobile = self.phone[:3] + "*" * 4 + self.phone[7:] if self.phone else ''
        if self.phone:
            Log(f'用户:【{self.mobile}】登陆成功')
            return True
        else:
            Log(f'获取用户信息失败')
            return False

    def getSign(self):
        timestamp = str(int(round(time.time() * 1000)))
        token = 'wwesldfs29aniversaryvdld29'
        sysCode = 'MCS-MIMP-CORE'
        data = f'token={token}&timestamp={timestamp}&sysCode={sysCode}'
        signature = hashlib.md5(data.encode()).hexdigest()
        sign_data = {'sysCode': sysCode, 'timestamp': timestamp, 'signature': signature}
        self.headers.update(sign_data)
        return sign_data

    def do_request(self, url, data={}, req_type='post'):
        self.getSign()
        original_content_type = self.headers.get('content-type')
        try:
            if req_type.lower() == 'get':
                if 'content-type' in self.headers: del self.headers['content-type']
                response = self.s.get(url, headers=self.headers)
            else:
                self.headers['content-type'] = 'application/json'
                response = self.s.post(url, headers=self.headers, json=data)
            
            if original_content_type: self.headers['content-type'] = original_content_type
            elif 'content-type' in self.headers: del self.headers['content-type']

            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            Log(f'请求错误: {str(e)}')
            if original_content_type: self.headers['content-type'] = original_content_type
            return None

    # =================================================================
    # VVVVVV 日常签到和积分任务 VVVVVV
    # =================================================================
    def sign(self):
        Log('====== 开始执行日常签到 ======')
        json_data = {"comeFrom": "vioin", "channelFrom": "WEIXIN"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskSignPlusService~automaticSignFetchPackage'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            count_day = response.get('obj', {}).get('countDay', 0)
            if response.get('obj') and response['obj'].get('integralTaskSignPackageVOList'):
                packet_name = response["obj"]["integralTaskSignPackageVOList"][0]["packetName"]
                Log(f'>>>签到成功，获得【{packet_name}】，本周累计签到【{count_day + 1}】天')
            else:
                Log(f'今日已签到，本周累计签到【{count_day + 1}】天')
        elif response:
            Log(f'签到失败！原因：{response.get("errorMessage")}')
        else:
            Log(f'签到请求失败！')

    def doTask(self):
        Log(f'>>>开始去完成【{self.title}】任务')
        json_data = {'taskCode': self.taskCode}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonRoutePost/memberEs/taskRecord/finishTask'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            Log(f'>【{self.title}】任务-已完成')
        elif response:
            Log(f'>【{self.title}】任务-{response.get("errorMessage")}')
        else:
            Log(f'>【{self.title}】任务请求失败！')

    def receiveTask(self):
        Log(f'>>>开始领取【{self.title}】任务奖励')
        json_data = {
            "strategyId": self.strategyId, "taskId": self.taskId,
            "taskCode": self.taskCode, "deviceId": self.get_deviceId()
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~fetchIntegral'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            Log(f'>【{self.title}】任务奖励领取成功！')
        elif response:
            Log(f'>【{self.title}】任务-{response.get("errorMessage")}')
        else:
            Log(f'>【{self.title}】任务奖励领取请求失败！')

    def get_SignTaskList(self, END=False):
        if not END: Log('====== 开始获取积分任务列表 ======')
        json_data = {'channelType': '1', 'deviceId': self.get_deviceId()}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES'
        response = self.do_request(url, data=json_data)
        if response and response.get('success') and response.get('obj'):
            totalPoint = response["obj"]["totalPoint"]
            if END:
                Log(f'当前积分：【{totalPoint}】')
                return
            Log(f'执行前积分：【{totalPoint}】')
            for task in response["obj"]["taskTitleLevels"]:
                self.taskId = task["taskId"]
                self.taskCode = task["taskCode"]
                self.strategyId = task["strategyId"]
                self.title = task["title"]
                status = task["status"]
                skip_title = ['用行业模板寄件下单', '去新增一个收件偏好', '参与积分活动']
                if status == 3:
                    Log(f'>{self.title}-已完成')
                    continue
                if self.title in skip_title:
                    Log(f'>{self.title}-跳过')
                    continue
                else:
                    self.doTask()
                    time.sleep(2)
                self.receiveTask()
    
    # =================================================================
    # VVVVVV 丰蜜活动 VVVVVV
    # =================================================================
    def do_honeyTask(self):
        # 做任务
        json_data = {"taskCode": self.taskCode}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            Log(f'>【{self.taskType}】任务-已完成')
        elif response:
            Log(f'>【{self.taskType}】任务-{response.get("errorMessage")}')

    def receive_honeyTask(self):
        Log('>>>执行收取丰蜜任务')
        # 收取
        self.headers['syscode'] = 'MCS-MIMP-CORE'
        self.headers['channel'] = 'wxwdsj'
        self.headers['accept'] = 'application/json, text/plain, */*'
        self.headers['content-type'] = 'application/json;charset=UTF-8'
        self.headers['platform'] = 'MINI_PROGRAM'
        json_data = {"taskType": self.taskType}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~receiveHoney'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            Log(f'收取任务【{self.taskType}】成功！')
        elif response:
            Log(f'收取任务【{self.taskType}】失败！原因：{response.get("errorMessage")}')

    def get_coupom(self):
        Log('>>>执行领取生活权益领券任务')
        json_data = {
            "from": "Point_Mall", "orderSource": "POINT_MALL_EXCHANGE",
            "goodsNo": self.goodsNo, "quantity": 1, "taskCode": self.taskCode
        }
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~createOrder'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            Log(f'>领券成功！')
        elif response:
            Log(f'>领券失败！原因：{response.get("errorMessage")}')

    def get_coupom_list(self):
        Log('>>>获取生活权益券列表')
        json_data = {"memGrade": 2, "categoryCode": "SHTQ", "showCode": "SHTQWNTJ"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~mallGoodsLifeService~list'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            goodsList = response["obj"][0]["goodsList"]
            for goods in goodsList:
                if goods['exchangeTimesLimit'] >= 1:
                    self.goodsNo = goods['goodsNo']
                    Log(f'当前选择券号：{self.goodsNo}')
                    self.get_coupom()
                    break
        elif response:
            Log(f'>获取券列表失败！原因：{response.get("errorMessage")}')

    def get_honeyTaskListStart(self):
        Log('>>>开始获取采蜜换大礼任务列表')
        json_data = {}
        self.headers['channel'] = 'wxwdsj'
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~taskDetail'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            for item in response["obj"]["list"]:
                self.taskType = item["taskType"]
                if item["status"] == 3:
                    Log(f'>【{self.taskType}】-已完成')
                    continue
                if "taskCode" in item:
                    self.taskCode = item["taskCode"]
                    if self.taskType == 'DAILY_VIP_TASK_TYPE':
                        self.get_coupom_list()
                    else:
                        self.do_honeyTask()
                if self.taskType == 'BEES_GAME_TASK_TYPE':
                    self.honey_damaoxian()
                time.sleep(2)

    def honey_damaoxian(self):
        Log('>>>执行大冒险任务')
        gameNum = 5
        for i in range(1, gameNum + 1):
            if gameNum <= 0: break
            Log(f'>>开始第{i}次大冒险')
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeGameService~gameReport'
            response = self.do_request(url, data={'gatherHoney': 20})
            if response and response.get('success'):
                gameNum = response.get('obj', {}).get('gameNum', 0)
                Log(f'>大冒险成功！剩余次数【{gameNum}】')
                time.sleep(2)
            elif response and response.get("errorMessage") == '容量不足':
                Log(f'> 需要扩容')
                self.honey_expand()
            else:
                Log(f'>大冒险失败！【{response.get("errorMessage") if response else "请求失败"}】')
                break

    def honey_expand(self):
        Log('>>>容器扩容')
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~expand'
        response = self.do_request(url, data={})
        if response and response.get('success'):
            Log(f'>成功扩容【{response.get("obj")}】容量')
        else:
            Log(f'>扩容失败！【{response.get("errorMessage") if response else "请求失败"}】')

    def honey_indexData(self, END=False):
        if not END: Log('\n====== 开始执行采蜜换大礼任务 ======')
        random_invite = random.choice([invite for invite in inviteId if invite != self.user_id])
        self.headers['channel'] = 'wxwdsj'
        json_data = {"inviteUserId": random_invite}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~receiveExchangeIndexService~indexData'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            usableHoney = response.get('obj', {}).get('usableHoney')
            if END:
                Log(f'当前丰蜜：【{usableHoney}】')
                return
            Log(f'执行前丰蜜：【{usableHoney}】')
            taskDetail = response.get('obj', {}).get('taskDetail', [])
            activityEndTime = response.get('obj', {}).get('activityEndTime', '')
            if activityEndTime and datetime.now().date() == datetime.strptime(activityEndTime, "%Y-%m-%d %H:%M:%S").date():
                Log("本期活动今日结束，请及时兑换")
            else:
                Log(f'本期活动结束时间【{activityEndTime}】')
            for task in taskDetail:
                self.taskType = task['type']
                self.receive_honeyTask()
                time.sleep(2)

    # =================================================================
    # VVVVVV 周年庆活动 VVVVVV
    # =================================================================
    def EAR_END_2023_TaskList(self):
        Log('\n====== 开始执行周年庆任务 ======')
        json_data = {"activityCode": "ANNIVERSARY_2025", "channelType": "MINI_PROGRAM"}
        self.headers['channel'] = '32annixcx'
        self.headers['platform'] = 'MINI_PROGRAM'
        self.headers['syscode'] = 'MCS-MIMP-CORE'
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            for item in response.get("obj", []):
                self.title = item["taskName"]
                self.taskType = item["taskType"]
                if item["status"] == 3:
                    Log(f'>【{self.title}】-已完成')
                    continue
                if "taskCode" in item:
                    self.taskCode = item["taskCode"]
                    self.doTask()
                    time.sleep(3)
                    self.EAR_END_2023_receiveTask()
                else:
                    Log(f'暂时不支持【{self.title}】任务')
        self.EAR_END_2023_getAward()

    def EAR_END_2023_getAward(self):
        Log(f'>>>开始周年庆抽卡')
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025ClaimService~claim'
        for _ in range(10):
            stop_drawing = False
            for i in range(3):
                response = self.do_request(url, data={"cardType": i})
                if response and response.get('success'):
                    for card in response['obj'].get('receivedAccountList', []):
                        Log(f'>获得：【{card["currency"]}】卡【{card["amount"]}】张！')
                else:
                    error_msg = response.get("errorMessage", "") if response else "请求失败"
                    if '不足' in error_msg or '失效' in error_msg:
                        stop_drawing = True
                        break
                    Log(f'>抽卡失败：{error_msg}')
                time.sleep(3)
            if stop_drawing:
                break

    def EAR_END_2023_query(self):
        Log(f'>>>开始查询周年庆卡片数量')
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~anniversary2025ClaimService~claimStatus'
        response = self.do_request(url, {})
        if response and response.get('success'):
            obj = response.get('obj')
            if not obj: return
            Log("当前卡片数量：")
            for card in obj.get('currentAccountList', []):
                currency_map = {'DAI_BI': '坐以待币', 'CHENG_GONG': '成功人士', 'GAN_FAN': '干饭圣体', 'DING_ZHU': '都顶得住', 'ZHI_SHUI': '心如止水'}
                currency_name = currency_map.get(card.get('currency'), card.get('currency'))
                Log(f"卡片名称：{currency_name}, 数量：{card.get('balance')}")
            Log(f"总抽卡机会：{obj.get('totalFortuneTimes', 0)}")

    def EAR_END_2023_receiveTask(self):
        Log(f'>>>开始领取【{self.title}】任务奖励')
        json_data = {"taskType": self.taskType, "activityCode": "ANNIVERSARY_2025", "channelType": "MINI_PROGRAM"}
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonNoLoginPost/~memberNonactivity~yearEnd2024TaskService~fetchMixTaskReward'
        response = self.do_request(url, data=json_data)
        if response and response.get('success'):
            Log(f'>【{self.title}】任务奖励领取成功！')
        else:
            Log(f'>【{self.title}】任务-{response.get("errorMessage") if response else "请求失败"}')
    
    # =================================================================
    # VVVVVV 会员日活动 VVVVVV
    # =================================================================
    def member_day_index(self):
        Log('\n====== 开始执行会员日活动 ======')
        invite_user_id = random.choice([invite for invite in inviteId if invite != self.user_id])
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayIndexService~index'
        response = self.do_request(url, data={'inviteUserId': invite_user_id})
        if response and response.get('success'):
            lottery_num = response.get('obj', {}).get('lotteryNum', 0)
            Log(f'会员日可以抽奖{lottery_num}次')
            for _ in range(lottery_num):
                self.member_day_lottery()
            self.member_day_task_list()
        else:
            Log(f'查询会员日失败: {response.get("errorMessage") if response else "请求失败"}')

    def member_day_lottery(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayLotteryService~lottery'
        response = self.do_request(url, {})
        if response and response.get('success'):
            Log(f'会员日抽奖: {response.get("obj", {}).get("productName", "空气")}')
        else:
            Log(f'会员日抽奖失败: {response.get("errorMessage") if response else "请求失败"}')

    def member_day_task_list(self):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'
        payload = {'activityCode': 'MEMBER_DAY', 'channelType': 'MINI_PROGRAM'}
        response = self.do_request(url, payload)
        if response and response.get('success'):
            for task in response.get('obj', []):
                if task['status'] == 2:
                    if task['taskType'] not in ['SEND_SUCCESS', 'INVITEFRIENDS_PARTAKE_ACTIVITY']:
                        for _ in range(task.get('restFinishTime', 1)):
                            self.member_day_finish_task(task)
    
    def member_day_finish_task(self, task):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'
        response = self.do_request(url, {'taskCode': task['taskCode']})
        if response and response.get('success'):
            Log(f'完成会员日任务【{task["taskName"]}】成功')
            self.member_day_fetch_mix_task_reward(task)

    def member_day_fetch_mix_task_reward(self, task):
        url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~fetchMixTaskReward'
        payload = {'taskType': task['taskType'], 'activityCode': 'MEMBER_DAY', 'channelType': 'MINI_PROGRAM'}
        response = self.do_request(url, payload)
        if response and response.get('success'):
            Log(f'领取会员日任务【{task["taskName"]}】奖励成功')

    # =================================================================
    # VVVVVV 2025中秋活动功能 VVVVVV
    # =================================================================
    def midautumn_check_activity_status(self):
        """检查中秋活动状态"""
        Log('\n====== 查询2025中秋活动状态 ======')
        self.headers['channel'] = '25zqappdb2'
        try:
            invite_user_id = random.choice([invite for invite in inviteId if invite != self.user_id])
            payload = {"inviteUserId": invite_user_id}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonNoLoginPost/~memberNonactivity~midAutumn2025IndexService~index'
            response = self.do_request(url, payload)
            if response and response.get('success'):
                obj = response.get('obj', {})
                ac_end_time = obj.get('acEndTime', '')
                if ac_end_time and datetime.now() < datetime.strptime(ac_end_time, "%Y-%m-%d %H:%M:%S"):
                    Log(f'2025中秋活动进行中，结束时间：{ac_end_time}')
                    self.midautumn_activity_code = obj.get('actCode', 'MIDAUTUMN_2025')
                    self.midautumn_recommend_tasks = obj.get('recommendTasks', [])
                    return True
                Log('2025中秋活动已结束或未开始')
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'查询中秋活动失败: {error_msg}')
        except Exception as e:
            Log(f'活动状态查询异常: {str(e)}')
        finally:
            if 'channel' in self.headers: del self.headers['channel']
        return False

    def midautumn_process_tasks(self):
        """处理中秋活动任务"""
        Log('====== 处理2025中秋活动任务 ======')
        self.headers['channel'] = '25zqappdb2'
        try:
            payload = {"activityCode": self.midautumn_activity_code, "channelType": "MINI_PROGRAM"}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~taskList'
            response = self.do_request(url, payload)
            if response and response.get('success'):
                task_list = response.get('obj', []) or self.midautumn_recommend_tasks
                for task in task_list:
                    task_name = task.get('val', task.get('taskName', '未知任务'))
                    status = task.get('status', 0)
                    if status == 3:
                        Log(f'> 中秋任务【{task_name}】已完成')
                        continue
                    Log(f'> 开始完成中秋任务【{task_name}】')
                    task_code = task.get('key', task.get('taskCode'))
                    if task_code:
                        self.midautumn_finish_task(task, task_code)
                        time.sleep(2)
                self.midautumn_receive_countdown_reward()
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'查询中秋任务列表失败: {error_msg}')
        except Exception as e:
            Log(f'任务处理异常: {str(e)}')
        finally:
            if 'channel' in self.headers: del self.headers['channel']

    def midautumn_finish_task(self, task, task_code):
        """完成指定的中秋任务"""
        self.headers['channel'] = '25zqappdb2'
        try:
            payload = {'taskCode': task_code}
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberEs~taskRecord~finishTask'
            response = self.do_request(url, payload)
            task_name = task.get('val', task.get('taskName', '未知任务'))
            if response and response.get('success'):
                Log(f'> 完成中秋任务【{task_name}】成功')
                self.midautumn_receive_task_reward(task)
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'> 完成中秋任务【{task_name}】失败: {error_msg}')
        except Exception as e:
            Log(f'> 任务执行异常: {str(e)}')

    def midautumn_receive_task_reward(self, task):
        """领取中秋任务奖励"""
        self.headers['channel'] = '25zqappdb2'
        try:
            payload = {
                'taskType': task.get('taskType', ''),
                'activityCode': self.midautumn_activity_code,
                'channelType': 'MINI_PROGRAM'
            }
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~activityTaskService~fetchMixTaskReward'
            response = self.do_request(url, payload)
            task_name = task.get('val', task.get('taskName', '未知任务'))
            if response and response.get('success'):
                Log(f'> 领取中秋任务【{task_name}】奖励成功')
            else:
                error_msg = response.get('errorMessage', '无返回') if response else '请求失败'
                Log(f'> 领取中秋任务【{task_name}】奖励失败: {error_msg}')
        except Exception as e:
            Log(f'> 奖励领取异常: {str(e)}')

    def midautumn_receive_countdown_reward(self):
        """领取倒计时奖励"""
        Log('====== 尝试领取中秋倒计时奖励 ======')
        self.headers['channel'] = '25zqappdb2'
        try:
            url = 'https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~midAutumn2025BoxService~receiveCountdownReward'
            response = self.do_request(url, {})
            if response and response.get('success', False):
                Log(f'> 领取倒计时奖励成功')
            else:
                error_msg = response.get('errorMessage', '无返回信息') if response else '请求失败'
                Log(f'> 领取倒计时奖励失败: {error_msg}')
        except Exception as e:
            Log(f'> 倒计时奖励领取异常: {str(e)}')
    
    # =================================================================
    # VVVVVV 主函数入口 VVVVVV
    # =================================================================
    def main(self):
        """主运行函数"""
        time.sleep(random.uniform(1.0, 3.0))
        if not self.login_res:
            return False
        
        # --- 1. 执行日常签到和积分任务 ---
        self.sign()
        self.get_SignTaskList()
        self.get_SignTaskList(True)

        # --- 2. 执行丰蜜任务 ---
        self.honey_indexData()
        self.get_honeyTaskListStart()
        self.honey_indexData(True)

        # --- 3. 执行周年庆活动 ---
        Log('\n====== 检查周年庆活动 ======')
        target_time = datetime(2025, 4, 8, 19, 0)
        if datetime.now() < target_time:
            self.EAR_END_2023_TaskList()
            self.EAR_END_2023_query()
        else:
            Log('周年庆活动已结束')

        # --- 4. 执行会员日活动 ---
        Log('\n====== 检查会员日活动 ======')
        current_date = datetime.now().day
        if 26 <= current_date <= 28:
            self.member_day_index()
        else:
            Log('未到会员日（每月26-28日）')

        # --- 5. 执行2025中秋活动任务 ---
        if self.midautumn_check_activity_status():
            self.midautumn_process_tasks()

        self.sendMsg()
        return True

    def sendMsg(self, help=False):
        """消息推送功能（预留）"""
        pass

if __name__ == '__main__':
    ENV_NAME = 'sfsyUrl'
    token = os.getenv(ENV_NAME)
    
    print(f'''
    顺丰速运全能活动自动化脚本
    变量名：{ENV_NAME}（多账号请用换行或&分隔）
    功能：
    - 每日签到、积分任务
    - 丰蜜活动
    - 周年庆活动
    - 会员日活动
    - 2025中秋活动任务
    ''')
    
    if not token:
        print(f"请设置环境变量 {ENV_NAME}")
        exit(1)
        
    tokens = [t.strip() for t in token.replace('&', '\n').split('\n') if t.strip()]
    if not tokens:
        print(f"环境变量 {ENV_NAME} 内容为空，请检查！")
        exit(1)

    print(f"\n>>>>>>>>>>共获取到{len(tokens)}个账号<<<<<<<<<<")
    
    for index, info in enumerate(tokens):
        try:
            runner = RUN(info, index)
            if not runner.main():
                continue
        except Exception as e:
            Log(f"账号 {index+1} 运行出现未知错误: {e}")