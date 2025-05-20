"""
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

from .http_request import HttpRequestUtil
from .addon_config import (
    resolve_addon_config_by_attachment_or_color,
    resolve_addon_config_by_url,
)

__all__ = ['HttpRequestUtil', 'resolve_addon_config_by_attachment_or_color', 'resolve_addon_config_by_url']
