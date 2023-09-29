import asyncio
import logging
import sys
import random

from aiogram import Dispatcher, Bot, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from bot import config

TOKEN = config.TOURNEY_COP_BOT_API_TOKEN

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


class NewTourneyForm(StatesGroup):
    waiting_game_sides = State()
    waiting_players_names = State()
    start_tourney = State()


new_tourney_router = Router()


@new_tourney_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(
        f"Hello, {hbold(message.from_user.full_name)}! Welcome to tournament management bot.\n"
        f"Let's start by typed /new_tourney"
    )


@new_tourney_router.message(Command("new_tourney"))
async def command_new_tourney_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/new_tourney` command
    """
    await state.set_state(NewTourneyForm.waiting_game_sides)
    await message.answer(
        f"Ok, go to new tourney creation.\n"
        f"First of all, please type separated by space names of sides participating in a game "
        f"(for chess these are white and black):"
    )


@new_tourney_router.message(NewTourneyForm.waiting_game_sides)
async def process_game_sides(message: Message, state: FSMContext) -> None:
    game_sides = message.text.split(" ")
    await state.update_data(game_sides=game_sides)
    await state.set_state(NewTourneyForm.waiting_players_names)
    await message.answer("Good job! Now please type players names:")


@new_tourney_router.message(NewTourneyForm.waiting_players_names)
async def process_players_names(message: Message, state: FSMContext) -> None:
    players_names = message.text.split(" ")
    new_tourney_data = await state.update_data(players_names=players_names)
    await state.set_state(NewTourneyForm.start_tourney)
    await message.answer(
        "Congrats! You've just created a new tourney!\n\n"
        f"So, the Sides: {new_tourney_data['game_sides']};\n"
        f"The Players: {new_tourney_data['players_names']}.\n\n"
        "Now you can start the competition round (enter command /new_round))"
    )


@new_tourney_router.message(Command("new_round"))
async def process_new_round(message: Message, state: FSMContext) -> None:
    new_tourney_data = await state.get_data()
    game_sides_stack = new_tourney_data["game_sides"]
    selected_sides = {}
    for name in new_tourney_data["players_names"]:
        side = random.choice(game_sides_stack)
        selected_sides[name] = side
        game_sides_stack.remove(side)
    await message.answer(f"In this round side are distributed as:\n{selected_sides}.\n\n hf-:)")


@dp.message()
async def main() -> None:
    bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(new_tourney_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
