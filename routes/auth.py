import hashlib
import logging
import re
import secrets
import smtplib
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError

from config.database import SessionLocal
from models.interview_result import InterviewResult
from models.interview_session import InterviewSession
from models.password_reset_token import PasswordResetToken
from models.user import User
from services.auth import hash_password, verify_password
from services.email_service import send_password_reset_email


logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="templates")

PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_BYTES = 72
RESET_TOKEN_LIFETIME = timedelta(minutes=30)
RESET_REQUEST_LIMIT = 3
RESET_REQUEST_WINDOW = timedelta(hours=1)


def _utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _render_auth_page(
    request,
    template,
    message=None,
    error=None,
    status_code=200,
    next_path="/dashboard",
):
    return templates.TemplateResponse(
        request=request,
        name=template,
        context={
            "request": request,
            "message": message,
            "error": error,
            "next_path": _safe_next_path(next_path),
        },
        status_code=status_code,
    )


def _password_error(password):
    if len(password) < PASSWORD_MIN_LENGTH:
        return f"Password must be at least {PASSWORD_MIN_LENGTH} characters."
    if len(password.encode("utf-8")) > PASSWORD_MAX_BYTES:
        return f"Password must be no more than {PASSWORD_MAX_BYTES} UTF-8 bytes."
    return None


def _valid_email(email):
    return (
        len(email) <= 100
        and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) is not None
    )


def _safe_next_path(next_path):
    return "/upload" if next_path == "/upload" else "/dashboard"


@router.get("/register")
def register_page(request: Request, next: str = "/dashboard"):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "request": request,
            "error": None,
            "next_path": _safe_next_path(next),
        },
    )


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/dashboard"),
):
    name = name.strip()
    email = email.strip().lower()
    password_error = _password_error(password)

    if not name or len(name) > 100:
        return _render_auth_page(
            request,
            "register.html",
            error="Enter a name no longer than 100 characters.",
            status_code=400,
            next_path=next,
        )
    if not _valid_email(email):
        return _render_auth_page(
            request,
            "register.html",
            error="Enter a valid email address.",
            status_code=400,
            next_path=next,
        )
    if password_error:
        return _render_auth_page(
            request,
            "register.html",
            error=password_error,
            status_code=400,
            next_path=next,
        )

    db = SessionLocal()
    try:
        if db.query(User.id).filter(User.email == email).first():
            return _render_auth_page(
                request,
                "register.html",
                error="An account with that email already exists.",
                status_code=409,
                next_path=next,
            )

        db.add(User(name=name, email=email, password=hash_password(password)))
        db.commit()
    except IntegrityError:
        db.rollback()
        return _render_auth_page(
            request,
            "register.html",
            error="An account with that email already exists.",
            status_code=409,
            next_path=next,
        )
    finally:
        db.close()

    destination = _safe_next_path(next)
    login_url = "/login?registered=1"
    if destination == "/upload":
        login_url += "&next=%2Fupload"
    return RedirectResponse(
        url=login_url,
        status_code=303,
    )


@router.get("/login")
def login_page(
    request: Request,
    registered: int = 0,
    reset: int = 0,
    account_deleted: int = 0,
    next: str = "/dashboard",
):
    message = None
    if account_deleted:
        message = (
            "Your login was deleted. Your interview records were retained "
            "without an account link."
        )
    elif registered:
        message = "Registration successful. You can now log in."
    elif reset:
        message = "Password reset successfully. You can now log in."
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "message": message,
            "error": None,
            "next_path": _safe_next_path(next),
        },
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form("/dashboard"),
):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email.strip().lower()).first()
        if user is None or not verify_password(password, user.password):
            return _render_auth_page(
                request,
                "login.html",
                error="Invalid email or password.",
                status_code=401,
                next_path=next,
            )

        request.session.clear()
        request.session["user"] = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
        }
    finally:
        db.close()

    return RedirectResponse(
        url=_safe_next_path(next),
        status_code=303,
    )


@router.get("/profile")
def profile_page(request: Request):
    user_data = request.session.get("user")
    user_id = user_data.get("id") if isinstance(user_data, dict) else None
    if type(user_id) is not int:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            request.session.clear()
            return RedirectResponse(url="/login", status_code=303)

        profile = {"name": user.name, "email": user.email}
    finally:
        db.close()

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"request": request, "profile": profile, "error": None},
    )


@router.post("/profile/delete")
def delete_account(
    request: Request,
    password: str = Form(...),
    confirmation: str = Form(...),
):
    user_data = request.session.get("user")
    user_id = user_data.get("id") if isinstance(user_data, dict) else None
    if type(user_id) is not int:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            request.session.clear()
            return RedirectResponse(url="/login", status_code=303)

        if not verify_password(password, user.password):
            return templates.TemplateResponse(
                request=request,
                name="profile.html",
                context={
                    "request": request,
                    "profile": {"name": user.name, "email": user.email},
                    "error": "Password is incorrect. Your account was not deleted.",
                },
                status_code=400,
            )

        if confirmation.strip().casefold() != "delete my account":
            return templates.TemplateResponse(
                request=request,
                name="profile.html",
                context={
                    "request": request,
                    "profile": {"name": user.name, "email": user.email},
                    "error": "Enter DELETE MY ACCOUNT to confirm. Capitalization and surrounding spaces do not matter.",
                    "confirmation": confirmation,
                },
                status_code=400,
            )

        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id
        ).delete(synchronize_session=False)
        db.query(InterviewSession).filter(
            InterviewSession.user_id == user_id
        ).update({"user_id": None}, synchronize_session=False)
        db.query(InterviewResult).filter(
            InterviewResult.user_id == user_id
        ).update({"user_id": None}, synchronize_session=False)
        db.delete(user)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    request.session.clear()
    return RedirectResponse(url="/login?account_deleted=1", status_code=303)


