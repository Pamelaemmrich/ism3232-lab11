from change_queue import ChangeQueue
from chatbot import SupportChatbot
from fake_model import FakeModel
from keyword_model import KeywordModel
from order_tool import OrderLookup
from stock_tool import StockLookup
from toolbox import Toolbox


class SilentModel:
    """A model that never has an answer. It stands in for Ollama being switched off."""

    def decide(self, instructions, history, tools):
        return None


def make_bot(model):
    """Build a fresh chatbot with its own tools and the model it is given."""
    orders = {
        "A100": {"status": "shipped", "address": "14 Bay Road"},
        "A101": {"status": "processing", "address": "3 Gull Lane"},
    }
    order_tool = OrderLookup(orders)
    stock_tool = StockLookup({"rain jacket": 12, "day pack": 0})
    tools = Toolbox(order_tool, stock_tool, ChangeQueue(order_tool))
    return SupportChatbot("Sunny", "Be friendly.", tools, model)


def ask_for_tool(name, arguments):
    """Build the decision a model returns when it wants a tool."""
    return {"tool": name, "arguments": arguments}


def test_respond_records_both_messages():
    bot = make_bot(KeywordModel())
    bot.respond("hello")
    assert len(bot.history) == 2
    assert bot.history[0]["role"] == "user"
    assert bot.history[1]["role"] == "assistant"


def test_order_question_uses_the_tool():
    bot = make_bot(KeywordModel())
    assert bot.respond("Where is order A100?") == "Order A100 is shipped."


def test_tool_use_is_recorded_in_the_history():
    bot = make_bot(KeywordModel())
    bot.respond("Where is order A100?")
    assert len(bot.history) == 3
    assert bot.history[1]["role"] == "tool"
    assert bot.history[1]["tool_name"] == "look_up_order"


def test_model_can_ask_for_a_tool_without_keywords():
    model = FakeModel(
        [
            ask_for_tool("look_up_order", {"order_id": "A101"}),
            {"text": "Your package A101 is still processing."},
        ]
    )
    bot = make_bot(model)
    bot.respond("Has my package A101 shipped?")
    assert bot.history[1]["content"] == "Order A101 is processing."


def test_payment_question_never_reaches_the_model():
    bot = make_bot(FakeModel([]))
    assert "human" in bot.respond("Can I pay with a different card?")


def test_safe_reply_when_the_model_has_no_answer():
    bot = make_bot(SilentModel())
    assert "try again" in bot.respond("hello")


def test_unknown_tool_is_refused():
    model = FakeModel(
        [ask_for_tool("delete_order", {"order_id": "A100"}), {"text": "Sorry."}]
    )
    bot = make_bot(model)
    bot.respond("Delete order A100")
    assert bot.history[1]["content"] == "There is no tool named delete_order."


def test_loop_stops_after_three_tool_rounds():
    request = ask_for_tool("look_up_order", {"order_id": "A100"})
    bot = make_bot(FakeModel([request, request, request]))
    reply = bot.respond("Where is order A100?")
    assert "human" in reply
    assert len(bot.history) == 5


def test_made_up_address_is_refused():
    model = FakeModel(
        [
            ask_for_tool(
                "request_address_change",
                {"order_id": "A100", "new_address": "123 Main St"},
            ),
            {"text": "What is the new address?"},
        ]
    )
    bot = make_bot(model)
    bot.respond("Please change the address on order A100")
    assert "has not given that address" in bot.history[1]["content"]
    assert bot.tools.change_queue.waiting() == []


def test_blank_address_is_refused():
    model = FakeModel(
        [
            ask_for_tool(
                "request_address_change", {"order_id": "A100", "new_address": ""}
            ),
            {"text": "What is the new address?"},
        ]
    )
    bot = make_bot(model)
    bot.respond("Please change the address on order A100")
    assert bot.tools.change_queue.waiting() == []


def test_address_change_waits_for_staff():
    model = FakeModel(
        [
            ask_for_tool(
                "request_address_change",
                {"order_id": "A100", "new_address": "9 Pine Street"},
            ),
            {"text": "Sent to staff."},
        ]
    )
    bot = make_bot(model)
    bot.respond("Change the address on order A100 to 9 Pine Street")
    assert len(bot.tools.change_queue.waiting()) == 1
    assert bot.tools.order_tool.orders["A100"]["address"] == "14 Bay Road"


def test_number_argument_does_not_crash():
    model = FakeModel(
        [ask_for_tool("look_up_order", {"order_id": 100}), {"text": "Not found."}]
    )
    bot = make_bot(model)
    assert bot.respond("Where is order 100?") == "Not found."


def test_two_chatbots_keep_separate_histories():
    first = make_bot(KeywordModel())
    second = make_bot(KeywordModel())
    first.respond("hello")
    assert len(first.history) == 2
    assert len(second.history) == 0


def test_count_user_messages_skips_tool_entries():
    bot = make_bot(KeywordModel())
    bot.respond("hello")
    bot.respond("Where is order A100?")
    assert bot.count_user_messages() == 2