"""Retail Remedy Operations tools for the hosted acl-remedy-advisor-hosted agent.

These six tools mirror the Module 06 MCP server, but are bundled directly into the
hosted agent container as Agent Framework ``@tool`` functions instead of being called
over the network. All data is loaded from the local ``retail-operations.json`` file —
no real POS, CRM, or database connections are required.

Bundling the tools in-process keeps the hosted agent self-contained: there is no MCP
server to run or dev tunnel to expose, so the same agent image deploys cleanly to
Foundry hosted agents (Module 09).
"""

import json
from pathlib import Path
from typing import Annotated

from agent_framework import tool
from pydantic import Field

_DATA_FILE = Path(__file__).parent / 'retail-operations.json'

with _DATA_FILE.open() as _f:
    _DATA = json.load(_f)

_PURCHASES: dict = {p['receipt_id']: p for p in _DATA['purchases']}
_PRODUCTS: dict = {p['product_id']: p for p in _DATA['products']}
_POLICIES: list = _DATA['policies']
_INVENTORY: dict = _DATA['inventory']


@tool(approval_mode='never_require')
def lookup_purchase(
    receipt_id: Annotated[str, Field(description='The receipt ID to look up, for example R-1007.')],
) -> dict:
    """Return the purchase record for the given receipt ID.

    Returns the full purchase record including customer ID, product ID,
    purchase date, price paid, channel, and store location.
    Returns an error dict if the receipt ID is not found.
    """
    record = _PURCHASES.get(receipt_id)
    if record is None:
        return {'error': f'Receipt {receipt_id} not found'}
    return record


@tool(approval_mode='never_require')
def get_product_profile(
    product_id: Annotated[str, Field(description='The product ID to profile, for example PROD-LAPTOP-14.')],
) -> dict:
    """Return the product profile for the given product ID.

    Includes category, brand, expected lifespan in months, manufacturer
    warranty period in months, repairability rating, and current RRP.
    Returns an error dict if the product ID is not found.
    """
    profile = _PRODUCTS.get(product_id)
    if profile is None:
        return {'error': f'Product {product_id} not found'}
    return profile


@tool(approval_mode='never_require')
def search_store_policy(
    topic: Annotated[str, Field(description='The policy topic or keyword to search for, for example "major failure".')],
) -> list[dict]:
    """Search store policies for excerpts relevant to the given topic.

    Matches against policy titles and keywords. Returns a list of matching
    policy objects each containing a title and an excerpt. Returns a note
    dict if no policies match.
    """
    topic_lower = topic.lower()
    results = [
        p for p in _POLICIES
        if any(topic_lower in kw.lower() for kw in p.get('keywords', []))
        or topic_lower in p.get('title', '').lower()
    ]
    return results or [{'note': f'No specific policy found for topic: {topic}'}]


@tool(approval_mode='never_require')
def find_replacement_options(
    product_id: Annotated[str, Field(description='The product ID to find replacements for, for example PROD-LAPTOP-14.')],
) -> dict:
    """Return available in-stock replacement products comparable to the given product ID.

    Includes current stock status and a list of replacement options with
    current prices and price deltas relative to the original purchase price.
    Returns an error dict if no inventory data exists for the product ID.
    """
    entry = _INVENTORY.get(product_id)
    if entry is None:
        return {'error': f'No inventory data for product {product_id}'}
    return entry


@tool(approval_mode='never_require')
def draft_remedy_summary(
    receipt_id: Annotated[str, Field(description='The receipt ID for the remedy.')],
    product_name: Annotated[str, Field(description='The product name involved in the remedy.')],
    issue: Annotated[str, Field(description='A short description of the reported issue.')],
    likely_failure_type: Annotated[str, Field(description="The ACL assessment: 'major' or 'minor'.")],
    recommended_remedy: Annotated[str, Field(description='The recommended remedy, for example refund, replacement, or repair.')],
    notes: Annotated[str, Field(description='Optional additional notes.')] = '',
) -> dict:
    """Produce a structured staff-facing remedy summary.

    Compiles the key facts into a formatted summary for the staff member to
    present or record. Does not persist any data. The likely_failure_type
    should be 'major' or 'minor' based on the ACL assessment.
    """
    return {
        'receipt_id': receipt_id,
        'product_name': product_name,
        'issue': issue,
        'likely_failure_type': likely_failure_type,
        'recommended_remedy': recommended_remedy,
        'notes': notes,
        'status': 'draft',
        'disclaimer': 'General guidance only — not legal advice.',
    }


@tool(approval_mode='never_require')
def create_remedy_case(
    receipt_id: Annotated[str, Field(description='The receipt ID for the remedy case.')],
    remedy_type: Annotated[str, Field(description='The remedy type, for example refund, replacement, or repair.')],
    notes: Annotated[str, Field(description='Optional additional notes.')] = '',
) -> dict:
    """Simulate creating a remedy case in the retail operations system.

    Returns a deterministic case ID for demonstration purposes.
    No data is actually persisted — this is a mocked write operation
    that shows how the agent would log an approved remedy outcome.
    """
    receipt_num = ''.join(filter(str.isdigit, receipt_id)) or '0'
    case_id = f'CASE-2026-{int(receipt_num) % 10000:05d}'
    return {
        'case_id': case_id,
        'receipt_id': receipt_id,
        'remedy_type': remedy_type,
        'notes': notes,
        'status': 'created',
        'message': f'Case {case_id} created successfully (simulated).',
    }


RETAIL_TOOLS = [
    lookup_purchase,
    get_product_profile,
    search_store_policy,
    find_replacement_options,
    draft_remedy_summary,
    create_remedy_case,
]
