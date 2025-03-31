# Lucid task

## Features

- **User Authentication:** Secure signup and login endpoints using JWT tokens.
- **Posts Management:** Endpoints to create, retrieve (with per-user caching), and delete posts.
- **Security:** Passwords are hashed using bcrypt.
- **Configuration:** Environment-specific settings are managed via environment variables.
- **Containerized:** Easily deployable using Docker and Docker Compose.

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed on your system.

### Environment Configuration

**Rename the Environment File**

In the project root, rename the file `.env.example` to `.env`:

```bash
mv .env.example .env
```

### Running with Docker

From the project root, run:

```bash
docker-compose up --build
```

The FastAPI app will be accessible at http://localhost:8080 as defined in docker-compose.yml.
