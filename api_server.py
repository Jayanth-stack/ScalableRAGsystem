"""Run the Code Assistant API server."""

import uvicorn
from code_assistant.api import app

if __name__ == "__main__":
    uvicorn.run(
        "code_assistant.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 