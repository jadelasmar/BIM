UI_TOKENS = {
    "command_center": {
        "name": "Command Center",
        "icon": "layout-dashboard",
        "tone": "blue",
    },
    "inventory": {
        "name": "Inventory",
        "icon": "boxes",
        "tone": "blue",
    },
    "operations": {
        "name": "Operations",
        "icon": "workflow",
        "tone": "green",
    },
    "settings": {
        "name": "Settings",
        "icon": "settings",
        "tone": "neutral",
    },
    "administration": {
        "name": "Administration",
        "icon": "shield-check",
        "tone": "neutral",
    },
    "total_products": {
        "label": "Total Products",
        "icon": "package",
        "tone": "blue",
    },
    "available_stock": {
        "label": "Available Stock",
        "icon": "check-circle-2",
        "tone": "green",
    },
    "reserved_stock": {
        "label": "Reserved Stock",
        "icon": "clock-3",
        "tone": "indigo",
    },
    "out_of_stock": {
        "label": "Out of Stock Products",
        "icon": "package-x",
        "tone": "danger",
    },
    "low_stock": {
        "label": "Low Stock Alerts",
        "icon": "triangle-alert",
        "tone": "warning",
    },
    "pending_actions": {
        "label": "Pending Actions",
        "icon": "clipboard",
        "tone": "cyan",
    },
    "suppliers": {
        "label": "Suppliers",
        "icon": "suppliers",
        "tone": "purple",
    },
    "product_categories": {
        "label": "Product Categories",
        "icon": "package",
        "tone": "blue",
    },
    "receiving_records": {
        "label": "Receiving Records",
        "icon": "inbox",
        "tone": "sky",
    },
    "delivery_records": {
        "label": "Delivery Records",
        "icon": "delivery",
        "tone": "yellow",
    },
    "reservation_records": {
        "label": "Reservation Records",
        "icon": "clock-3",
        "tone": "warning",
    },
    "repair_records": {
        "label": "Repair Records",
        "icon": "wrench",
        "tone": "danger",
    },
    "client_return_records": {
        "label": "Client Returns",
        "icon": "reset",
        "tone": "green",
    },
    "clients": {
        "label": "Clients",
        "icon": "clients",
        "tone": "blue",
    },
    "active_users": {
        "label": "Active Users",
        "icon": "user-check",
        "tone": "neutral",
    },
    "new_stock_units": {
        "label": "New Stock Units",
        "icon": "receiving",
        "tone": "green",
    },
    "assets": {
        "name": "Assets",
        "label": "Total Assets",
        "icon": "cpu",
        "tone": "purple",
    },
    "knowledge_base": {
        "name": "Knowledge Base",
        "label": "Knowledge Docs",
        "icon": "book-open",
        "tone": "yellow",
    },
    "reports": {
        "name": "Reports",
        "icon": "bar-chart-3",
        "tone": "orange",
    },
    "add_product": {
        "label": "Add Product",
        "icon": "plus",
        "tone": "blue",
    },
    "add_stock_unit": {
        "label": "Add Unit",
        "icon": "package-plus",
        "tone": "green",
    },
    "receive_stock": {
        "label": "Receive Stock",
        "icon": "inbox",
        "tone": "green",
    },
    "create_delivery": {
        "label": "Create Delivery",
        "icon": "delivery",
        "tone": "indigo",
    },
    "create_reservation": {
        "label": "Create Reservation",
        "icon": "clock-3",
        "tone": "warning",
    },
    "create_issue": {
        "label": "Create Temporary Assignment",
        "icon": "user-check",
        "tone": "indigo",
    },
    "create_repair": {
        "label": "Create Repair",
        "icon": "wrench",
        "tone": "danger",
    },
    "create_client_return": {
        "label": "Create Client Return",
        "icon": "reset",
        "tone": "green",
    },
    "add_supplier": {
        "label": "Add Supplier",
        "icon": "suppliers",
        "tone": "purple",
    },
    "add_client": {
        "label": "Add Client",
        "icon": "clients",
        "tone": "blue",
    },
    "create_removal": {
        "label": "Remove Unit",
        "icon": "package-x",
        "tone": "danger",
    },
}


def ui_item(key, **overrides):
    item = UI_TOKENS[key].copy()
    item.update(overrides)
    return item


def disabled_ui_item(key, **overrides):
    return ui_item(
        key,
        enabled=False,
        tone="neutral",
        **overrides,
    )
