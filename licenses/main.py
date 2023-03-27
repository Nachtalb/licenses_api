from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
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

    @validator("using", pre=True, always=True)
    def set_using_default(cls, value):
        return value or {}


def load_licenses() -> dict:
    yaml = YAML()
    licenses = {}
    for license_path in HERE.glob("licenses/*.txt"):
        file_content = license_path.read_text().split("---")
        license_data = yaml.load(file_content[1])
        license_data["content"] = file_content[2]
        license = License(**license_data)
        licenses[license.spdx_id.lower()] = license
    return licenses


licenses = load_licenses()

app = FastAPI()

app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
app = FastAPI()


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """
    Serve the website's front page, which provides an interactive interface
    for users to explore and interact with the available software licenses.
    """
    return (HERE / "public/index.html").read_text()


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


@app.get("/licenses/{spdx_id}/raw", response_class=PlainTextResponse)
def get_license_content(spdx_id: str) -> str:
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
    return licenses[spdx_id].content
