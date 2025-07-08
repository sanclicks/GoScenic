# Project Progress and Technology Overview

## Completed Tasks
- Removed the obsolete `GoScenic.git/` mirror directory from version control.
- Added the directory to `.gitignore` so it does not return in future commits.
- Deleted an outdated Terraform state file (`terraform/errored.tfstate`) to keep the repository clean.

## Technology Used
- **Python & FastAPI**: Backend API located in `goscenic-backend/`.
- **Docker**: Containerization instructions via `goscenic-backend/Dockerfile`.
- **Terraform**: Infrastructure-as-code files inside the `terraform/` directory.

These steps prepare the repository for further development by ensuring only necessary resources are tracked.