@router.get("/forgot-password")
def forgot_password_page(request: Request, next: str = "/dashboard"):
    return _render_auth_page(
        request,
        "forgot_password.html",
        next_path=next,
    )


@router.get("/forgot-email")
def forgot_email_page(request: Request, next: str = "/dashboard"):
    return templates.TemplateResponse(
        request=request,
        name="forgot_email.html",
        context={
            "request": request,
            "next_path": _safe_next_path(next),
        },
    )


@router.post("/forgot-password")
def request_password_reset(
    request: Request,
    email: str = Form(...),
    next: str = Form("/dashboard"),
):
    normalized_email = email.strip().lower()
    generic_message = (
        "If an account exists for that email, a password reset link will be sent."
    )
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == normalized_email).first()
        if user is None:
            return _render_auth_page(
                request,
                "forgot_password.html",
                message=generic_message,
                next_path=next,
            )

        now = _utc_now()
        recent_requests = (
            db.query(PasswordResetToken.id)
            .filter(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.created_at >= now - RESET_REQUEST_WINDOW,
            )
            .count()
        )
        if recent_requests >= RESET_REQUEST_LIMIT:
            return _render_auth_page(
                request,
                "forgot_password.html",
                message=generic_message,
                next_path=next,
            )

        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        ).update({"used_at": now}, synchronize_session=False)

        raw_token = secrets.token_urlsafe(32)
        token_record = PasswordResetToken(
            user_id=user.id,
            token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
            expires_at=now + RESET_TOKEN_LIFETIME,
            used_at=None,
            created_at=now,
        )
        db.add(token_record)
        db.commit()
        recipient = user.email
    finally:
        db.close()

    try:
        send_password_reset_email(
            recipient,
            raw_token,
            next_path=_safe_next_path(next),
        )
    except (OSError, RuntimeError, smtplib.SMTPException, ValueError):
        logger.exception("Unable to send password reset email.")

    return _render_auth_page(
        request,
        "forgot_password.html",
        message=generic_message,
        next_path=next,
    )


@router.get("/reset-password")
def reset_password_page(
    request: Request,
    token: str = "",
    next: str = "/dashboard",
):
    if not token:
        return _render_auth_page(
            request,
            "reset_password.html",
            error="This reset link is invalid or expired. Request a new one.",
            status_code=400,
            next_path=next,
        )
    return templates.TemplateResponse(
        request=request,
        name="reset_password.html",
        context={
            "request": request,
            "token": token,
            "error": None,
            "next_path": _safe_next_path(next),
        },
        headers={
            "Cache-Control": "no-store",
            "Referrer-Policy": "no-referrer",
        },
    )


@router.post("/reset-password")
def reset_password(
    request: Request,
    token: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    next: str = Form("/dashboard"),
):
    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "token": token,
                "error": "Passwords do not match.",
                "next_path": _safe_next_path(next),
            },
            status_code=400,
        )

    password_error = _password_error(password)
    if password_error:
        return templates.TemplateResponse(
            request=request,
            name="reset_password.html",
            context={
                "request": request,
                "token": token,
                "error": password_error,
                "next_path": _safe_next_path(next),
            },
            status_code=400,
        )

    now = _utc_now()
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    db = SessionLocal()
    try:
        reset_record = (
            db.query(PasswordResetToken)
            .filter(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
            )
            .with_for_update()
            .first()
        )
        if reset_record is None:
            return templates.TemplateResponse(
                request=request,
                name="reset_password.html",
                context={
                    "request": request,
                    "token": "",
                    "error": "This reset link is invalid or expired. Request a new one.",
                    "next_path": _safe_next_path(next),
                },
                status_code=400,
            )

        user = db.query(User).filter(User.id == reset_record.user_id).first()
        if user is None:
            logger.error(
                "Password reset token references missing user id %s.",
                reset_record.user_id,
            )
            return templates.TemplateResponse(
                request=request,
                name="reset_password.html",
                context={
                    "request": request,
                    "token": "",
                    "error": "This reset link is invalid or expired. Request a new one.",
                    "next_path": _safe_next_path(next),
                },
                status_code=400,
            )

        user.password = hash_password(password)
        reset_record.used_at = now
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.id != reset_record.id,
            PasswordResetToken.used_at.is_(None),
        ).update({"used_at": now}, synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    return RedirectResponse(
        url=f"/login?reset=1&next={_safe_next_path(next)}",
        status_code=303,
    )


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
