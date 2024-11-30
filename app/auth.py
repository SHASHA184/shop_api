from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from app.services.user_service import UserService
from app.database.database import get_db
from app.utils import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    """Retrieve the current authenticated user."""
    payload = decode_access_token(token)
    id: str = payload.get("sub")
    if not id:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    service = UserService(db)
    user = await service.get_one(int(id))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
