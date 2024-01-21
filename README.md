# Cloud Run Docker Image Template

This repository provides a Docker image template designed for deployment using Google Cloud's Cloud Build and to be triggered by Cloud Run whenever files are uploaded to storage.

## Overview

When storage dispatches a notification, it is captured through pub/sub and triggers two tests:

1. Read and write operations on a Cloud SQL PostgreSQL database.
2. Storing a pre-trained model from Hugging Face in the storage used as cache, which is then read and utilized each time the Cloud Run is triggered.

FastAPI is used to handle pub/sub requests. For setting up infrastructure components like Cloud SQL, Cloud Build, and Cloud Run, etc., please refer to another repository where you'll find the specific Terraform code for this use case.

## Key Functions

The main functionalities – database connectivity with read/write operations and text translation using a pre-trained model fetched from Hugging Face – are all triggered in the cloud when a message from pub/sub arrives. However, for local testing and independent execution, these functions can be run directly from the terminal.

## Local Testing of /pubsub-handler

To test the `/pubsub-handler` endpoint locally:

1. Start the FastAPI server with the following command:

   ```bash
   uvicorn src.main:app --reload
   ```

   This command will host the application on a local server, usually available at `http://127.0.0.1:8000`.

2. Send a POST request to your locally running server. You can use Postman or a simple curl command:
   ```bash
   curl -X POST http://127.0.0.1:8000/pubsub-handler
   ```
