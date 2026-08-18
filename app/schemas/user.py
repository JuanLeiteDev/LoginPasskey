from pydantic import BaseModel, field_validator, Field

class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[a-z][a-z0-9._]{2,29}$"
    )

    @field_validator("username", mode="before")
    def name_validator(value: str):
        value = "".join(value.strip().lower().split(" "))

        return value