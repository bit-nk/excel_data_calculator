from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPermissions(BaseModel):
    view_all_bus: bool = False
    approve_reports: bool = False
    manage_rules: bool = False
    export_ledger: bool = False


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role_name: str
    business_unit_id: int | None = None
    is_active: bool
    permissions: UserPermissions

    model_config = {"from_attributes": True}
