from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from crud.SCCrud import StudentCourseCrud
from schema.course.grade.CourseTeacherGradeSchema import CourseTeacherGradeSchema
from utils.auth_token import validate_teacher_token
from utils.get_db import get_db
import traceback

grade_teacher_router = APIRouter()

@grade_teacher_router.get("/teacher")
async def _(body: CourseTeacherGradeSchema = Depends(), token_payload: dict = Depends(validate_teacher_token), db: Session = Depends(get_db)):
    user_id = token_payload.get("user_id")
    class_id = body.class_id 

    try:
        data = StudentCourseCrud.get_students_and_grades(db, class_id=class_id)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"status": 1, "message": f"Database Error: {e}"})

    return {
        "status": 0,
        "message": "OK",
        "data": [{
            "id": _[0],
            "name": _[1],
            "grade": _[2]
        } for _ in data]
    }

