# SPDX-FileCopyrightText: 2025 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

import pytest
from pydantic import ValidationError
from test_models import (
    ForbidExtraTestModel,
    AnnotatedStrTestModel,
    AnnotatedStrListTestModel,
    ValidSchemaTestModel,
    ChildValidationTestModel,
    ChildExtraFieldsTestModel,
)
from schema import Schema


class TestBaseModelForbidExtra:
    """Test the BaseModelForbidExtra class functionality."""

    def test_extra_fields_not_allowed(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError) as exc_info:
            ForbidExtraTestModel(field="value", extra_field="not_allowed")

        assert "Extra inputs are not permitted" in str(exc_info.value)


class TestAnnotatedTypes:
    """Test the custom annotated types."""

    @pytest.mark.parametrize("test_input,expected", [
        ("valid", "valid"),
        ("a", "a"),
    ])
    def test_annotated_str_valid(self, test_input, expected):
        """Test valid AnnotatedStr values."""
        model_instance = AnnotatedStrTestModel(field=test_input)
        assert model_instance.field == expected

    @pytest.mark.parametrize("test_input", ["", "   "])
    def test_annotated_str_invalid(self, test_input):
        """Test invalid AnnotatedStr values."""
        with pytest.raises(ValidationError):
            AnnotatedStrTestModel(field=test_input)

    def test_annotated_str_list_valid(self):
        """Test valid AnnotatedStrList."""
        model_instance = AnnotatedStrListTestModel(fields=["valid", "values"])
        assert len(model_instance.fields) == 2

    @pytest.mark.parametrize("test_input", [[], [""], ["   "]])
    def test_annotated_str_list_invalid(self, test_input):
        """Test invalid AnnotatedStrList."""
        with pytest.raises(ValidationError):
            AnnotatedStrListTestModel(fields=test_input)


class TestSchema:
    """Test the Schema class functionality."""

    def test_from_yaml_valid(self):
        """Test loading valid YAML."""
        yaml_str = """field1: value1
field2: value2"""
        schema_instance = ValidSchemaTestModel.from_yaml(yaml_str)
        assert schema_instance.field1 == "value1"
        assert schema_instance.field2 == "value2"

    def test_from_yaml_invalid_yaml(self):
        """Test loading invalid YAML."""
        invalid_yaml = "field1: value1\nfield2: value2: value3"
        with pytest.raises(ValueError) as exc_info:
            Schema.from_yaml(invalid_yaml)
        assert "Failed to load YAML" in str(exc_info.value)

    def test_from_yaml_validation_error(self):
        """Test YAML that fails model validation."""
        yaml_str = "extra_field: value"
        with pytest.raises(ValueError) as exc_info:
            Schema.from_yaml(yaml_str)
        assert "Failed to initialize model" in str(exc_info.value)

    def test_from_yaml_empty_string(self):
        """Test empty YAML string."""
        with pytest.raises(ValidationError):
            Schema.from_yaml("")

    def test_from_yaml_whitespace_string(self):
        """Test whitespace-only YAML string."""
        with pytest.raises(ValidationError):
            Schema.from_yaml("   ")


class TestSchemaInheritance:
    """Test schema inheritance scenarios."""

    def test_inherited_schema_validation(self):
        """Test that inherited schemas maintain validation rules."""
        valid_yaml = "required_field: value"
        child_instance = ChildValidationTestModel.from_yaml(valid_yaml)
        assert child_instance.required_field == "value"
        assert child_instance.optional_field == "default"

        invalid_yaml = "optional_field: value"
        with pytest.raises(ValueError):
            ChildValidationTestModel.from_yaml(invalid_yaml)

    def test_inherited_schema_extra_fields(self):
        """Test that extra fields are still forbidden in child classes."""
        yaml_str = "field: value\nextra: not_allowed"
        with pytest.raises(ValueError) as exc_info:
            ChildExtraFieldsTestModel.from_yaml(yaml_str)
        assert "Extra inputs are not permitted" in str(exc_info.value)
