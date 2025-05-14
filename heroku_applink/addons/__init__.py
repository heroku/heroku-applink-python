"""
Copyright (c) 2024, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

from .heroku_applink import get_authorization, resolve_addon_config_by_attachment, resolve_addon_config_by_url

__all__ = ['get_authorization', 'resolve_addon_config_by_attachment', 'resolve_addon_config_by_url']
