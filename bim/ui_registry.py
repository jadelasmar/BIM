UI_TOKENS = {
    "command_center": {
        "name": "Command Center",
        "icon": "layout-dashboard",
        "tone": "blue",
    },
    "inventory": {
        "name": "BIM Stock",
        "icon": "database",
        "tone": "blue",
    },
    "operations": {
        "name": "Operations",
        "icon": "trending-up",
        "tone": "green",
    },
    "settings": {
        "name": "Settings",
        "icon": "settings",
        "tone": "neutral",
    },
    "administration": {
        "name": "Administration",
        "icon": "settings",
        "tone": "neutral",
    },
    "total_products": {
        "label": "Total Products",
        "icon": "database",
        "tone": "blue",
    },
    "available_stock": {
        "label": "Available Stock",
        "icon": "layers",
        "tone": "green",
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
    "suppliers": {
        "label": "Suppliers",
        "icon": "suppliers",
        "tone": "purple",
    },
    "delivery_records": {
        "label": "Delivery Records",
        "icon": "delivery",
        "tone": "indigo",
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
    "receive_stock": {
        "label": "Receive Stock",
        "icon": "download",
        "tone": "green",
    },
    "create_delivery": {
        "label": "Create Delivery",
        "icon": "delivery",
        "tone": "indigo",
    },
    "add_supplier": {
        "label": "Add Supplier",
        "icon": "suppliers",
        "tone": "purple",
    },
    "stock_movement": {
        "label": "Stock Movement",
        "icon": "trending-up",
        "tone": "neutral",
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
