# =============================================================================
# IMPORTS — tools we need
# =============================================================================
import azure.functions as func   # Azure Functions SDK (same as before)
import logging                   # For printing log messages (same as before)
import json                      # For working with JSON (same as before)
import re                        # For pattern matching (same as before)
import uuid                      # NEW — generates unique IDs like "a3f9-b2c1-..."
import os                        # NEW — lets us read environment variables
from datetime import datetime    # For timestamps (same as before)
from azure.cosmos import CosmosClient  # NEW — lets Python talk to Cosmos DB

# =============================================================================
# APP SETUP
# =============================================================================
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Read the connection string from environment variables
# os.environ.get() looks inside local.settings.json when running locally
# and looks inside Azure App Settings when running in the cloud
COSMOS_CONNECTION_STRING = os.environ.get("COSMOS_CONNECTION_STRING")
DATABASE_NAME = "TextAnalyzerDB"      # must match what you created in Azure
CONTAINER_NAME = "AnalysisResults"    # must match what you created in Azure


def get_container():
    """
    This helper function connects to Cosmos DB and returns our container.
    Think of it like opening the filing cabinet drawer.
    We call this every time we need to read or write to the database.
    """
    client = CosmosClient.from_connection_string(COSMOS_CONNECTION_STRING)
    database = client.get_database_client(DATABASE_NAME)
    return database.get_container_client(CONTAINER_NAME)


# =============================================================================
# ENDPOINT 1: TextAnalyzer  →  /api/TextAnalyzer
# Same as before BUT now saves results to the database
# =============================================================================
@app.route(route="TextAnalyzer")
def TextAnalyzer(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Text Analyzer API was called!')

    # ── Get the text (same as before) ──────────────────────────────────────
    text = req.params.get('text')
    if not text:
        try:
            req_body = req.get_json()
            text = req_body.get('text')
        except ValueError:
            pass

    if text:
        # ── Analyze the text (same as before) ──────────────────────────────
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        char_count_no_spaces = len(text.replace(" ", ""))
        sentence_count = len(re.findall(r'[.!?]+', text)) or 1
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        reading_time_minutes = round(word_count / 200, 1)
        avg_word_length = round(char_count_no_spaces / word_count, 1) if word_count > 0 else 0
        longest_word = max(words, key=len) if words else ""

        # ── NEW: Build a document to save ──────────────────────────────────
        # uuid.uuid4() generates a random unique ID every time
        # str() converts it to a string like "3f2504e0-4f89-11d3-9a0c-0305e82c3301"
        doc_id = str(uuid.uuid4())

        # This is the object we will save to Cosmos DB
        # Cosmos DB requires every document to have an "id" field
        document = {
            "id": doc_id,
            "originalText": text,
            "analysis": {
                "wordCount": word_count,
                "characterCount": char_count,
                "characterCountNoSpaces": char_count_no_spaces,
                "sentenceCount": sentence_count,
                "paragraphCount": paragraph_count,
                "averageWordLength": avg_word_length,
                "longestWord": longest_word,
                "readingTimeMinutes": reading_time_minutes
            },
            "metadata": {
                "analyzedAt": datetime.utcnow().isoformat(),
                "textPreview": text[:100] + "..." if len(text) > 100 else text
            }
        }

        # ── NEW: Save to Cosmos DB ──────────────────────────────────────────
        # We wrap this in try/except so if the database save fails,
        # we still return the analysis result to the user
        try:
            container = get_container()
            container.create_item(body=document)  # this is the actual save
            logging.info(f"Saved to database with id: {doc_id}")
        except Exception as e:
            logging.error(f"Database save failed: {e}")

        # ── Return the result to the user (now includes the id) ────────────
        response_data = {
            "id": doc_id,
            "analysis": document["analysis"],
            "metadata": document["metadata"]
        }

        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            mimetype="application/json",
            status_code=200
        )

    else:
        # No text provided — return error (same as before)
        instructions = {
            "error": "No text provided",
            "howToUse": {
                "option1": "Add ?text=YourText to the URL",
                "option2": "Send a POST request with JSON body: {\"text\": \"Your text here\"}"
            }
        }
        return func.HttpResponse(
            json.dumps(instructions, indent=2),
            mimetype="application/json",
            status_code=400
        )


# =============================================================================
# ENDPOINT 2: GetAnalysisHistory  →  /api/GetAnalysisHistory
# BRAND NEW — reads past results from the database
# =============================================================================
@app.route(route="GetAnalysisHistory", methods=["GET"])
def GetAnalysisHistory(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('GetAnalysisHistory API was called!')

    # ── Get the optional "limit" parameter ─────────────────────────────────
    # Example: /api/GetAnalysisHistory?limit=5 returns only 5 results
    # If no limit is given, default to 10
    limit = req.params.get('limit', '10')
    try:
        limit = int(limit)            # convert "10" string to 10 number
        limit = max(1, min(limit, 100))  # keep it between 1 and 100
    except ValueError:
        limit = 10

    # ── Read from Cosmos DB ─────────────────────────────────────────────────
    try:
        container = get_container()

        # This is a database query — like asking "give me the last X results"
        # ORDER BY analyzedAt DESC = newest first
        # OFFSET 0 LIMIT {limit} = start from beginning, take only {limit} items
        query = (
            f"SELECT c.id, c.analysis, c.metadata "
            f"FROM c "
            f"ORDER BY c.metadata.analyzedAt DESC "
            f"OFFSET 0 LIMIT {limit}"
        )

        # execute the query and convert results to a list
        items = list(container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        response_data = {
            "count": len(items),
            "results": items
        }

        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Failed to get history: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Failed to retrieve history", "details": str(e)}),
            mimetype="application/json",
            status_code=500
        )



# ## PHASE 3: Test Locally

# ### Step 8 — Run and Test

# 1. Press **F1** → type **Azurite: Start** → press Enter
# 2. Press **F5** to start your function
# 3. Open your browser and go to:
# ```
# http://localhost:7071/api/TextAnalyzer?text=Hello world this is a test sentence.
# ```
# You should see a response that includes an `"id"` field — that means it saved to the database ✅

# 4. Now test the history endpoint:
# ```
# http://localhost:7071/api/GetAnalysisHistory
# ```
# You should see your saved result come back ✅

# 5. Run the analyzer 2-3 more times with different text, then test:
# ```
# http://localhost:7071/api/GetAnalysisHistory?limit=2