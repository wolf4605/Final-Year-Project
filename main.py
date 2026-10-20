
# ============================== Main Application File ==============================

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from scalar_fastapi import AgentScalarConfig, Layout, get_scalar_api_reference

from src.configs import AppSettings

app = FastAPI(
    title= AppSettings.Title,
    version= AppSettings.Version,
    description= AppSettings.Description,
    terms_of_service=None,
    contact=AppSettings.Contact[0],
    license_info=AppSettings.License
)
"""
The main application variable used to run the Backend.
"""

# ================================== Routers =======================================

# ADD ROUTERS HERE

# ============================== Scalar Docs Setup ==================================

@app.get(
    path= "/",
    include_in_schema=False,
    status_code= 200
)
async def setup_scalar() -> HTMLResponse:
    """
    Overrides the default Swagger UI to a custom Scalar theme.
    """

    css_data:str = f"<head><style>{Path(__file__).parent.joinpath("src").joinpath("static").joinpath("scalar_theme.css").read_text(encoding="utf-8")}</style></head>"
    return get_scalar_api_reference(
        scalar_favicon_url = "https://raw.githubusercontent.com/wolf4605/bondvaultpk.github.io/refs/heads/main/src/assets/logo.svg",
        title= app.title,
        openapi_url= app.openapi_url,
        hide_models= True,
        layout= Layout.MODERN,
        custom_css= css_data,
        agent= AgentScalarConfig(disabled=True)
    )

# =============================== Error Handling ===================================

