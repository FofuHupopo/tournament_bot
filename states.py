from aiogram.dispatcher.filters.state import StatesGroup, State


class QuestionState(StatesGroup):
    question = State()


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
    

class RegistrationState(StatesGroup):
    competition_id = State()
    nickname = State()


class CompetitionDetailState(StatesGroup):
    competition_id = State()
    name = State()
    description = State()
    date = State()
    
    notification = State()
    registration_number = State()


class AddCompetitionState(StatesGroup):
    name = State()
    description = State()
    game = State()
    server = State()
    max_participants = State()
    date = State()


class UserSignupState(StatesGroup):
    mail = State()
    surname = State()
    name = State()
    class_number = State()
    class_letter = State()
    