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
        "tone": "green",
    },
    "available_stock": {
        "label": "Available Stock",
        "icon": "check-circle-2",
        "tone": "teal",
    },
    "reserved_stock": {
        "label": "Reserved Stock",
        "icon": "clock-3",
        "tone": "purple",
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
        "tone": "blue",
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
        "tone": "teal",
    },
    "delivery_records": {
        "label": "Delivery Records",
        "icon": "delivery",
        "tone": "indigo",
    },
    "reservation_records": {
        "label": "Reservation Records",
        "icon": "clock-3",
        "tone": "purple",
    },
    "repair_records": {
        "label": "Repair Records",
        "icon": "wrench",
        "tone": "pink",
    },
    "client_return_records": {
        "label": "Client Returns",
        "icon": "reset",
        "tone": "yellow",
    },
    "clients": {
        "label": "Clients",
        "icon": "clients",
        "tone": "sky",
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
        "tone": "green",
    },
    "add_stock_unit": {
        "label": "Add Unit",
        "icon": "package-plus",
        "tone": "blue",
    },
    "receive_stock": {
        "label": "Receive Stock",
        "icon": "inbox",
        "tone": "teal",
    },
    "create_delivery": {
        "label": "Create Delivery",
        "icon": "delivery",
        "tone": "indigo",
    },
    "create_reservation": {
        "label": "Create Reservation",
        "icon": "clock-3",
        "tone": "purple",
    },
    "create_issue": {
        "label": "Create Temporary Assignment",
        "icon": "user-check",
        "tone": "cyan",
    },
    "create_repair": {
        "label": "Create Repair",
        "icon": "wrench",
        "tone": "pink",
    },
    "create_client_return": {
        "label": "Create Client Return",
        "icon": "reset",
        "tone": "yellow",
    },
    "add_supplier": {
        "label": "Add Supplier",
        "icon": "suppliers",
        "tone": "orange",
    },
    "add_client": {
        "label": "Add Client",
        "icon": "clients",
        "tone": "neutral",
    },
    "create_removal": {
        "label": "Remove Unit",
        "icon": "package-x",
        "tone": "danger",
    },
    "create_client_upgrade": {
        "label": "Add Client Upgrade",
        "icon": "refresh-cw",
        "tone": "sky",
    },
}


def ui_item(key, **overrides):
    item = UI_TOKENS[key].copy()
    item.update(overrides)
    return item
