from fake_model import FakeModel
from my_assistant import BakeryAssistant
from my_queue import PickupQueue
from my_tool import BakeryLookup
from my_toolbox import BakeryToolbox


class SilentModel:
    """A model that never has an answer. It stands in for Ollama being switched off."""

    def decide(self, instructions, history, tools):
        return None


def make_bot(model):
    """Build a fresh assistant with its own tools and the model it is given."""
    orders = {
        "B100": {"status": "ready", "pickup": "9 am"},
        "B101": {"status": "baking", "pickup": "11 am"},
    }
    order_tool = BakeryLookup(orders)
    tools = BakeryToolbox(order_tool, PickupQueue(order_tool))
    return BakeryAssistant("Robin", "Be friendly.", tools, model)


def ask_for_tool(name, arguments):
    """Build the decision a model returns when it wants a tool."""
    return {"tool": name, "arguments": arguments}


def test_model_asks_for_the_tool_and_the_result_is_recorded():
    model = FakeModel(
        [
            ask_for_tool("look_up_order", {"order_id": "B101"}),
            {"text": "Your order B101 is still baking."},
        ]
    )
    bot = make_bot(model)
    bot.respond("Is B101 ready?")
    assert bot.history[1]["role"] == "tool"
    assert bot.history[1]["content"] == "Order B101 is baking."


def test_handoff_never_reaches_the_model():
    bot = make_bot(FakeModel([]))
    assert "baker" in bot.respond("I want a refund")


def test_made_up_order_id_is_refused():
    model = FakeModel(
        [ask_for_tool("look_up_order", {"order_id": "B101"}), {"text": "Sorry."}]
    )
    bot = make_bot(model)
    bot.respond("Where is B100?")
    assert "has not given that order ID" in bot.history[1]["content"]


def test_made_up_pickup_time_is_refused():
    model = FakeModel(
        [
            ask_for_tool(
                "request_pickup_change", {"order_id": "B100", "new_time": "3 pm"}
            ),
            {"text": "What time would you like?"},
        ]
    )
    bot = make_bot(model)
    bot.respond("Please change the pickup on order B100")
    assert "has not given that time" in bot.history[1]["content"]
    assert bot.tools.change_queue.waiting() == []


def test_pickup_change_waits_for_a_baker():
    model = FakeModel(
        [
            ask_for_tool(
                "request_pickup_change", {"order_id": "B100", "new_time": "3 pm"}
            ),
            {"text": "Sent to a baker."},
        ]
    )
    bot = make_bot(model)
    bot.respond("Change order B100 pickup to 3 pm")
    assert len(bot.tools.change_queue.waiting()) == 1
    assert bot.tools.order_tool.orders["B100"]["pickup"] == "9 am"


def test_approve_makes_the_change_once():
    model = FakeModel(
        [
            ask_for_tool(
                "request_pickup_change", {"order_id": "B100", "new_time": "3 pm"}
            ),
            {"text": "Sent to a baker."},
        ]
    )
    bot = make_bot(model)
    bot.respond("Change order B100 pickup to 3 pm")
    assert bot.tools.change_queue.approve(1) == "Request 1 approved."
    assert bot.tools.order_tool.orders["B100"]["pickup"] == "3 pm"
    assert bot.tools.change_queue.approve(1) == "Request 1 is already approved."


def test_unknown_tool_is_refused():
    model = FakeModel(
        [ask_for_tool("delete_order", {"order_id": "B100"}), {"text": "Sorry."}]
    )
    bot = make_bot(model)
    bot.respond("Delete order B100")
    assert bot.history[1]["content"] == "There is no tool named delete_order."


def test_loop_stops_after_three_tool_rounds():
    request = ask_for_tool("look_up_order", {"order_id": "B100"})
    bot = make_bot(FakeModel([request, request, request]))
    reply = bot.respond("Where is B100?")
    assert "baker" in reply
    assert len(bot.history) == 5


def test_safe_reply_when_the_model_has_no_answer():
    bot = make_bot(SilentModel())
    assert "try again" in bot.respond("hello")
