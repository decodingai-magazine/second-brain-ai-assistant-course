from openai import OpenAI
from opik import track
from smolagents import Tool

from second_brain_online.config import settings


class HuggingFaceEndpointSummarizerTool(Tool):
    name = "huggingface_summarizer"
    description = """Use this tool to summarize a piece of text. Especially useful when you need to summarize a document."""

    inputs = {
        "text": {
            "type": "string",
            "description": """The text to summarize.""",
        }
    }
    output_type = "string"

    SYSTEM_PROMPT = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
You are a helpful assistant specialized in summarizing documents. Generate a concise TL;DR summary in markdown format having a maximum of 512 characters of the key findings from the provided documents, highlighting the most significant insights

### Input:
{content}

### Response:
"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        assert settings.HUGGINGFACE_ACCESS_TOKEN is not None, (
            "HUGGINGFACE_ACCESS_TOKEN is required to use the dedicated endpoint. Add it to the .env file."
        )
        assert settings.HUGGINGFACE_DEDICATED_ENDPOINT is not None, (
            "HUGGINGFACE_DEDICATED_ENDPOINT is required to use the dedicated endpoint. Add it to the .env file."
        )

        self.__client = OpenAI(
            base_url=settings.HUGGINGFACE_DEDICATED_ENDPOINT,
            api_key=settings.HUGGINGFACE_ACCESS_TOKEN,
        )

    @track
    def forward(self, text: str) -> str:
        result = self.__client.chat.completions.create(
            model="tgi",
            messages=[
                {
                    "role": "user",
                    "content": self.SYSTEM_PROMPT.format(content=text),
                },
            ],
        )

        return result.choices[0].message.content


class OpenAISummarizerTool(Tool):
    name = "openai_summarizer"
    description = """Use this tool to summarize a piece of text. Especially useful when you need to summarize a document or a list of documents."""

    inputs = {
        "text": {
            "type": "string",
            "description": """The text to summarize.""",
        }
    }
    output_type = "string"

    SYSTEM_PROMPT = """You are a helpful assistant specialized in summarizing documents.
Your task is to create a clear, concise TL;DR summary in plain text.
Things to keep in mind while summarizing:
- titles of sections and sub-sections
- tags such as Generative AI, LLMs, etc.
- entities such as persons, organizations, processes, people, etc.
- the style such as the type, sentiment and writing style of the document
- the main findings and insights while preserving key information and main ideas
- ignore any irrelevant information such as cookie policies, privacy policies, HTTP errors,etc.

Document content:
{content}

Generate a concise summary of the key findings from the provided documents, highlighting the most significant insights and implications.
Return the document in plain text format regardless of the original format.
"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if settings.USE_ASTRAFLOW:
            self.__client = OpenAI(
                base_url="https://api-us-ca.umodelverse.ai/v1",
                api_key=settings.ASTRAFLOW_API_KEY,
            )
        else:
            self.__client = OpenAI(
                base_url="https://api.openai.com/v1",
                api_key=settings.OPENAI_API_KEY,
            )

    @track
    def forward(self, text: str) -> str:
        result = self.__client.chat.completions.create(
            model=settings.OPENAI_MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": self.SYSTEM_PROMPT.format(content=text),
                },
            ],
        )

        return result.choices[0].message.content
