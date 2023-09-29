from environs import Env

env = Env()
env.read_env()

TOURNEY_COP_BOT_API_TOKEN = env.str("TOURNEY_COP_BOT_API_TOKEN")
