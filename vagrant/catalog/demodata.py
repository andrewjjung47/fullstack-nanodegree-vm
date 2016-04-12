from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


guitar = Category(name="guitar")
base = Category(name="base")
drum = Category(name="drum")
keyboard = Category(name="keyboard")

session.add(guitar)
session.add(base)
session.add(drum)
session.add(keyboard)

session.commit()

print "Imported demo data."
