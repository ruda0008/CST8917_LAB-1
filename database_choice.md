# Database Choice: Azure Cosmos DB for NoSQL

## My Choice
Azure Cosmos DB (NoSQL)

## Justification
Azure Cosmos DB was selected because the Text Analyzer produces structured JSON
results, which Cosmos DB stores natively as documents without needing any schema.
The serverless tier makes it cost effective. It aligns with
serverless principles  no infrastructure to manage, automatic scaling and the
azure cosmos Python SDK integrates cleanly with Azure Functions. The SQL-like
query syntax makes retrieving ordered history straightforward.

## Alternatives Considered
- **Azure Table Storage**: Simpler but limited query capabilities and awkward
  for nested JSON structures like our analysis results.
- **Azure SQL Database**: Requires schema design upfront, overkill for
  flexible JSON documents with no relational data.
- **Azure Blob Storage**: Can store JSON files but has no querying ability   retrieving history would require reading every file individually.
