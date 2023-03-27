from pathlib import Path

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
