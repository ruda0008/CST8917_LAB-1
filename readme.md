# Text Analyzer Azure Function

An Azure Function that analyzes text and stores results in Azure Cosmos DB.

## Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/TextAnalyzer` | GET/POST | Analyzes text and saves result to database |
| `/api/GetAnalysisHistory` | GET | Retrieves past analysis results |

## How to Run Locally

### Prerequisites
- Python 3.12
- VS Code with Azure Functions extension
- Azure Functions Core Tools
- Azurite extension (local storage emulator)

### Setup Steps

1. Clone the repository
2. Open the folder in VS Code
3. Create a file called `local.settings.json` in the project root with the following:
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "COSMOS_CONNECTION_STRING": "your-cosmos-db-connection-string-here"
  }
}
```

4. Replace `your-cosmos-db-connection-string-here` with your Cosmos DB 
   connection string from Azure Portal → your Cosmos DB account → Keys → 
   Primary Connection String

5. Install dependencies:
```bash
pip install -r requirements.txt
```

6. Start Azurite: Press `F1` → type `Azurite: Start` → press Enter

7. Run the function: Press `F5` or run in terminal:
```bash
func start
```

### Test Locally

**Analyze text:**
```
http://localhost:7071/api/TextAnalyzer?text=Hello world this is a test
```

**Get history:**
```
http://localhost:7071/api/GetAnalysisHistory
```

**Get history with limit:**
```
http://localhost:7071/api/GetAnalysisHistory?limit=5
```

## Environment Variables

| Variable | Description | Where to get it |
|---|---|---|
| `COSMOS_CONNECTION_STRING` | Cosmos DB connection string | Azure Portal → Cosmos DB account → Keys |

## Important Notes
- Never commit `local.settings.json` to GitHub — it contains secrets
- The `local.settings.json` file is already in `.gitignore` by default