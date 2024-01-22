from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import os


def load_model(model_name, storage_option):
    model_dir = "models"

    bucket_name = os.getenv("GCS_BUCKET_NAME")

    # Configure cache path based on storage option
    cache_dir = (
        os.path.join(model_dir, model_name)
        if storage_option == "local"
        else f"gs://{bucket_name}/{model_dir}/{model_name}"
    )

    # Load tokenizer and model
    tokenizer = M2M100Tokenizer.from_pretrained(model_name, cache_dir=cache_dir)
    model = M2M100ForConditionalGeneration.from_pretrained(
        model_name, cache_dir=cache_dir
    )
    return tokenizer, model


def translate_text(text, source_language, target_language, tokenizer, model):
    tokenizer.src_lang = source_language
    encoded = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(
        **encoded, forced_bos_token_id=tokenizer.get_lang_id(target_language)
    )
    translation = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return translation[0]
