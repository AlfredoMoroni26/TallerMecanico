from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.exceptions import DomainError
from app.db.session import get_db
from app.modules.identity.dependencies import get_user_agent
from app.modules.identity.schemas.auth import LoginRequest, PasswordResetConfirm, PasswordResetRequest, RefreshRequest, TokenPair
from app.modules.identity.schemas.user import UserCreate, UserRead
from app.modules.identity.services import identity_service as service

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Registro público: siempre crea clientes, nunca permite elevar privilegios."""
    return service.create_user(db, data)


@router.post("/login", response_model=TokenPair)
def login(data: LoginRequest, db: Session = Depends(get_db), user_agent: str | None = Depends(get_user_agent)):
    return service.authenticate(db, data.login, data.password, user_agent)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, db: Session = Depends(get_db), user_agent: str | None = Depends(get_user_agent)):
    return service.refresh_tokens(db, data.refresh_token, user_agent)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(data: RefreshRequest, db: Session = Depends(get_db)):
    service.revoke_session(db, data.refresh_token)


@router.post("/password-reset/request", status_code=status.HTTP_202_ACCEPTED)
def password_reset_request(data: PasswordResetRequest, db: Session = Depends(get_db)):
    token = service.request_reset(db, data.email)
    # Conectar aquí un proveedor de correo. Nunca se expone el token ni existencia de cuenta.
    # En desarrollo, imprimirlo sólo con logging seguro y nunca en la respuesta HTTP.
    _ = token
    return {"message": "Si el correo existe, recibirás instrucciones para recuperar tu contraseña."}


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
def password_reset_confirm(data: PasswordResetConfirm, db: Session = Depends(get_db)):
    # Reutiliza la política de contraseña validada en UserCreate.
    UserCreate(username="temporary_user", email="validation@example.com", password=data.new_password)
    service.reset_password(db, data.token, data.new_password)
