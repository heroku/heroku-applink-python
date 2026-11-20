# Copyright (c) 2026, Salesforce, Inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause

import json
from decimal import Decimal
from typing import Any, NoReturn, TypeGuard

type JsonObject = dict[str, Any]


class InvalidFieldError(Exception):
    def __init__(self, field: str) -> None:
        super().__init__(field)
        self.field = field


def _reject_constant(_name: str) -> NoReturn:
    raise ValueError


def parse_json_object(data: bytes) -> JsonObject | None:
    """Parses a strict UTF-8 JSON object, or returns None if that fails.

    Numbers with a fraction or exponent become Decimal, so they can't be
    mistaken for integers.
    """
    try:
        result: object = json.loads(
            data.decode("utf-8"),
            parse_float=Decimal,
            parse_constant=_reject_constant,
        )
    except (ValueError, RecursionError):
        return None
    return result if is_object(result) else None


def is_object(value: object) -> TypeGuard[JsonObject]:
    return isinstance(value, dict)


def is_non_empty_string(value: object) -> TypeGuard[str]:
    return isinstance(value, str) and value != ""


def required_object(data: JsonObject, field: str, prefix: str = "") -> JsonObject:
    value = data.get(field)
    if not is_object(value):
        raise InvalidFieldError(prefix + field)
    return value


def required_string(data: JsonObject, field: str, prefix: str = "") -> str:
    value = data.get(field)
    if not is_non_empty_string(value):
        raise InvalidFieldError(prefix + field)
    return value


def optional_string(data: JsonObject, field: str) -> str | None:
    value = data.get(field)
    if value is not None and not isinstance(value, str):
        raise InvalidFieldError(field)
    return value or None
