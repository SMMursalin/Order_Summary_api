{
    "name": "Order Summary",
    "version": "18.0.1.0.1",
    "summary": "demo",
    "author": "mursalin",
    "category": "General Module (API)",
    "license": "LGPL-3",
    "depends": ["base", "web", "bus", "stock", "sale", "mrp"],
    "data": [
        "security/ir.model.access.csv",
    ],
    "assets": {
        "web.assets_backend": [

        ],
    },
    # "external_dependencies": {"python": ["PyJWT"]},
    "installable": True,
    "application": False,
}
