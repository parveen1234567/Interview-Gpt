from fastapi import HTTPException, Request, status


def get_authenticated_user_id(request: Request) -> int:
    user = request.session.get("user")
    user_id = user.get("id") if isinstance(user, dict) else None

    if type(user_id) is not int:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in to continue.",
        )

    return user_id
