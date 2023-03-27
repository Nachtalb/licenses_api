# Software License API

This project is a FastAPI implementation that provides an interactive interface
for users to explore and interact with various software licenses. The license
files are sourced from
[choosealicense.com](https://github.com/github/choosealicense.com), and the
author of this project is [Nachtalb](https://github.com/Nachtalb).

The source repository for this project can be found at
[https://github.com/Nachtalb/licenses_api](https://github.com/Nachtalb/licenses_api).

## Website and API Documentation

You can access the website for this application at
[https://licenses.nachtalb.io](https://licenses.nachtalb.io).

The API documentation is available at
[https://licenses.nachtalb.io/docs](https://licenses.nachtalb.io/docs).

### Short Overview of the API Endpoints

The following API endpoints are available:

1. `GET /` - Serve the website's front page, which provides an interactive
   interface for users to explore and interact with the available software
   licenses.

2. `GET /licenses` - Retrieve a list of all available software licenses.

3. `GET /licenses/{spdx_id}` - Retrieve a specific software license by its SPDX
   ID.

4. `GET /licenses/{spdx_id}/raw` - Retrieve the raw content of a specific
   software license by its SPDX ID.

## Installation

The installation is done using [Poetry](https://python-poetry.org/). To install
the project, follow these steps:

```bash
# Clone the repository
git clone https://github.com/Nachtalb/license_api.git
# Navigate to the project directory
cd license_api
# Install the dependencies using Poetry
poetry install
# Run the FastAPI server
poetry run uvicorn license.main:app --reload
```

### Installation using Docker

You can also run the application using Docker. There are two methods to do this:
using the Docker CLI command or using Docker Compose.

### Docker CLI

To run the application using the Docker CLI, execute the following command:

```bash
docker run --name license_api -p 8000:8000 ghcr.io/nachtalb/licenses_api:latest
```

The application will be accessible at `http://localhost:8000`.

### Docker Compose

Alternatively, you can use Docker Compose to run the application. Create a file
named `docker-compose.yml` with the following content:

```yaml
version: "3"

services:
  license_api:
    image: ghcr.io/nachtalb/licenses_api:latest
    container_name: license_api
    ports:
      - "8000:8000"
    restart: unless-stopped
```

Now, run the following command to start the application using Docker Compose:

```bash
docker-compose up -d
```

The application will be accessible at `http://localhost:8000`.

## License

This project is licensed under the
[GNU Lesser General Public License v3.0](https://www.gnu.org/licenses/lgpl-3.0.en.html).
