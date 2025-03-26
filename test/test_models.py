# SPDX-FileCopyrightText: 2024 CERN (home.cern)
#
# SPDX-License-Identifier: BSD-3-Clause

from schema import BaseModelForbidExtra, Schema, AnnotatedStr, AnnotatedStrList


class ForbidExtraTestModel(BaseModelForbidExtra):
    field: str


class AnnotatedStrTestModel(BaseModelForbidExtra):
    field: AnnotatedStr


class AnnotatedStrListTestModel(BaseModelForbidExtra):
    fields: AnnotatedStrList


class ValidSchemaTestModel(Schema):
    field1: str
    field2: str


class ChildValidationTestModel(Schema):
    required_field: str
    optional_field: str = "default"


class ChildExtraFieldsTestModel(Schema):
    field: str
