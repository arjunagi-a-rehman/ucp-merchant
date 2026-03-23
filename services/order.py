from models.order import Order

class OrderService:
    def __init__(self):
        self.orders = {}
        
    def create_order(self, order_id: str, line_items: list, buyer: dict) -> Order:
        order = Order(
            id=order_id,
            status="processing",
            line_items=line_items,
            buyer=buyer,
            tracking_url=f"https://track.example.com/{order_id}"
        )
        self.orders[order_id] = order
        return order
        
    def get_order(self, order_id: str) -> Order:
        if order_id not in self.orders:
            raise ValueError("Order not found")
        return self.orders[order_id]

order_service = OrderService()
