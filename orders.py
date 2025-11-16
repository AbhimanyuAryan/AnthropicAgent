"""
Sample order and customer data for demos.
"""

orders = {
    "O1": {
        "id": "O1",
        "product": "Laptop",
        "quantity": 1,
        "price": 1200,
        "status": "shipped",
        "customer_id": "C1"
    },
    "O2": {
        "id": "O2",
        "product": "Mouse",
        "quantity": 2,
        "price": 25,
        "status": "delivered",
        "customer_id": "C1"
    },
    "O3": {
        "id": "O3",
        "product": "Keyboard",
        "quantity": 1,
        "price": 75,
        "status": "processing",
        "customer_id": "C2"
    },
    "O4": {
        "id": "O4",
        "product": "Monitor",
        "quantity": 2,
        "price": 300,
        "status": "shipped",
        "customer_id": "C2"
    }
}

customers = {
    "C1": {
        "id": "C1",
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-0123",
        "orders": [
            orders["O1"],
            orders["O2"]
        ]
    },
    "C2": {
        "id": "C2",
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "555-0456",
        "orders": [
            orders["O3"],
            orders["O4"]
        ]
    }
}
