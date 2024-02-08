from pydantic import BaseModel, HttpUrl


class VideoDownloadRequest(BaseModel):
    url: HttpUrl = "https://youtube.com/shorts/pcydlhq2MWI?si=DDLpxVeckksS61t-"
