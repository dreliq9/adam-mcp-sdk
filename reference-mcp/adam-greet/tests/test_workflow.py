"""Tests for adam_greet morning_briefing workflow + tool wrapper."""

from adam_mcp_py import Status
from adam_greet.workflows import MorningBriefingWorkflow
from adam_greet.mcp.workflow_tools import morning_briefing


def test_workflow_run_directly():
    wf = MorningBriefingWorkflow()
    r = wf.run(name="Adam")
    assert r.status == Status.OK
    assert "Adam" in r.value
    assert r.metrics["steps"] == 4


def test_morning_briefing_tool_ok():
    r = morning_briefing({"name": "Adam"})
    assert r.status == Status.OK
    assert "Adam" in r.value


def test_morning_briefing_validates_empty_name():
    r = morning_briefing({"name": ""})
    assert r.status == Status.FAIL
