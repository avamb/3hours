"""
MINDSETHAPPYBOT - Social profile FSM states
"""
from aiogram.fsm.state import State, StatesGroup


class SocialProfileStates(StatesGroup):
    """States for social profile editing"""
    waiting_for_social_link = State()
    waiting_for_bio = State()
