"""Tests for adam_mcp_py.validates — implements §1.2."""
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
