"""This Module Imports Settings from pyproject.toml."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class _AppSettings(BaseSettings):
    """Contains all the main app settings settings."""

    Title: str = Field(default=..., alias= "name", description= "Title of the Application.")
    """Title of the Application."""
    Summary: str = Field(default=..., alias= "summary", description= "Summary of the Application.")
    """Summary of the Application."""
    Version: str = Field(default=..., alias= "version", description="Current application version.") 
    """Current application version."""
    Description: str = Field(default=..., alias="description", description="A detailed explaination of the Project.")
    """A detailed explaination of the Project."""
    Contact: list[dict[str,str]] = Field(default=..., alias="authors", description="A detailed explaination of the Project.")

    model_config = SettingsConfigDict(
        toml_file=Path(__file__).parent.parent.parent.joinpath("pyproject.toml"),
        toml_table_header= ("project",),
        extra="ignore",
        case_sensitive=False,
        populate_by_name= True
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
) -> tuple[PydanticBaseSettingsSource, ...]:
        """Prioritizes loading variables directly from the defined TOML configuration file."""
        return (TomlConfigSettingsSource(settings_cls),)

AppSettings:_AppSettings = _AppSettings()
"""Contains all the main app settings settings."""