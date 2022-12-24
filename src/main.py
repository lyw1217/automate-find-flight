from app import *

if __name__ == "__main__":
    #
    #
    #
    #
    #
    #
    root_logger.critical(r"======================================")
    root_logger.critical(r"     _______           __  by Youngwoo")
    root_logger.critical(r"    / ____(_)___  ____/ /             ")
    root_logger.critical(r"   / /_  / / __ \/ __  /              ")
    root_logger.critical(r"  / __/ / / / / / /_/ /               ")
    root_logger.critical(r" /_/   /_/_/ /_/\__,_/                ")
    root_logger.critical(r"    ________    ____________  ________")
    root_logger.critical(r"   / ____/ /   /  _/ ____/ / / /_  __/")
    root_logger.critical(r"  / /_  / /    / // / __/ /_/ / / /   ")
    root_logger.critical(r" / __/ / /____/ // /_/ / __  / / /    ")
    root_logger.critical(r"/_/   /_____/___/\____/_/ /_/ /_/     ")
    root_logger.critical(r"                            S T A R T ")
    root_logger.critical(r"======================================")
    root_logger.critical(f"  ROOT DIR     = {ROOT_DIR}")
    root_logger.critical(f"  BASE DIR     = {BASE_DIR}")
    root_logger.critical(f"  CONFIG  PATH = {CONFIG_PATH}")
    root_logger.critical(f"  LOG CFG PATH = {LOG_CFG_PATH}")
    root_logger.critical(f"  LOGGING PATH = {LOGGING_PATH}")
    root_logger.critical(f"  DRIVER  PATH = {DRIVER_PATH}")
    root_logger.critical(f"")
    root_logger.critical(f"  INTERVAL     = {INTERVAL} min")
    root_logger.critical(r"======================================")

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    client = MyClient(intents=intents)
    client.run(DISCORD_TOKEN)
