# from fastapi import FastAPI
# from sqlalchemy.orm import Session
# from loguru import logger
# from .database.connection import SessionLocal, engine
# from .database.models import Base, Item

# # from .translation.text_translator import load_model, translate_text
# # import os


# Base.metadata.create_all(bind=engine)


# app = FastAPI()


# @app.post("/pubsub-handler")
# async def pubsub_handler():
#     # Database Operation: Adding an item
#     with SessionLocal() as session:
#         new_item = Item(name="Test Item")
#         session.add(new_item)
#         session.commit()
#         logger.info(f"New item added to database: {new_item.name}")

#     # Database Operation: Reading items
#     with Session(engine) as session:
#         items = session.query(Item).all()
#         for item in items:
#             logger.info(f"Retrieved item from database: {item.name}")

#     # # Translation Operation
#     # text = """Wie oben bereits erwähnt, ist die Transparenz ein entscheidender Treiber für diese Entwicklungen. Im Bereich
#     #           Emissionen wird laut House Gas unterschieden in Emissionen, welche dem Unternehmen
#     #           direkt zuzuordnen sind, z. B. die eingekaufte Energie und
#     #           die Prozessemissionen. Diese zusam"""
#     # source_language = "de"
#     # target_language = "en"

#     # # Load model
#     # model_name = "facebook/m2m100_418M"
#     # storage_option = os.getenv("STORAGE_OPTION")
#     # tokenizer, model = load_model(model_name, storage_option)

#     # # Perform translation
#     # translated_text = translate_text(
#     #     text, source_language, target_language, tokenizer, model
#     # )
#     # logger.info(f"Original text: {text}")
#     # logger.info(f"Translated text: {translated_text}")

#     return {
#         "message": "Pub/Sub handler executed successfully, database and translation tasks completed."
#     }


from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from dotenv import load_dotenv

load_dotenv()


# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Accessing environment variables
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# Creating SQLAlchemy engine
logger.info("Creating database engine.")
engine = create_engine(DATABASE_URL)

# SQLAlchemy session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base model for creating ORM models
Base = declarative_base()

# Creating FastAPI app
app = FastAPI()


# Defining a sample model
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    def __repr__(self):
        return f"<Item id={self.id} name={self.name}>"


# Creating tables in the database (if they don't already exist)
logger.info("Creating tables in the database.")
Base.metadata.create_all(bind=engine)


@app.post("/pubsub-handler")
def pubsub_handler():
    # Logica per gestire il messaggio Pub/Sub

    db = SessionLocal()
    try:
        new_item = Item(name="nuovotest2")
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        logger.info("Item succesfsfully added.")

    except Exception as e:
        logger.error(f"Error during item addition: {e}")
        raise
    finally:
        db.close()

    db = SessionLocal()
    try:
        logger.info("Reading items from the database.")
        items = db.query(Item).all()

        return items
    except Exception as e:
        logger.error(f"Error during database read: {e}")
        raise
    finally:
        db.close()
