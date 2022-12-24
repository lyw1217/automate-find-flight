from app.config import *
from app.flight import *
from discord.ext import tasks

import discord

initial_str = '''
█▀▀ █ █▄░█ █▀▄  █▀▀ █░░ █ █▀▀ █░█ ▀█▀
█▀░ █ █░▀█ █▄▀  █▀░ █▄▄ █ █▄█ █▀█ ░█░
by Youngwoo\n
'''

help_str = '''
🥇 네이버 왕복 항공권 자동 검색 (30분마다)\n
🥈 사용 방법 : !항공권 [도시] [출발일] [시간대...] [도착일] [시간대...]\n
🥉 사용 예시 : !항공권 오사카 23-01-26 06-09,09-12 23-01-29 15-18,18-21
        - [인천 <-> 오사카]
        - [23년 01월 26일, 06시-09시, 09시-12시 인천 출발]
        - [23년 01월 29일, 15시-18시, 18시-21시 오사카 출발]\n
🏅 적용 가능한 [시간대]
        [ 00-06 | 06-09 | 09-12 | 12-15 | 15-18 | 18-21 | 21-00 ]
'''

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
    
    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = f'Welcome {member.mention} to {guild.name}!'
            await guild.system_channel.send(to_send)

    async def setup_hook(self) -> None:
        # start the task to run in the background
        self.find_flight_task.start()
        print("FIND FLIGHT TASK START")

    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = f'Welcome {member.mention} to {guild.name}!\n{initial_str}{help_str}'
            await guild.system_channel.send(to_send)

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!항공권'):
            if message.content == '!항공권' :
                await message.reply(initial_str + help_str, mention_author=True)
            else :
                commands = message.content.split(" ")
                print(commands)
                if len(commands) == 6 :
                    create_time = time.strftime('%Y.%m.%d - %H:%M:%S')
                    # 도시
                    city = commands[1]
                    # 출발일
                    departure_day = commands[2]
                    # 출발 시간대
                    departure_time = commands[3]
                    # 도착일
                    arrival_day = commands[4]
                    # 도착 시간대
                    arrival_time = commands[5]
                    reply_str = f'''
⏲️ 생성 시간 : {create_time}
🧳 도시 : {city}
📅 출발일 : {departure_day}
🕒 출발 시간대 : {departure_time}
🗓️ 도착일 : {arrival_day}
🕧 도착 시간대 : {arrival_time}

    대충 {INTERVAL}분에 한 번씩 검색해서 알려드릴게요.
'''
                    await message.reply(reply_str, mention_author=True)

                    flight = Flight(create_time, city, departure_day, departure_time, arrival_day, arrival_time)
                    res = await flight.get_flight()
                    await message.reply(res, mention_author=True)

                    global flight_list
                    flight_list.append(flight)
                else :
                    await message.reply(f'명령어를 잘못 입력했습니다.\n{help_str}', mention_author=True)
                
    @tasks.loop(seconds=INTERVAL*60)  # task runs every 1800 seconds
    async def find_flight_task(self):
        global flight_list
        for f in flight_list :
            res = await f.get_flight()
            channel = self.get_channel(DISCORD_CHANNEL)  # channel ID goes here
            await channel.send(res)

    @find_flight_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in