"""Tests for adam_mcp_py.validates — implements §1.2."""

import pytest
from pydantic import BaseModel, Field
from adam_mcp_py import Result, Status, validates


class GreetInput(BaseModel):
    name: str = Field(min_length=1)
    formality: int = Field(ge=0, le=10)


def test_validates_passes_valid_input():
    @validates(GreetInput)
    def greet(input: GreetInput) -> Result[str]:
        return Result.ok(value=f"hello {input.name}")

    r = greet({"name": "Adam", "formality": 5})
    assert r.status == Status.OK
    assert r.value == "hello Adam"


def test_validates_rejects_missing_field():
    @validates(GreetInput)
    def greet(input: GreetInput) -> Result[str]:
        return Result.ok(value="ok")

    r = greet({"name": "Adam"})
    assert r.status == Status.FAIL
    assert "formality" in (r.hint or "") or any("formality" in d for d in r.diagnostics)


def test_validates_rejects_out_of_range():
    @validates(GreetInput)
    def greet(input: GreetInput) -> Result[str]:
        return Result.ok(value="ok")

    r = greet({"name": "Adam", "formality": 99})
    assert r.status == Status.FAIL
    assert r.hint is not None


def test_validates_accepts_input_kwarg():
    """FastMCP dispatches with `input=...` as kwarg — must work. Regression for §1.5."""

    @validates(GreetInput)
    def greet(input: GreetInput) -> Result[str]:
        return Result.ok(value=input.name)

    r = greet(input={"name": "Adam", "formality": 5})
    assert r.status == Status.OK
    assert r.value == "Adam"


def test_validates_accepts_pre_parsed_model_instance():
    """FastMCP validates from JSONSchema before dispatch and may pass the parsed model.
    Wrapper must short-circuit, not double-validate. Regression for §1.5."""

    @validates(GreetInput)
    def greet(input: GreetInput) -> Result[str]:
        return Result.ok(value=input.name)

    parsed = GreetInput(name="Adam", formality=5)
    r = greet(parsed)
    assert r.status == Status.OK
    assert r.value == "Adam"

    r2 = greet(input=parsed)
    assert r2.status == Status.OK
    assert r2.value == "Adam"


@pytest.mark.asyncio
async def test_validates_supports_async_tools():
    @validates(GreetInput)
    async def greet(input: GreetInput) -> Result[str]:
        return Result.ok(value=input.name)

    result = await greet({"name": "Async", "formality": 5})
    assert result.status == Status.OK
    assert result.value == "Async"
