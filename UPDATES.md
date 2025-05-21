# Medical AI Assistant System Updates

## Latest Improvements (2025-05-21)

### Bug Fixes

1. **Fixed JSON Serialization Error**: Solved the issue with conversation saving that was causing "Object of type datetime is not JSON serializable" errors.

2. **Improved JSON Parsing for LLM Responses**: Enhanced error handling in the specialty classification to extract valid JSON from LLM responses, handle malformed output, and provide better fallbacks when parsing fails.

3. **Corrupt Conversation File Handling**: Added robust handling of corrupted conversation files by renaming them with a `.corrupted.json` extension instead of crashing on load.

### New Features

1. **Added Internal Medicine Agent**: Created a dedicated specialist agent for Internal Medicine instead of using the Cardiology agent as a fallback.

2. **Better Specialty Fallbacks**: Updated the agent factory to use the Internal Medicine agent as the default fallback for missing specialties.

### Configuration

Create a `.env` file in the project root with the following settings:

```
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here

# LLM Configuration
LLM_PROVIDER=openai  # 'openai' or 'groq'
LLM_MODEL=gpt-4o  # or mixtral-8x7b for GROQ

# Flask Configuration
FLASK_SECRET_KEY=your_secret_key_for_production
FLASK_DEBUG=True  # Set to False in production

# LangGraph Configuration
USE_LANGGRAPH=True
```

## Running the Application

1. Ensure you have set up your API keys in the `.env` file
2. Activate the virtual environment:
   ```
   .\langchain-bootcamp-venv\Scripts\activate  # Windows
   source langchain-bootcamp-venv/bin/activate  # Linux/Mac
   ```
3. Run the application:
   ```
   python -m src.app
   ```
4. Open a browser and navigate to:
   ```
   http://localhost:5000
   ```

## Known Issues

- Only three specialties (Cardiology, Neurology, and Internal Medicine) have dedicated agents. Other specialties are handled by the Internal Medicine agent as a fallback.
- Multi-specialty consensus responses may include more than one perspective on symptoms, which can occasionally be contradictory. 