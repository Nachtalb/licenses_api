__author__ = "Nachtalb <na@nachtalb.io>"
__maintainer__ = "Nachtalb"
__email__ = "na@nachtalb.io"
__version__ = "0.2.0"
__repository__ = "https://github.com/Nachtalb/licenses_api"
__license__ = "LGPL 3.0"

import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .license import License, licenses

HERE = Path(__file__).parent
app = FastAPI()

app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "public")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    Serve the website's front page, which provides an interactive interface
    for users to explore and interact with the available software licenses.
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "licenses": sorted(licenses.values(), key=lambda i: i.spdx_id),
            "current_year": datetime.datetime.now().year,
            "version": __version__,
        },
    )


@app.get("/licenses")
def get_all_licenses() -> list[License]:
    """
    Retrieve a list of all available software licenses.
    """
    return list(licenses.values())


@app.get("/licenses/{spdx_id}")
def get_license(spdx_id: str) -> License:
    """
    Retrieve a specific software license by its SPDX ID.

    Args:
        spdx_id (str): The SPDX ID of the license to retrieve.

    Returns:
        License: The requested software license.

    Raises:
        HTTPException: If the license with the specified SPDX ID is not found.
    """
    spdx_id = spdx_id.lower()
    if spdx_id not in licenses:
        raise HTTPException(status_code=404, detail="License not found")
    return licenses[spdx_id]


@app.get("/licenses/{spdx_id}/raw")
def get_license_content(spdx_id: str) -> StreamingResponse:
    """
    Retrieve the raw content of a specific software license by its SPDX ID.

    Args:
        spdx_id (str): The SPDX ID of the license to retrieve.

    Returns:
        StreamingResponse: The raw content of the requested software license.

    Raises:
        HTTPException: If the license with the specified SPDX ID is not found.
    """
    spdx_id = spdx_id.lower()
    if spdx_id not in licenses:
        raise HTTPException(status_code=404, detail="License not found")
    license = licenses[spdx_id]
    filename = f"{license.spdx_id}.txt"

    def iter_content():
        yield license.content

    return StreamingResponse(
        iter_content(),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="License API",
        version=__version__,
        description=(
            "An API for retrieving software license information, including SPDX ID, permissions, conditions,"
            " limitations, raw content and more."
        ),
        contact={
            "name": __maintainer__,
            "email": __email__,
            "url": __repository__ + "/issues",
        },
        license_info={
            "name": "LGPL 3.0",
            "url": "https://www.gnu.org/licenses/lgpl-3.0.en.html",
        },
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
