# This validates input schemas

catalog_validate_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "catalog",
    "description": "Catalog loaded for dispatch",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "product_id": {
                "description": "The unique identifier for the product",
                "type": 'integer'
            },
            "mass_g": {
                "description": "This is the mass (grams) of the this product stocked currently",
                "type": "integer"
            },
            "product_name": {
                "description": "This is the name of the product",
                "type": "string"
            }
        },
        "required": ["product_id", "mass_g", "product_name"]
    },
}

restock_validate_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "catalog_restock",
    "description": "Catalog restock",
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "product_id": {
                "description": "The unique identifier for the product",
                "type": 'integer'
            },
            "quanity": {
                "description": "Quantity of orders required",
                "type": "integer"
            },
        },
        "required": ["product_id", "quantity"]
    },

}
