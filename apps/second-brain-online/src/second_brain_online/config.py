from loguru import logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    A Pydantic-based settings class for managing application configurations.
    """

    # --- Pydantic Settings ---
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )

    # --- Comet ML & Opik Configuration ---
    COMET_API_KEY: str | None = Field(
        default=None, description="API key for Comet ML and Opik services."
    )
    COMET_PROJECT: str = Field(
        default="second_brain_course",
        description="Project name for Comet ML and Opik tracking.",
    )

    # --- Hugging Face Configuration ---
    HUGGINGFACE_ACCESS_TOKEN: str | None = Field(
        default=None, description="Access token for Hugging Face API authentication."
    )
    USE_HUGGINGFACE_DEDICATED_ENDPOINT: bool = Field(
        default=False,
        description="Whether to use the dedicated endpoint for summarizing responses. If True, we will use the dedicated endpoint instead of OpenAI.",
    )
    HUGGINGFACE_DEDICATED_ENDPOINT: str | None = Field(
        default=None,
        description="Dedicated endpoint URL for real-time inference. "
        "If provided, we will use the dedicated endpoint instead of OpenAI. "
        "For example, https://um18v2aeit3f6g1b.eu-west-1.aws.endpoints.huggingface.cloud/v1/, "
        "with /v1 after the endpoint URL.",
    )

    # --- MongoDB Atlas Configuration ---
    MONGODB_DATABASE_NAME: str = Field(
        default="second_brain_course",
        description="Name of the MongoDB database.",
    )
    MONGODB_URI: str = Field(
        default="mongodb://decodingml:decodingml@localhost:27017/?directConnection=true",
        description="Connection URI for the local MongoDB Atlas instance.",
    )

    # --- Astraflow API Configuration ---
    # Astraflow by UCloud — OpenAI-compatible platform supporting 200+ models (global endpoint)
    # Global endpoint: https://api-us-ca.umodelverse.ai/v1  |  Sign up: https://astraflow.ucloud-global.com
    # China endpoint:  https://api.modelverse.cn/v1         |  Sign up: https://astraflow.ucloud.cn
    USE_ASTRAFLOW: bool = Field(
        default=False,
        description="When True, route LLM requests to Astraflow instead of OpenAI.",
    )
    ASTRAFLOW_API_KEY: str | None = Field(
        default=None,
        description="API key for Astraflow global endpoint (https://api-us-ca.umodelverse.ai/v1).",
    )
    ASTRAFLOW_CN_API_KEY: str | None = Field(
        default=None,
        description="API key for Astraflow China endpoint (https://api.modelverse.cn/v1).",
    )

    # --- OpenAI API Configuration ---
    OPENAI_API_KEY: str = Field(
        description="API key for OpenAI service authentication.",
    )
    OPENAI_MODEL_ID: str = Field(
        default="gpt-4o-mini", description="Identifier for the OpenAI model to be used."
    )

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def check_not_empty(cls, value: str, info) -> str:
        if not value or value.strip() == "":
            logger.error(f"{info.field_name} cannot be empty.")
            raise ValueError(f"{info.field_name} cannot be empty.")
        return value


try:
    settings = Settings()
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    raise SystemExit(e)
