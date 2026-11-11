# my_toolbox.py
# Author: Pamela Emmrich


class BakeryToolbox:
    """Every tool request from the model comes through here and is checked."""

    def __init__(self, order_tool, change_queue):
        """Hold the tools the model is allowed to ask for."""
        self.order_tool = order_tool
        self.change_queue = change_queue

    def tool_list(self):
        """Return the tools the model may ask for. They are not called here."""
        return [
            self.order_tool.look_up_order,
            self.change_queue.request_pickup_change,
        ]

    def run(self, name, arguments, history):
        """Check one tool request. Run the tool only if every check passes."""
        if name == "look_up_order":
            order_id = self.clean(arguments, "order_id")
            if order_id == "":
                return "The order ID is missing. Ask the customer for it."
            if not self.customer_said(history, order_id):
                return "The customer has not given that order ID. Ask them for it."
            return self.order_tool.look_up_order(order_id)
        if name == "request_pickup_change":
            order_id = self.clean(arguments, "order_id")
            new_time = self.clean(arguments, "new_time")
            if order_id == "" or new_time == "":
                return "The order ID and the new pickup time are both needed."
            if not self.customer_said(history, order_id):
                return "The customer has not given that order ID. Ask them for it."
            if not self.customer_said(history, new_time):
                return "The customer has not given that time. Ask them for it."
            return self.change_queue.request_pickup_change(order_id, new_time)
        return f"There is no tool named {name}."

    def clean(self, arguments, key):
        """Return one argument as text without extra spaces, or "" if it is missing."""
        return str(arguments.get(key, "")).strip()

    def customer_said(self, history, text):
        """Return True if text appears in a message the customer typed."""
        for message in history:
            if message["role"] == "user" and text.lower() in message["content"].lower():
                return True
        return False
