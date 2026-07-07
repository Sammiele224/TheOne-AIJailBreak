from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Khởi tạo biến "app" mà Uvicorn đang tìm kiếm:
app = FastAPI(
    title="NeuroCorp Heist API",
    description="Multi-Model AI Red Teaming & Prompt Injection Backend",
    version="1.0.0",
)

# Cấu hình CORS để React Frontend (localhost:5173) có thể kết nối:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint kiểm tra sức khỏe hệ thống:
@app.get("/health", tags=["System Diagnostics"])
async def health_check():
    return {
        "status": "ONLINE",
        "system": "NeuroCorp Security Gateway",
        "message": "Backend engine is primed and ready for prompt injection."
    }