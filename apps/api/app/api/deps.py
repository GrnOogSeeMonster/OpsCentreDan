from typing import Annotated

from fastapi import Depends

from app.core.security import get_current_user, role_guard
from app.models.entities import RoleEnum, User

CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(role_guard(RoleEnum.ADMIN))]
EngineerOrAdminUser = Annotated[
    User,
    Depends(role_guard(RoleEnum.ADMIN, RoleEnum.ENGINEER)),
]
ViewerOrAboveUser = Annotated[
    User,
    Depends(role_guard(RoleEnum.ADMIN, RoleEnum.ENGINEER, RoleEnum.VIEWER)),
]
