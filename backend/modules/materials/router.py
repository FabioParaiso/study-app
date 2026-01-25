from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from modules.materials.deps import get_ai_service, get_material_service
from modules.materials.service import MaterialService, MaterialServiceError
from schemas.study import AnalyzeRequest
from dependencies import get_current_user
from models import Student

router = APIRouter()

# --- Endpoints ---
@router.get("/current-material")
def get_current_material(
    current_user: Student = Depends(get_current_user),
    material_service: MaterialService = Depends(get_material_service)
):
    data = material_service.get_current_material(current_user.id)
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
    material_service: MaterialService = Depends(get_material_service)
):
    material_service.clear_material(current_user.id)
    return {"status": "cleared"}

@router.delete("/delete-material/{material_id}")
def delete_material(
    material_id: int,
    current_user: Student = Depends(get_current_user),
    material_service: MaterialService = Depends(get_material_service)
):
    success = material_service.delete_material(current_user.id, material_id)
    if not success:
        return {"status": "error", "message": "Material not found or could not be deleted"}
    return {"status": "deleted"}

@router.get("/materials")
def list_materials(
    current_user: Student = Depends(get_current_user),
    material_service: MaterialService = Depends(get_material_service)
):
    return material_service.list_materials(current_user.id)

@router.post("/materials/{material_id}/activate")
def activate_material(
    material_id: int,
    current_user: Student = Depends(get_current_user),
    material_service: MaterialService = Depends(get_material_service)
):
    success = material_service.activate_material(current_user.id, material_id)
    if not success:
        raise HTTPException(status_code=404, detail="Material not found")
    return {"status": "activated"}

@router.post("/upload")
async def upload_file(
    current_user: Student = Depends(get_current_user),
    file: UploadFile = File(...),
    material_service: MaterialService = Depends(get_material_service)
):
    ai_service = get_ai_service()
    try:
        return await material_service.upload_material(current_user.id, file, ai_service)
    except MaterialServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        print(f"Error processing upload: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/analyze-topics")
def analyze_topics_endpoint(
    request: AnalyzeRequest,
    current_user: Student = Depends(get_current_user),
    material_service: MaterialService = Depends(get_material_service)
):
    ai_service = get_ai_service()
    try:
        return material_service.analyze_topics(current_user.id, ai_service)
    except MaterialServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
