from discord.ext import tasks
import hashlib
import discord

from app.config import *
from app.flight import *

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
            to_send = f'Welcome {member.mention} to {guild.name}!\n{INITIAL_STR}{HELP_STR}'
            await guild.system_channel.send(to_send)
    
    global flight_list
    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if message.content.startswith('!삭제'):
            try :
                input_id = message.content.split(" ")[1]
                for f in flight_list :
                    if f.id == input_id :
                        reply_str = f"ID : {f.id}, {f.city}행 {f.departure_day} 출발하는 항공권 검색을 그만할게요."
                        del flight_list[flight_list.index(f)]
                        await message.reply(reply_str, mention_author=True)
                        return
                raise Exception("Not found id")
            except Exception as e :
                print("항공권 삭제 실패")
                print(e)
                await message.reply("해당 ID가 존재하지 않아요.", mention_author=True)
        
        elif message.content.startswith('!목록'):
            try :
                reply_str = ""
                for f in flight_list :
                    reply_str += f"ID:{f.id} > {f.city}행 {f.departure_day} 출국, {f.arrival_day} 귀국\n"

                await message.reply(reply_str, mention_author=True)
            except Exception as e :
                reply_str = "목록 조회 에러 발생"
                print(reply_str)
                print(e)
                await message.reply(reply_str, mention_author=True)

        elif message.content.startswith('!항공권'):
            if message.content == '!항공권' :
                await message.reply(INITIAL_STR + HELP_STR, mention_author=True)
            else :
                commands = message.content.split(" ")
                print(commands)
                if len(commands) == 6 :
                    # 생성 시간
                    create_time = time.strftime('%Y.%m.%d - %H:%M:%S')
                    # ID
                    id = hashlib.sha1(create_time.encode("UTF-8")).hexdigest()[:10]
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
< 항공권 검색 > (ID : {id}, TIME : {create_time})
🧳 도시 : {city}
📅 출발일 : {departure_day}  🕒 출발 시간대 : {departure_time}
🗓️ 도착일 : {arrival_day}  🕧 도착 시간대 : {arrival_time}

    대충 {INTERVAL}분에 한 번씩 검색해서 알려드릴게요.
'''
                    await message.reply(reply_str, mention_author=True)

                    flight = Flight(id, create_time, city, departure_day, departure_time, arrival_day, arrival_time)
                    res = await flight.find_flight()
                    await message.reply(res, mention_author=True)
                    
                    flight_list.append(flight)
                else :
                    await message.reply(f'명령어를 잘못 입력했습니다.\n{HELP_STR}', mention_author=True)
                
    @tasks.loop(seconds=INTERVAL*60)  # task runs every 1800 seconds
    async def find_flight_task(self):
        global flight_list
        for f in flight_list :
            res = await f.find_flight()
            channel = self.get_channel(DISCORD_CHANNEL)  # channel ID goes here
            await channel.send(res)

    @find_flight_task.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in