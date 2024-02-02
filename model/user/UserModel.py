from enum import Enum, auto
import re
from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field, constr, validator

class AccountStatus(Enum):
    Active=auto()
    Freeze=auto
    Inactive=auto()
class Role(Enum):  
    SuperAdmin=auto()
    Admin = auto()
    User=auto()

class Users(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    password: str
    phone_number: Optional[constr(min_length=11, max_length=14)] = None
    address: Optional[str] = ""
    t_shirt_size: Optional[str] = ""
    bio:Optional[str]=''
    facebook_id:Optional[str]=''
    codeforces_id:Optional[str]=''
    status:str=AccountStatus.Active.name
    isEmailVerified:bool=False
    isActivated:bool=True
    role:str

    @validator("phone_number", pre=True, always=True)
    def validate_phone_number(cls, value):
        if value is not None and not re.match(r"^[+].+[0-9]$", value):
            raise ValueError("Invalid phone number format")
        return value
