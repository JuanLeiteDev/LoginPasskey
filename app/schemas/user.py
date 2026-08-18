from pydantic import BaseModel, EmailStr, field_validator, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr

    @field_validator("name", mode="before")
    def name_validator(value: str):
        value = " ".join(value.strip().title().split(" "))

        if any(char.isdigit() for char in value):
            raise ValueError()

        return value