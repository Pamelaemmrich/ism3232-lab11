# my_queue.py
# Author: Pamela Emmrich


class PickupQueue:
    """Pickup changes waiting for a baker to approve. Nothing changes until they do."""

    def __init__(self, order_tool):
        """Start with no requests. Approved changes go through the order tool."""
        self.order_tool = order_tool
        self.requests = []

    def request_pickup_change(self, order_id, new_time):
        """Ask a baker to change the pickup time on one order. A baker must approve it.

        Args:
            order_id: The order ID, like B100.
            new_time: The full new pickup time, like 3 pm.
        """
        order_id = order_id.upper()
        if self.order_tool.find_status(order_id) is None:
            return "No order with that ID was found. Order IDs look like B100."
        number = len(self.requests) + 1
        request = {
            "number": number,
            "order_id": order_id,
            "new_time": new_time,
            "status": "waiting",
        }
        self.requests.append(request)
        return f"Request {number} was sent to a baker. The pickup time has not changed yet."

    def waiting(self):
        """Return the requests that are still waiting for a decision."""
        result = []
        for request in self.requests:
            if request["status"] == "waiting":
                result.append(request)
        return result

    def find(self, number):
        """Return the request with this number, or None."""
        for request in self.requests:
            if request["number"] == number:
                return request
        return None

    def approve(self, number):
        """Approve one waiting request and make the change."""
        request = self.find(number)
        if request is None:
            return f"There is no request {number}."
        if request["status"] != "waiting":
            return f"Request {number} is already {request['status']}."
        request["status"] = "approved"
        self.order_tool.change_pickup(request["order_id"], request["new_time"])
        return f"Request {number} approved."

    def reject(self, number):
        """Reject one waiting request. Nothing changes."""
        request = self.find(number)
        if request is None:
            return f"There is no request {number}."
        if request["status"] != "waiting":
            return f"Request {number} is already {request['status']}."
        request["status"] = "rejected"
        return f"Request {number} rejected."
