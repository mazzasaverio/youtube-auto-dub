from fastapi import FastAPI
from sqlalchemy.orm import Session
from loguru import logger
from .database.connection import SessionLocal, engine
from .database.models import Base, Item

# from .translation.text_translator import load_model, translate_text
# import os


Base.metadata.create_all(bind=engine)


app = FastAPI()


@app.post("/pubsub-handler")
async def pubsub_handler():
    # Database Operation: Adding an item
    with SessionLocal() as session:
        new_item = Item(name="Test Item")
        session.add(new_item)
        session.commit()
        logger.info(f"New item added to database: {new_item.name}")

    # Database Operation: Reading items
    with Session(engine) as session:
        items = session.query(Item).all()
        for item in items:
            logger.info(f"Retrieved item from db: {item.name}")

    # # Translation Operation
    # text = """Wie oben bereits erwähnt, ist die Transparenz ein entscheidender Treiber für diese Entwicklungen. Im Bereich
    #           Emissionen wird laut House Gas unterschieden in Emissionen, welche dem Unternehmen
    #           direkt zuzuordnen sind, z. B. die eingekaufte Energie und
    #           die Prozessemissionen. Diese zusam"""
    # source_language = "de"
    # target_language = "en"

    # # Load model
    # model_name = "facebook/m2m100_418M"
    # storage_option = os.getenv("STORAGE_OPTION")
    # tokenizer, model = load_model(model_name, storage_option)

    # # Perform translation
    # translated_text = translate_text(
    #     text, source_language, target_language, tokenizer, model
    # )
    # logger.info(f"Original text: {text}")
    # logger.info(f"Translated text: {translated_text}")

    return {
        "message": "Pub/Sub handler executed successfully, database and translation tasks completed."
    }
