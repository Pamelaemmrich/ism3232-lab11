# my_main.py
# Author: Pamela Emmrich

from my_assistant import BakeryAssistant
from my_queue import PickupQueue
from my_tool import BakeryLookup
from my_toolbox import BakeryToolbox
from ollama_model import OllamaModel

MODEL_NAME = "granite4.1:3b"

INSTRUCTIONS = """You are Robin, a helper for a bakery.
Answer in one short sentence. If the customer only says hello, greet them and ask how you can help.
If the customer wants to change a pickup time but has not given both the order ID and the time, ask for what is missing.
Only state facts that appear in these instructions or in tool results.
If you do not know, say you do not know and offer to pass the customer to a baker."""

ORDERS = {
    "B100": {"status": "ready", "pickup": "9 am"},
    "B101": {"status": "baking", "pickup": "11 am"},
    "B102": {"status": "picked up", "pickup": "8 am"},
}

order_tool = BakeryLookup(ORDERS)
change_queue = PickupQueue(order_tool)
tools = BakeryToolbox(order_tool, change_queue)
model = OllamaModel(MODEL_NAME)
bot = BakeryAssistant("Robin", INSTRUCTIONS, tools, model)

print("Type a message, or type quit to stop.")
user_message = input("You: ")
while user_message != "quit":
    print(f"{bot.name}: {bot.respond(user_message)}")
    user_message = input("You: ")

print(f"Messages in this conversation: {len(bot.history)}")

print("Baker review")
for request in change_queue.waiting():
    number = request["number"]
    print(f"Request {number}: {request['order_id']} to {request['new_time']}")
    answer = input("Approve? yes or no: ")
    if answer == "yes":
        print(change_queue.approve(number))
    else:
        print(change_queue.reject(number))

for order_id in ORDERS:
    print(order_id, ORDERS[order_id]["pickup"])
