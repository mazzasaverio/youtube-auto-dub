# [titolo]

This repository aims to establish a foundation for deploying a backend using Docker, which utilizes OpenVoice and FastAPI. The main functionality is to recognize the voice timbre from a YouTube video and recreate the same video with a text-to-speech model in the same timbre after translating the subtitles. This is just a basic setup.

## Steps:

1. Submit a YouTube link via the endpoint `/api/v1/download/`.
2. The final processed video is saved in `backend/data/final_videos`.

## Features

- Deployment via GitHub Actions and Cloud Build on a Cloud Run.

Currently ho provato the deployment is on a Cloud Run (thus, only CPU is used for inference).

For a starting template on setting up Cloud Run with Terraform, refer to this link:
[FastAPI-CloudRun-Starter](https://github.com/mazzasaverio/fastapi-cloudrun-starter)

## Next Steps

- Test better models.
- Test serverless GPU.
- Add a frontend.
- Improve translation synchronization.

## Local Installation Instructions

We recommend the following for local installation:

```
conda install mamba -n base -c conda-forge

mamba create -n youtube-auto-dub python=3.9 -y

mamba install -n youtube-auto-dub pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 pytorch-cuda=11.7 -c pytorch -c nvidia -y

conda activate youtube-auto-dub

pip install -r requirements.txt
```

Download the checkpoint from [here](https://myshell-public-repo-hosting.s3.amazonaws.com/checkpoints_1226.zip) and extract it to the `checkpoints` folder. Insert the checkpoint found in `checkpoints_1226` into the `backend` folder.

conda install mamba -n base -c conda-forge

mamba create -n youtube-auto-dub python=3.9 -y

mamba install -n youtube-auto-dub pytorch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1 pytorch-cuda=11.7 -c pytorch -c nvidia -y

conda activate youtube-auto-dub

pip install pytube moviepy fastapi uvicorn loguru youtube-dl youtube-transcript-api librosa

pip install googletrans==4.0.0-rc1

sudo apt -y install -qq aria2 unzip

sudo aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://myshell-public-repo-hosting.s3.amazonaws.com/checkpoints_1226.zip -d /code -o checkpoints_1226.zip

sudo unzip /code/checkpoints_1226.zip

## Reference and Inspiration

|                      Repository                      | Stars | Forks | Last Updated |               About               |
| :--------------------------------------------------: | :---: | :---: | :----------: | :-------------------------------: |
| [OpenVoice](https://github.com/myshell-ai/OpenVoice) | 13972 | 1213  |  2024-02-09  | Instant voice cloning by MyShell. |

<!-- START_SECTION:under-review -->
## Repositories Under Review

| Repository | Stars | Forks | Last Updated | About |
|:-:|:-:|:-:|:-:|:-:|
<!-- END_SECTION:under-review -->
<!-- START_SECTION:reference-inspiration -->
## Reference and Inspiration

| Repository | Stars | Forks | Last Updated | About |
|:-:|:-:|:-:|:-:|:-:|
| [OpenVoice](https://github.com/myshell-ai/OpenVoice) | 13973 | 1213 | 2024-02-09 | Instant voice cloning by MyShell. |
<!-- END_SECTION:reference-inspiration -->