from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
import os
from rate_limiter import limiter
from modules.materials.deps import (
    get_ai_service,
    get_upload_material_use_case,
    get_analyze_topics_use_case,
    get_get_current_material_use_case,
    get_clear_material_use_case,
    get_list_materials_use_case,
    get_activate_material_use_case,
    get_delete_material_use_case,
)
from modules.materials.errors import MaterialServiceError
from schemas.study import AnalyzeRequest
from dependencies import get_current_user, enforce_ai_quota
from models import Student
from modules.materials.ports import (
    UploadMaterialUseCasePort,
    AnalyzeTopicsUseCasePort,
    GetCurrentMaterialUseCasePort,
    ClearMaterialUseCasePort,
    ListMaterialsUseCasePort,
    ActivateMaterialUseCasePort,
    DeleteMaterialUseCasePort,
    TopicAIServicePort,
)

router = APIRouter()
AI_RATE_LIMIT = os.getenv("AI_RATE_LIMIT", "20/minute")

# --- Endpoints ---
@router.get("/current-material")
def get_current_material(
    current_user: Student = Depends(get_current_user),
    use_case: GetCurrentMaterialUseCasePort = Depends(get_get_current_material_use_case)
):
    data = use_case.execute(current_user.id)
    if data:
        return {
            "has_material": True,
            "id": data.get("id"),
            "source": data.get("source"),
            "preview": data.get("text")[:200] if data.get("text") else "",
            "topics": data.get("topics", []),
            "total_xp": data.get("total_xp", 0),
            "high_score": data.get("high_score", 0)
        }
    return {"has_material": False}

@router.post("/clear-material")
def clear_material(
    current_user: Student = Depends(get_current_user),
    use_case: ClearMaterialUseCasePort = Depends(get_clear_material_use_case)
):
    use_case.execute(current_user.id)
    return {"status": "cleared"}

@router.delete("/delete-material/{material_id}")
def delete_material(
    material_id: int,
    current_user: Student = Depends(get_current_user),
    use_case: DeleteMaterialUseCasePort = Depends(get_delete_material_use_case)
):
    success = use_case.execute(current_user.id, material_id)
    if not success:
        return {"status": "error", "message": "Material not found or could not be deleted"}
    return {"status": "deleted"}

@router.get("/materials")
def list_materials(
    current_user: Student = Depends(get_current_user),
    use_case: ListMaterialsUseCasePort = Depends(get_list_materials_use_case)
):
    return use_case.execute(current_user.id)

@router.post("/materials/{material_id}/activate")
def activate_material(
    material_id: int,
    current_user: Student = Depends(get_current_user),
    use_case: ActivateMaterialUseCasePort = Depends(get_activate_material_use_case)
):
    success = use_case.execute(current_user.id, material_id)
    if not success:
        raise HTTPException(status_code=404, detail="Material not found. Active material unchanged.")
    return {"status": "activated"}

@router.post("/upload")
@limiter.limit(AI_RATE_LIMIT)
async def upload_file(
    request: Request,
    current_user: Student = Depends(get_current_user),
    _quota: None = Depends(enforce_ai_quota),
    file: UploadFile = File(...),
    use_case: UploadMaterialUseCasePort = Depends(get_upload_material_use_case),
    ai_service: TopicAIServicePort = Depends(get_ai_service)
):
    try:
        content = await file.read()
        return await use_case.execute(
            user_id=current_user.id,
            file_content=content,
            filename=file.filename,
            file_type=file.content_type,
            ai_service=ai_service
        )
    except MaterialServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        print(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/analyze-topics")
@limiter.limit(AI_RATE_LIMIT)
def analyze_topics_endpoint(
    request: Request,
    payload: AnalyzeRequest,
    current_user: Student = Depends(get_current_user),
    _quota: None = Depends(enforce_ai_quota),
    use_case: AnalyzeTopicsUseCasePort = Depends(get_analyze_topics_use_case),
    ai_service: TopicAIServicePort = Depends(get_ai_service)
):
    try:
        return use_case.execute(current_user.id, ai_service)
    except MaterialServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
