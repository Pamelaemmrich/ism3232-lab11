# my_tool.py
# Author: Pamela Emmrich


class BakeryLookup:
    """A tool that knows about bakery orders. It knows nothing about chatting."""

    def __init__(self, orders):
        """Store the orders this tool can look up."""
        self.orders = orders

    def find_order_id(self, text):
        """Return the first known order ID mentioned in text, or None."""
        for order_id in self.orders:
            if order_id in text.upper():
                return order_id
        return None

    def find_status(self, order_id):
        """Return the status of one order, or None if there is no such order."""
        if order_id in self.orders:
            return self.orders[order_id]["status"]
        return None

    def look_up_order(self, order_id):
        """Look up the status of one bakery order.

        Args:
            order_id: The order ID, like B100.
        """
        found = self.find_order_id(order_id)
        if found is None:
            return "No order with that ID was found. Order IDs look like B100."
        return f"Order {found} is {self.find_status(found)}."

    def change_pickup(self, order_id, new_time):
        """Change the pickup time on one order. Only an approval calls this."""
        self.orders[order_id]["pickup"] = new_time