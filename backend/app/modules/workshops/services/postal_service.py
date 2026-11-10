import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.core.config import get_settings
from app.core.exceptions import DomainError


def _request(endpoint: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    settings = get_settings()
    if not settings.postal_api_key:
        raise DomainError("La consulta postal no está configurada. Configura POSTAL_API_KEY en el servidor.", 503)
    query = f"?{urlencode(params)}" if params else ""
    request = Request(
        f"{settings.postal_api_base_url.rstrip('/')}/{endpoint.lstrip('/')}{query}",
        headers={"X-API-Key": settings.postal_api_key, "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=8) as response:  # noqa: S310 - URL administrada por configuración.
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        if error.code == 404:
            raise DomainError("No se encontró información para esa ubicación.", 404) from error
        raise DomainError("No fue posible consultar la API de códigos postales.", 503) from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise DomainError("No fue posible consultar la API de códigos postales.", 503) from error
    if not payload.get("success"):
        message = payload.get("error", {}).get("message") or "No se encontró información para esa ubicación."
        raise DomainError(message, 404)
    return payload["data"]


def lookup_postal_code(postal_code: str) -> dict[str, Any]:
    data = _request(f"codigo-postal/{postal_code}")
    return {
        "postal_code": data["codigo_postal"],
        "state": data["estado"],
        "municipality": data["municipio"],
        "neighborhoods": [item["colonia"] for item in data.get("colonias", [])],
    }


def list_states() -> list[dict[str, str]]:
    data = _request("estados")
    return [{"id": str(item["id"]), "name": item["nombre"]} for item in data.get("estados", [])]


def list_municipalities(state_id: str) -> list[dict[str, str]]:
    data = _request(f"estados/{state_id}/municipios")
    return [{"id": str(item["id"]), "name": item["nombre"]} for item in data.get("municipios", [])]


def search_settlements(state: str, municipality: str, query: str) -> list[dict[str, str]]:
    if len(query.strip()) < 3:
        raise DomainError("Escribe al menos 3 caracteres de la colonia.", 422)
    data = _request("buscar", {"q": query.strip()})
    state_key = state.casefold()
    municipality_key = municipality.casefold()
    return [
        {"name": item["colonia"], "postal_code": item["codigo_postal"]}
        for item in data.get("results", [])
        if item.get("estado", "").casefold() == state_key and item.get("municipio", "").casefold() == municipality_key
    ]
