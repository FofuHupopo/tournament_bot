from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime


Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(127))
    mail = Column(String(127))

    name = Column(String(127))
    surname = Column(String(127))
    
    class_letter = Column(String(1))
    class_number = Column(Integer)
    
    is_active = Column(Boolean(True))
    is_admin = Column(Boolean(False))
    

    def __str__(self) -> str:
        return f"{self.name} {self.surname} {self.class_number}{self.class_letter}"


class CompetitionModel(Base):
    __tablename__ = 'competitions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    description = Column(Text)
    game = Column(String(255))
    server = Column(String(255))
    max_participants = Column(Integer)
    date = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    def __str__(self) -> str:
        return f"{self.name} {self.date} {self.game}"


class RegistrationModel(Base):
    __tablename__ = 'registrations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    nickname = Column(String(255))
    competition_id = Column(Integer, ForeignKey('competitions.id'))
    date = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    is_accepted = Column(Boolean(False))

    user = relationship("UserModel")
    competition = relationship("CompetitionModel")


class UnregisteredMessageModel(Base):
    __tablename__ = "unregistered_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text)
    date = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class RconRuleModel(Base):
    __tablename__ = "rcon_rules"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(127), unique=True)
    ip = Column(String(127))
    port = Column(Integer)
    password = Column(String(127))


# engine = create_engine("postgresql+pg8000://bot:bot@localhost/tournament")
engine = create_engine("sqlite:///temp.db")
Base.metadata.create_all(engine)
