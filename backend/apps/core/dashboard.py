"""The Command Center's module dashboard: one summary card per module and one
Needs Attention list across all of them.

Every module contributes through a provider function (user -> {"section",
"attention"}) listed in DASHBOARD_PROVIDERS. When a new module is added, give
it a provider and list it here -- see the standing rule in CLAUDE.md.
"""

from apps.stock.dashboard import clients_dashboard, operations_dashboard, stock_dashboard

DASHBOARD_PROVIDERS = (
    stock_dashboard,
    operations_dashboard,
    clients_dashboard,
)

# Red rows (out of stock, overdue) come before orange ones.
ATTENTION_TONE_ORDER = {"danger": 0, "warning": 1}


def build_dashboard(user):
    sections = []
    attention = []
    for provider in DASHBOARD_PROVIDERS:
        result = provider(user)
        if result.get("section"):
            sections.append(result["section"])
        attention.extend(result.get("attention", []))
    attention.sort(key=lambda item: ATTENTION_TONE_ORDER.get(item["tone"], 2))
    return {"attention": attention, "sections": sections}
