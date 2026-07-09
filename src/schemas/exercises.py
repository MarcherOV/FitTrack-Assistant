from pydantic import BaseModel, ConfigDict

class BaseORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class ExercisePOST(BaseModel):
    name: str
    category_id: int
    type_id: int

class ExerciseGET(ExercisePOST, BaseORMModel):
    id: int

class ExerciseUPDATE(BaseModel):
    name: str | None = None
    category_id: int | None = None
    type_id: int | None = None

class CategoryPOST(BaseModel):
    name: str

class CategoryGET(CategoryPOST, BaseORMModel):
    id: int

class CategoryUPDATE(BaseModel):
    name: str | None = None

class TypePOST(BaseModel):
    name: str

class TypeGET(TypePOST, BaseORMModel):
    id: int

class TypeUPDATE(BaseModel):
    name: str | None = None