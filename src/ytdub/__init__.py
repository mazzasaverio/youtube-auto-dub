"""ytdub — local-first, open-source YouTube dubbing with voice cloning.

The public surface is intentionally small: build a :class:`~ytdub.config.Settings`,
then call :func:`ytdub.pipeline.dub`. Everything else is an implementation detail
of the individual pipeline stages under :mod:`ytdub.stages`.
"""

from ytdub.config import Settings

__version__ = "0.2.0"
__all__ = ["Settings", "__version__"]
