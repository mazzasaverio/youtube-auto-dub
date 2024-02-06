# FastAPI CloudRun Starter

This repository serves as a starter template for setting up a FastAPI backend using Google CloudRun. It's designed to streamline the process of deploying a FastAPI application using modern infrastructure as code principles.

## Features

- Terraform-based infrastructure setup.
- Integration with GitHub Actions for continuous integration.
- Automatic trigger setup for Cloud Build.
- Secure storage of secrets using Secret Manager.

## Getting Started

### Prerequisites

1. **Google Cloud Platform Account**: Ensure you have an active GCP account. [Sign up here](https://cloud.google.com/) if needed.
2. **Project Setup**: Create a new GCP project and note down the project ID.
3. **Service Account**: Create a service account with 'Owner' permissions in your GCP project and generate a JSON key file.
4. **Connecting Cloud Build to Your GitHub Account**: Create a personal access token in GitHub with `repo` and `read:user` permissions. For organization apps, include `read:org` permission. [Guide here](https://cloud.google.com/build/docs/automating-builds/github/connect-repo-github?generation=2nd-gen#terraform_1).

### Terraform Configuration

- **Rename File**: Rename `terraform.tfvars.example` to `terraform.tfvars`.
- **Insert Credentials**: Fill in your credentials in the `terraform.tfvars` file.

### Docker Configuration

The `Dockerfile` is configured to use the NVIDIA CUDA base image with FastAPI dependencies. The application is exposed on port 8000 and can be customized as needed.

### FastAPI Application

The `main.py` script is the entry point for the FastAPI application. It includes basic routes and can be extended for additional functionalit

## Usage

To deploy the infrastructure and application:

1. Initialize Terraform:
   ```bash
   terraform init
   ```
2. Apply Terraform configuration:
   ```bash
   terraform apply
   ```
3. To build and run the Docker container locally, use:
   ```bash
   docker-compose up --build
   ```

## Contributing

Contributions to enhance this starter template are welcome. Please follow standard GitHub contribution guidelines.
