__author__ = "Nachtalb <na@nachtalb.io>"
__maintainer__ = "Nachtalb"
__email__ = "na@nachtalb.io"
__version__ = "0.1.0"
__repository__ = "https://github.com/Nachtalb/licenses_api"
__license__ = "LGPL 3.0"

import io
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, validator
from ruamel.yaml import YAML

HERE = Path(__file__).parent


class License(BaseModel):
    """
    A model representing a software license, including its SPDX ID, permissions,
    conditions, limitations, and other relevant information.
    """

    title: str = Field(..., description="The full name of the license")
    spdx_id: str = Field(..., description="The SPDX identifier for the license", alias="spdx-id")
    nickname: str | None = Field(None, description="An alternative or shortened name for the license")
    description: str = Field(..., description="A brief description of the license")
    how: str = Field(..., description="Guidelines on how to apply the license")
    note: str | None = Field(None, description="Additional notes or comments about the license")
    using: dict[str, str] = Field(default_factory=dict, description="Examples of projects using the license")
    permissions: list[str] = Field(..., description="List of permissions granted by the license")
    conditions: list[str] = Field(..., description="List of conditions that must be met when using the license")
    limitations: list[str] = Field(..., description="List of limitations imposed by the license")
    content: str = Field(..., description="The full license text")

    @validator("*", pre=True, always=True)
    def set_using_default(cls, value, field):
        if field.name == "using":
            return value or {}
        elif field.name in ["permissions", "conditions", "limitations"]:
            return value or []
        return value


def load_licenses() -> dict:
    yaml = YAML()
    licenses = {}
    for license_path in HERE.glob("licenses/*.txt"):
        file_content = license_path.read_text().split("---", 2)
        license_data = yaml.load(file_content[1])
        license_data["content"] = file_content[2].strip()
        license = License(**license_data)
        licenses[license.spdx_id.lower()] = license
    return licenses


licenses = load_licenses()

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
        "index.html", {"request": request, "licenses": sorted(licenses.values(), key=lambda i: i.spdx_id)}
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
        str: The raw content of the requested software license.

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
