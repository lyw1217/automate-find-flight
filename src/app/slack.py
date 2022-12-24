# source: https://wooiljeong.github.io/python/slack-bot/
from slack_sdk import WebClient
from app.config import *
class SlackAPI:
    """
    슬랙 API 핸들러
    """
    def __init__(self, token:str):
        # 슬랙 클라이언트 인스턴스 생성
        self.client = WebClient(token)
        self.channel_id = ""
        
    def get_channel_id(self, channel_name:str):
        """
        슬랙 채널ID 조회
        """
        # conversations_list() 메서드 호출
        result = self.client.conversations_list()
        # 채널 정보 딕셔너리 리스트
        channels = result.data['channels']
        # 채널 명이 'test'인 채널 딕셔너리 쿼리
        channel = list(filter(lambda c: c["name"] == channel_name, channels))[0]
        # 채널ID 파싱
        channel_id = channel["id"]
        return channel_id

    def get_message_ts(self, channel_id:str, query:str):
        """
        슬랙 채널 내 메세지 조회
        """
        # conversations_history() 메서드 호출
        result = self.client.conversations_history(channel=channel_id)
        # 채널 내 메세지 정보 딕셔너리 리스트
        messages = result.data['messages']
        # 채널 내 메세지가 query와 일치하는 메세지 딕셔너리 쿼리
        message = list(filter(lambda m: m["text"]==query, messages))[0]
        # 해당 메세지ts 파싱
        message_ts = message["ts"]
        return message_ts

    def get_last_message(self, channel_id:str):
        """
        슬랙 채널 내 마지막 메세지 조회
        """
        # conversations_history() 메서드 호출
        result = self.client.conversations_history(channel=channel_id, inclusive=True, limit=1)
        # 채널 내 메세지 정보 딕셔너리 리스트
        message = result.data['messages'][0]

        return message

    def get_thread_latest_message(self, channel_id:str, message_ts:str):
        """
        슬랙 채널 내 메세지의 Thread에서 메시지 조회
        """
        # chat_postMessage() 메서드 호출
        result = self.client.conversations_replies(
            channel=channel_id,
            ts = message_ts,
            inclusive=True,
            limit=1
        )

        message = result["messages"][0]
        
        return message["text"]

    def post_thread_message(self, channel_id:str, message_ts:str, text:str):
        """
        슬랙 채널 내 메세지의 Thread에 댓글 달기
        """
        # chat_postMessage() 메서드 호출
        result = self.client.chat_postMessage(
            channel=channel_id,
            text = text,
            thread_ts = message_ts
        )
        return result
    
    def post_message(self, channel_id:str, text: str):
        """
        슬랙 채널 내 메시지 보내기
        """
        result = self.client.chat_postMessage(
            channel=channel_id,
            text = text
        )
        return result

def init_slack_channel(channel_name: str):
    try:
        s = SlackAPI(SLACK_KEY)
        s.channel_id = s.get_channel_id(channel_name)
        root_logger.critical(f"Initialize Slack > channel_id = {s.channel_id}")
    except Exception as e:
        root_logger.critical(f"Failed init slack > channel_name = {channel_name}, err = {e}")

    return s

def post_slack_message(s: SlackAPI, text: str):
    if len(s.channel_id) > 0 :
        try :
            res = s.post_message(s.channel_id, text)
            root_logger.critical("Send Slack Message : " + text)
            return res
        except Exception as e:
            root_logger.critical(f"Failed Send Slack Message > id : {s.channel_id}, text : {text}, err = {e}")
            res = ""
            return res
    return ""

slack = init_slack_channel(SLACK_CHANNEL)