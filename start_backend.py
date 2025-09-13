#!/usr/bin/env python3

import uvicorn

if __name__ == "__main__":
    print("Starting Literature Review Agent Backend...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("API Documentation: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
