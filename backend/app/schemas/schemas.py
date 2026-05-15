from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserPublic"


class LoginInput(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = Field(pattern="^(client|professional)$", default="client")


class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    avatar: str | None = None

    model_config = {"from_attributes": True}


class CategoryOut(BaseModel):
    id: int
    name: str
    icon: str
    description: str | None = None

    model_config = {"from_attributes": True}


class ProfessionalOut(BaseModel):
    id: int
    user_id: int
    category_id: int
    title: str
    description: str
    city: str
    state: str
    price_from: float
    rating: float
    reviews_count: int
    whatsapp: str | None = None
    is_featured: bool
    image: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    user: UserPublic
    category: CategoryOut

    model_config = {"from_attributes": True}


class ProfessionalCreate(BaseModel):
    category_id: int
    title: str
    description: str
    city: str
    state: str = Field(min_length=2, max_length=2)
    price_from: float = 0
    whatsapp: str | None = None
    image: str | None = None


class ProfessionalUpdate(BaseModel):
    category_id: int | None = None
    title: str | None = None
    description: str | None = None
    city: str | None = None
    state: str | None = Field(default=None, min_length=2, max_length=2)
    price_from: float | None = None
    whatsapp: str | None = None
    image: str | None = None


class ReviewOut(BaseModel):
    id: int
    professional_id: int
    client_name: str
    rating: int
    comment: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    professional_id: int
    client_name: str
    rating: int = Field(ge=1, le=5)
    comment: str


class RequestCreate(BaseModel):
    category_id: int
    professional_id: int | None = None
    title: str
    description: str
    location: str
    budget: float | None = None


class RequestOut(BaseModel):
    id: int
    client_id: int
    professional_id: int | None = None
    category_id: int
    title: str
    description: str
    location: str
    status: str
    budget: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    request_id: int
    content: str


class MessageOut(BaseModel):
    id: int
    request_id: int
    sender_id: int
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
