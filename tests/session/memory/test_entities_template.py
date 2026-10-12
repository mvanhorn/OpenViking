# Copyright (c) 2026 Beijing Volcano Engine Technology Co., Ltd.
# SPDX-License-Identifier: AGPL-3.0

from pathlib import Path

import pytest
import yaml
from jinja2 import Template

from openviking.session.memory.utils.description_template import (
    render_description_template,
)


@pytest.mark.parametrize(
    "schema_path",
    [
        "openviking/prompts/templates/memory/entities.yaml",
        "openviking/prompts/templates/memory/experimental_memory/entities.yaml",
    ],
)
def test_entity_filename_is_case_insensitive(schema_path):
    schema = yaml.safe_load(Path(schema_path).read_text(encoding="utf-8"))
    template = Template(schema["filename_template"])

    lower_path = template.render(category="concept", name="smart")
    upper_path = template.render(category="CONCEPT", name="SMART")

    assert lower_path == upper_path == "concept/smart.md"
    fields = {field["name"]: field for field in schema["fields"]}
    assert fields["category"]["merge_op"] == "replace"
    assert fields["name"]["merge_op"] == "replace"


@pytest.mark.parametrize(
    "schema_path",
    [
        "openviking/prompts/templates/memory/entities.yaml",
        "openviking/prompts/templates/memory/experimental_memory/entities.yaml",
    ],
)
def test_entity_filename_keeps_existing_non_ascii_category(schema_path):
    schema = yaml.safe_load(Path(schema_path).read_text(encoding="utf-8"))
    template = Template(schema["filename_template"])

    path = template.render(category="人物", name="张三")

    assert path == "人物/张三.md"


@pytest.mark.parametrize(
    "schema_path",
    [
        "openviking/prompts/templates/memory/entities.yaml",
        "openviking/prompts/templates/memory/experimental_memory/entities.yaml",
    ],
)
def test_category_guidance_is_stable_across_session_languages(schema_path):
    schema = yaml.safe_load(Path(schema_path).read_text(encoding="utf-8"))
    fields = {field["name"]: field for field in schema["fields"]}
    contexts = (
        {"language": "en"},
        {"language": "zh"},
        {"language": "es"},
        {},
    )

    rendered = [
        render_description_template(fields["category"]["description"], context)
        for context in contexts
    ]

    assert all(rendered)
    assert len(set(rendered)) == 1
    guidance = rendered[0]
    assert "Stable directory identifier" in guidance
    assert "reuse that identifier exactly" in guidance
    assert "non-ASCII" in guidance
    assert "differs from the session language" in guidance
    assert "English conversation reuses an existing Chinese identifier" in guidance
    assert "Chinese conversation reuses an existing English identifier" in guidance
    assert "Do not translate" in guidance
    assert "synonym" in guidance
    assert "preserve its existing category" in guidance
    assert "third variant" in guidance
    assert "self or peer" in guidance
    assert "does not merge distinct entities" in guidance
    assert "no suitable existing category exists" in guidance
    assert "English lowercase" in guidance
    assert "underscores" in guidance
    assert "at most three words" in guidance
    assert "takes precedence over this fallback" in guidance
