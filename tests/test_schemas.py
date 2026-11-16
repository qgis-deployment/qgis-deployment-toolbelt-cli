#! python3  # noqa: E265

"""Check the JSON schemas published in docs/schemas, and the profiles shipped with
the project against them.

The schemas are resolved locally, through their ``$id``: no network access.

Usage from the repo root folder:

.. code-block:: bash

    pytest tests/test_schemas.py
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import json
from pathlib import Path

# 3rd party
import pytest


jsonschema = pytest.importorskip("jsonschema")
referencing = pytest.importorskip("referencing")

# #############################################################################
# ########## Globals ###############
# ##################################

SCHEMAS_FOLDER = Path("docs/schemas")
PROFILE_SCHEMA_FILE = SCHEMAS_FOLDER / "profile/qgis_profile.json"
SCHEMA_FILES = sorted(SCHEMAS_FOLDER.rglob("*.json"))

GOOD_PROFILES = sorted(
    [
        *Path("examples/profiles").glob("*/profile.json"),
        *Path("tests/fixtures/profiles").glob("good_*.json"),
    ]
)
# bad fixtures rejected by the schema itself (others are bad at runtime only, like a
# qdtMinVersion higher than the running version)
BAD_PROFILES = [
    Path("tests/fixtures/profiles/bad_profile_qdt_min_version_invalid.json")
]


# #############################################################################
# ########## Helpers ###############
# ##################################


def load_json(json_path: Path) -> dict:
    """Load a JSON file."""
    return json.loads(json_path.read_text(encoding="UTF-8"))


def build_registry() -> "referencing.Registry":
    """Register every local schema under its $id, so that $ref resolve offline."""
    resources = []
    for schema_file in SCHEMA_FILES:
        schema = load_json(schema_file)
        resources.append(
            (schema["$id"], referencing.Resource.from_contents(schema)),
        )
    return referencing.Registry().with_resources(resources)


def profile_validator() -> "jsonschema.protocols.Validator":
    """Validator of profile.json files, with local resolution of references."""
    schema = load_json(PROFILE_SCHEMA_FILE)
    validator_class = jsonschema.validators.validator_for(schema)
    return validator_class(
        schema,
        registry=build_registry(),
        format_checker=validator_class.FORMAT_CHECKER,
    )


# #############################################################################
# ########## Tests #################
# ##################################


@pytest.mark.parametrize("schema_file", SCHEMA_FILES, ids=str)
def test_schema_is_valid(schema_file: Path):
    """Each schema is itself a valid JSON Schema."""
    schema = load_json(schema_file)
    jsonschema.validators.validator_for(schema).check_schema(schema)


def test_schema_ids_are_unique():
    """Each schema has its own $id, on the same host and branch as the others."""
    schema_ids = [load_json(schema_file)["$id"] for schema_file in SCHEMA_FILES]
    assert len(schema_ids) == len(set(schema_ids))

    prefix = (
        "https://raw.githubusercontent.com/qgis-deployment/"
        "qgis-deployment-toolbelt-cli/main/docs/schemas/"
    )
    for schema_file, schema_id in zip(SCHEMA_FILES, schema_ids, strict=True):
        assert schema_id == prefix + schema_file.relative_to(SCHEMAS_FOLDER).as_posix()


@pytest.mark.parametrize("profile_file", GOOD_PROFILES, ids=str)
def test_good_profiles_are_valid(profile_file: Path):
    """Profiles shipped as examples or good fixtures comply with the schema."""
    errors = sorted(
        profile_validator().iter_errors(load_json(profile_file)),
        key=lambda error: list(error.path),
    )
    assert not errors, "\n".join(
        f"{'/'.join(map(str, error.path)) or '<root>'}: {error.message}"
        for error in errors
    )


@pytest.mark.parametrize("profile_file", BAD_PROFILES, ids=str)
def test_bad_profiles_are_invalid(profile_file: Path):
    """Bad fixtures are rejected by the schema."""
    assert not profile_validator().is_valid(load_json(profile_file))


@pytest.mark.parametrize(
    ("version", "is_valid"),
    [
        ("1.2.3", True),
        ("1.2", True),
        ("10.0.12", True),
        ("1", False),
        ("1.2.3.4", False),
        ("v1.2.3", False),
        ("1.2.x", False),
    ],
)
def test_profile_version_format(version: str, is_valid: bool):
    """SemVer x.y.z is expected, x.y is accepted (read as x.y.0)."""
    profile = {
        "name": "version_format",
        "author": "QDT tests",
        "email": "qdt@example.org",
        "version": version,
        "qgisMinimumVersion": version,
    }
    assert profile_validator().is_valid(profile) is is_valid


@pytest.mark.parametrize("missing_key", ["author", "email", "name", "version"])
def test_profile_required_keys(missing_key: str):
    """author, email, name and version are required."""
    profile = {
        "name": "required_keys",
        "author": "QDT tests",
        "email": "qdt@example.org",
        "version": "1.0.0",
    }
    del profile[missing_key]
    assert not profile_validator().is_valid(profile)


@pytest.mark.parametrize(
    ("conditions", "is_valid"),
    [
        ({"all": [{"path": "$.env.QDT_X", "operator": "equal", "value": "1"}]}, True),
        ({"any": [{"path": "$.env.QDT_X", "operator": "in", "value": ["1"]}]}, True),
        (
            {"not": {"path": "$.env.QDT_X", "operator": "equal", "value": None}},
            True,
        ),
        (
            {
                "all": [
                    {"not": {"any": [{"operator": "equal", "value": 1, "path": "$.a"}]}}
                ]
            },
            True,
        ),
        # condition without path: the value is compared to the whole context
        ({"all": [{"operator": "equal", "value": {}}]}, True),
        (
            {
                "all": [
                    {
                        "path": "$.a",
                        "operator": "equal",
                        "value": 1,
                        "params": {"key": "value"},
                    }
                ]
            },
            True,
        ),
        # invalid ones
        ({}, False),
        ({"all": [], "any": []}, False),
        ({"all": [{"path": "$.a", "operator": "unknown_op", "value": 1}]}, False),
        ({"all": [{"path": "$.a", "operator": "equal"}]}, False),
        (
            {"all": [{"path": "$.a", "operator": "equal", "value": 1, "params": []}]},
            False,
        ),
    ],
)
def test_rules_conditions(conditions: dict, is_valid: bool):
    """Rules accept what python-rule-engine accepts: all, any, not, nested."""
    profile = {
        "name": "rules",
        "author": "QDT tests",
        "email": "qdt@example.org",
        "version": "1.0.0",
        "rules": [{"name": "test rule", "conditions": conditions}],
    }
    assert profile_validator().is_valid(profile) is is_valid


def test_rules_schema_matches_rule_engine():
    """The conditions declared valid by the schema are accepted by the engine."""
    rule_engine = pytest.importorskip("python_rule_engine")
    rule = {
        "name": "engine check",
        "description": "nested not, any and all",
        "conditions": {
            "all": [
                {"not": {"any": [{"path": "$.a", "operator": "equal", "value": 2}]}},
                {"operator": "contains", "path": "$.b", "value": "x"},
            ]
        },
    }
    profile = {
        "name": "engine",
        "author": "QDT tests",
        "email": "qdt@example.org",
        "version": "1.0.0",
        "rules": [rule],
    }
    assert profile_validator().is_valid(profile)

    engine = rule_engine.RuleEngine(rules=[rule])
    assert engine.evaluate({"a": 1, "b": ["x"]})
