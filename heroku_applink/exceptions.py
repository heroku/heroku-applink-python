"""
Copyright (c) 2025, salesforce.com, inc.
All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

class ClientError(Exception):
    """Raised when there is an error with the HTTP client."""
    pass

class UnexpectedRestApiResponsePayload(Exception):
    """Raised when the API response is not in the expected format."""
    pass
