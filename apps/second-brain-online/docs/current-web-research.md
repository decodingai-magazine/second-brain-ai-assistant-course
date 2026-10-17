# Research current sources for your Second Brain

Your Second Brain captures the resources you have collected. When researching a
fast-moving topic, such as PDF parsing tools or LLM optimization methods, compare
that knowledge with current primary sources before updating your notes.

This optional exercise uses [Parallel Search MCP](https://docs.parallel.ai/integrations/mcp/search-mcp)
in VS Code. It provides free web search and page fetching without a Parallel
account or API key. Anonymous search uses Fast mode and has usage limits.
The course's Gradio agent does not load this editor configuration; its MongoDB
retrieval and summarization tools continue to work as before.

## Connect VS Code

Use a current version of VS Code with GitHub Copilot Chat and access to an agent
that supports MCP tools. See [VS Code's MCP setup guide](https://code.visualstudio.com/docs/copilot/customization/mcp-servers)
for client requirements and organization settings. The editor's chat model needs
its own access; the course's `OPENAI_API_KEY` does not configure Copilot.

1. Open the repository folder in VS Code.
2. Create `.vscode/mcp.json` at the repository root with the following configuration.
   If the file already exists, add only the `parallel-search` entry to its existing
   `servers` object, preserving your other servers.

   ```json
   {
     "servers": {
       "parallel-search": {
         "type": "http",
         "url": "https://search.parallel.ai/mcp",
         "headers": {
           "User-Agent": "second-brain-ai-assistant-course"
         }
       }
     }
   }
   ```

3. Review the configuration and enable Workspace Trust only if you trust the
   repository. Run **MCP: List Servers** from the Command Palette, select
   `parallel-search`, and start it.
4. In an agent chat, use **Configure Tools** in the chat input to enable the
   server's `web_search` and `web_fetch` tools. Confirm that both tools appear
   before starting the exercise.

This configuration connects anonymously over HTTP. It does not need an
`Authorization` header or any changes to the course's `.env` files.

## Compare curated knowledge with current evidence

First, ask the [Module 6 assistant](../README.md#module-6-running-the-rag-agentic-app-and-llmops-layer)
a question supported by your indexed notes, for example:

> Which PDF parsing tools are covered in my Second Brain, and what tradeoffs do
> the saved resources describe?

Keep the answer and its source references for comparison. Then start a separate
VS Code agent chat and ask:

> Use Parallel's web_search to find current official documentation for Docling
> and Marker PDF parsing. Use web_fetch to read the relevant pages. Compare their
> supported input formats, OCR options, and license terms. Cite a URL for each
> claim, include the date you checked it, and mark anything you cannot verify.

Inspect the tool calls: search should return source URLs and excerpts; fetch
should return page content for the selected URLs. Open the cited pages and check
the evidence yourself. If a fetch fails or a claim is missing from the source,
record it as unverified rather than filling the gap from model memory.

Compare the findings with your original answer. Which saved claims still hold?
Which need a newer source? Add selected links and your own summary to your
personal notes, keeping the source URL and date checked. For a personal Notion
collection, follow the offline module's [Notion setup](../../second-brain-offline/README.md#-setup-notion-optional)
and [data preparation and ETL steps](../../second-brain-offline/README.md#prepare-notion-data),
then rebuild the Module 5 index before expecting newly collected resources in
the course assistant. Editor research results are not ingested automatically.

Use public research questions with the web tools. Keep private notes and course
credentials out of search queries and fetched URLs.

## Troubleshooting and cleanup

- If the tools are missing, check that the server is started, trusted, and enabled
  for the current chat. Organization settings may restrict MCP access.
- If anonymous usage is limited, pause and retry later. For sustained use, see
  Parallel's [authentication options](https://docs.parallel.ai/integrations/mcp/search-mcp#installation).
- To stop using the server, stop it with **MCP: List Servers** and remove only the
  `parallel-search` entry from `.vscode/mcp.json`.
