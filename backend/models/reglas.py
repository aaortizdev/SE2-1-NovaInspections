"""Formato de las reglas regulatorias (una lista de reglas por mercado en backend/reglas/*.json)."""

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Severidad = Literal["critico", "advertencia"]
EstadoRegla = Literal["pendiente_revision", "verificada"]

# PAIS-NORMA-TEMA-NN, por ejemplo US-FDA-NET-01 o EC-RTE022-SEM-01.
PATRON_ID = re.compile(r"^(US|EC)-[A-Z0-9]{2,10}-[A-Z]{3}-\d{2}$")

PREFIJO_POR_MERCADO = {"estados_unidos": "US", "ecuador": "EC"}

# Mercados con archivo de reglas en backend/reglas/. Estados Unidos quedó como "Próximamente":
# para activarlo, agregar "estados_unidos" aquí y crear reglas/estados_unidos.json.
MERCADOS_ACTIVOS = ("ecuador",)


class ReglaEtiquetado(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    norma: str = Field(min_length=3)
    referencia: str = Field(min_length=3)
    titulo: str = Field(min_length=5)
    requisito: str = Field(min_length=20)
    como_verificar: str = Field(min_length=20)
    cumple_si: str = Field(min_length=10)
    incumple_si: str = Field(min_length=10)
    severidad_si_incumple: Severidad
    aplica_si: str = Field(min_length=5)
    cita_fuente: str = Field(min_length=5)
    fuente_url: str
    estado: EstadoRegla = "pendiente_revision"
    verificada_por: str | None = None

    @field_validator("id")
    @classmethod
    def _id_valido(cls, v: str) -> str:
        if not PATRON_ID.match(v):
            raise ValueError("el id debe tener el formato PAIS-NORMA-TEMA-NN (p. ej. US-FDA-NET-01)")
        return v

    @field_validator("fuente_url")
    @classmethod
    def _url_valida(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("fuente_url debe empezar con https://")
        return v

    @property
    def referencia_normativa(self) -> str:
        """Texto que el backend copia al hallazgo (la IA no lo escribe)."""
        return f"{self.norma}, {self.referencia}"
