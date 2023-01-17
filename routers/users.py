from fastapi import FastAPI,APIRouter,Depends,Response,Request,Form,status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from passlib.context import CryptContext
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .auth import get_current_user


templates = Jinja2Templates(directory="templates")



class Usersn(BaseModel):
    username:str
    password:str
    newPassword:str



def get_db():
    try:
        db= SessionLocal()
        yield db
    finally:
        db.close()

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404:{"description":"not found"}}
)




bcrypt_context = CryptContext(schemes=["bcrypt"],deprecated="auto")

def get_password_hash(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password, hashed_password):
    return bcrypt_context.verify(plain_password, hashed_password)

def authenticate_user(username:str, password:str,db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user:
        return False

    if not verify_password(password,user.hashed_password):
        return False
    return user







# @router.get("/resetpassword")
# def hello(password:Password,db:Session=Depends(get_db)):

#     return "hello"

@router.get("/changePassword",response_class=HTMLResponse)
async def changePasswordPage(request: Request):
    
    return templates.TemplateResponse("change-password.html", {"request":request})



@router.post("/changepassword",response_class=HTMLResponse)
async def login_for_access_token(request: Request,response:Response,username:str = Form(...),password1:str = Form(...),password2:str = Form(...),db:Session=Depends(get_db)):
    
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)



    user1 = authenticate_user(username,password1,db)
    

    if not user1:
        msg='inavalid user name/ password'
        return templates.TemplateResponse("change-password.html",{"request":request, "msg":msg})
    


    hash_password=get_password_hash(password2)
    user1.hashed_password=hash_password
    db.add(user1)
    db.commit()
    

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)




    
