from loguru import logger
import os
import torch
import app.services.openvoice.se_extractor as se_extractor
from app.services.openvoice.api import BaseSpeakerTTS, ToneColorConverter

# Adjust ROOT_DIR to point two levels up from the current directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ckpt_path = os.path.join(ROOT_DIR, "checkpoints")

# Definizione delle directory relative
directories = ["processed_audios", "downloaded_videos", "captions", "final_videos"]

base_dir = os.path.join(ROOT_DIR, "data")

# Creazione delle directory se non esistono
for dir_name in directories:
    dir_path = os.path.join(base_dir, dir_name)
    os.makedirs(dir_path, exist_ok=True)



def process_audio(
    audio_input_path: str,
    audio_output_path: str,
    text: str,
    style: str = "default",
    speed: float = 1.0,
    language: str = "English",
    encode_message: str = "@MyShell",
):
    try:
        logger.info("Starting audio processing.")

        ckpt_base = os.path.join(ckpt_path, "base_speakers/EN")
        ckpt_converter = os.path.join(ckpt_path, "converter")
        device = "cuda:0" if torch.cuda.is_available() else "cpu"

        logger.info("Initializing BaseSpeakerTTS model.")
        base_speaker_tts = BaseSpeakerTTS(
            os.path.join(ckpt_base, "config.json"), device=device
        )
        base_speaker_tts.load_ckpt(os.path.join(ckpt_base, "checkpoint.pth"))

        logger.info("Initializing ToneColorConverter model.")
        tone_color_converter = ToneColorConverter(
            os.path.join(ckpt_converter, "config.json"), device=device
        )
        tone_color_converter.load_ckpt(os.path.join(ckpt_converter, "checkpoint.pth"))

        logger.info("Loading source tone color embedding.")
        source_se = torch.load(os.path.join(ckpt_base, "en_default_se.pth")).to(device)

        logger.info("Extracting tone color embedding of the reference speaker.")
        target_se, _ = se_extractor.get_se(
            audio_input_path, tone_color_converter, target_dir="processed", vad=True
        )

        temp_path = f"{audio_output_path}_tmp.wav"

        logger.info("Running the base speaker TTS.")
        base_speaker_tts.tts(
            text, temp_path, speaker=style, language=language, speed=speed
        )

        logger.info("Converting tone color and exporting audio.")
        tone_color_converter.convert(
            audio_src_path=temp_path,
            src_se=source_se,
            tgt_se=target_se,
            output_path=audio_output_path,
            message=encode_message,
        )

        os.remove(temp_path)

        logger.info("Audio processing completed successfully.")
    except Exception as e:
        logger.error(f"Error in process_audio: {e}")
        raise


# Rest of the code (if any)...
