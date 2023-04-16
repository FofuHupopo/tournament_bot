from aiogram.dispatcher.filters.state import StatesGroup, State


class JoinState(StatesGroup):
    name = State()
    mail = State()
    nickname = State()


class CompetitionListState(StatesGroup):
    current_competition = State()


class RconCommandState(StatesGroup):
    server_name = State()
    cmd = State()


class AddRconRuleState(StatesGroup):
    name = State()
    server_ip = State()
    server_port = State()
    password = State()
