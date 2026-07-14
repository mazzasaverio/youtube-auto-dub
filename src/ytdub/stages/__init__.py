"""Pipeline stages: download -> transcribe -> translate -> synthesize -> synchronize -> assemble.

Each stage is a small module with a single entry function and *lazy* heavy imports,
so importing the package (and running ``ytdub --help``) never requires torch, whisper
or a TTS engine to be installed.
"""
