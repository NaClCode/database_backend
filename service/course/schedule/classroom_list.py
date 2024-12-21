import traceback

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from crud.ClassroomCrud import ClassroomCrud
from utils.auth_token import validate_teacher_token
from utils.get_db import get_db

class_list_router = APIRouter()

@class_list_router.get("/classroomList")
async def _(token_payload: dict = Depends(validate_teacher_token), db: Session = Depends(get_db)):
    user_id = token_payload.get("user_id")

    try:
        classroom = ClassroomCrud.get_all_S(db)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"status": 1, "message": f"Database Error: {e}"})

    return {
        "status": 0,
        "message": "OK",
        "data": [{
            "name": _.name,
            "location": _.location,
            "capacity": _.capacity
        } for _ in classroom]
    }