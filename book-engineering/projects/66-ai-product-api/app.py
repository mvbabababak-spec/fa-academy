"""Synthetic FastAPI contract demo for Volume 5, Chapter 5 / global Chapter 66."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parent
FIXTURE = json.loads((ROOT / "synthetic_fixture.json").read_text(encoding="utf-8"))
RECORDS = {record["id"]: record for record in FIXTURE["records"]}


class Problem(BaseModel):
    """Small RFC 9457-style error representation for this teaching API."""

    type: str
    title: str
    status: int
    detail: str


class CatalogItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9-]+$", description="Stable identifier for this synthetic source.")
    title: str = Field(min_length=1, max_length=120)
    url: str = Field(description="Reserved example.invalid URL; it is not a live source.")


class CatalogResponse(BaseModel):
    contract_version: Literal["1.0"] = "1.0"
    items: list[CatalogItem]
    next_cursor: str | None = None


class AssistRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=300, description="Synthetic demo input; do not send personal data.")
    locale: Literal["fa", "en"] = "fa"


class SourceRef(BaseModel):
    id: str
    title: str


class AssistResponse(BaseModel):
    contract_version: Literal["1.0"] = "1.0"
    request_id: str
    status: Literal["completed"]
    answer: str
    sources: list[SourceRef]


PROBLEM_SCHEMA = Problem.model_json_schema()
PROBLEM_404 = {
    "description": "The requested synthetic catalog item does not exist.",
    "content": {"application/problem+json": {"schema": PROBLEM_SCHEMA}},
}
PROBLEM_422 = {
    "description": "The request does not satisfy the published input contract.",
    "content": {"application/problem+json": {"schema": PROBLEM_SCHEMA}},
}

app = FastAPI(
    title="CampusGuide synthetic product API",
    description="A deterministic, fixture-backed teaching example; it does not call an AI model.",
    version="1.0.0",
)


def problem_response(status: int, title: str, detail: str, slug: str) -> JSONResponse:
    body = {
        "type": f"https://example.invalid/problems/{slug}",
        "title": title,
        "status": status,
        "detail": detail,
    }
    return JSONResponse(status_code=status, content=body, media_type="application/problem+json")


@app.exception_handler(RequestValidationError)
async def request_validation_problem(_request: Request, _exc: RequestValidationError) -> JSONResponse:
    # The response intentionally does not echo rejected values or internal validator details.
    return problem_response(
        422,
        "درخواست با قرارداد سازگار نیست",
        "ساختار یا مقدار یکی از فیلدهای ورودی پذیرفته نشد.",
        "invalid-request",
    )


@app.get("/v1/catalog", response_model=CatalogResponse, operation_id="listCatalog")
def list_catalog(limit: int = Query(default=10, ge=1, le=10, description="Maximum items in this synthetic fixture.")) -> CatalogResponse:
    records = [CatalogItem.model_validate({key: row[key] for key in ("id", "title", "url")}) for row in FIXTURE["records"][:limit]]
    return CatalogResponse(items=records, next_cursor=None)


@app.get(
    "/v1/catalog/items/{item_id}",
    response_model=CatalogItem,
    responses={404: PROBLEM_404},
    operation_id="getCatalogItem",
)
def get_catalog_item(item_id: str) -> CatalogItem | JSONResponse:
    record = RECORDS.get(item_id)
    if record is None:
        return problem_response(404, "منبع پیدا نشد", "شناسه در fixture ساختگی وجود ندارد.", "not-found")
    return CatalogItem.model_validate({key: record[key] for key in ("id", "title", "url")})


@app.post(
    "/v1/assist",
    response_model=AssistResponse,
    responses={422: PROBLEM_422},
    operation_id="createAssistResponse",
)
def create_assist_response(payload: AssistRequest) -> AssistResponse | JSONResponse:
    question = payload.question.strip()
    if not question:
        return problem_response(
            422,
            "پرسش خالی است",
            "یک پرسش کوتاه و غیرشخصی وارد کنید.",
            "empty-question",
        )

    record = FIXTURE["records"][0]
    answer = record["answer_fa"] if payload.locale == "fa" else record["answer_en"]
    return AssistResponse(
        request_id="req-demo-001",
        status="completed",
        answer=answer,
        sources=[SourceRef(id=record["id"], title=record["title"])],
    )


@app.get("/demo", include_in_schema=False)
def demo() -> FileResponse:
    return FileResponse(ROOT / "demo.html", media_type="text/html; charset=utf-8")
