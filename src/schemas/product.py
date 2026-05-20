from pydantic import BaseModel, ConfigDict, Field, field_validator


def _strip_required(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} no puede estar vacio")
    return normalized


def normalize_sku(value: str) -> str:
    return _strip_required(value, "sku").upper()


class ProductCreate(BaseModel):
    nombre: str = Field(..., min_length=1)
    sku: str = Field(..., min_length=1)
    categoria: str = Field(..., min_length=1)
    stock_inicial: int = Field(default=0, ge=0)
    stock_minimo: int = Field(default=0, ge=0)
    unidad: str = Field(default="unidades", min_length=1)

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str) -> str:
        return _strip_required(value, "nombre")

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value: str) -> str:
        return normalize_sku(value)

    @field_validator("categoria")
    @classmethod
    def validate_categoria(cls, value: str) -> str:
        return _strip_required(value, "categoria")

    @field_validator("unidad")
    @classmethod
    def validate_unidad(cls, value: str) -> str:
        return _strip_required(value, "unidad")


class ProductResponse(BaseModel):
    id: int
    nombre: str
    sku: str
    categoria: str
    stock_actual: int
    stock_minimo: int
    unidad: str
    estado: str

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1)
    categoria: str | None = Field(default=None, min_length=1)
    stock_minimo: int | None = Field(default=None, ge=0)
    unidad: str | None = Field(default=None, min_length=1)

    model_config = ConfigDict(extra="forbid")

    @field_validator("nombre")
    @classmethod
    def validate_nombre(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _strip_required(value, "nombre")

    @field_validator("categoria")
    @classmethod
    def validate_categoria(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _strip_required(value, "categoria")

    @field_validator("unidad")
    @classmethod
    def validate_unidad(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _strip_required(value, "unidad")
