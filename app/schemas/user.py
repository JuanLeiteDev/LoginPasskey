from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    name: str
    email: EmailStr

    @field_validator("name", mode="before")
    def name_validator(value: str):
        value = " ".join(value.strip().title().split(" "))

        if any(char.isdigit() for char in value):
            raise ValueError()

        return value