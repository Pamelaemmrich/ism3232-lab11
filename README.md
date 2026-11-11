# Bakery Assistant

## Mock assistant: Biscuit

Biscuit is a fictional bakery assistant that informs clients of the "baking" or "ready for pickup" status of a cake order. The orders are imaginary sample data, and their responses are derived from basic Python keyword rules rather than an AI model. Because they deal with money or altering an order, messages that contain the terms "refund," "payment," or "cancel" are forwarded to a human, a virtual assistant shouldn't make those decisions. Anything else receives an appropriate response stating that it is unsure of how to assist. Since nothing verifies who is requesting, anyone who entered another customer's order ID may access the status of that order using actual customer data.

### Model Testing and Design Decisions

During my test, Biscuit correctly answered the question, "When are you open?" by providing the bakery's hours, which worked because the information was included in its instructions. However, when I asked, "Do you sell gluten free bread?" it could not provide an answer and directed me to ask a baker for more details. This showed that the model could answer questions using its provided information but should not guess when it does not know something. I kept the order lookup and refund handoff in the code because these actions require accurate and consistent results every time. Having these tasks handled by code instead of relying on the model helps prevent incorrect order information or mistakes involving refunds.
## Week 12 upgrade

The model handled "Where is order B100?" well it asked for the look_up_order tool on its own, and Robin answered "Order B100 is ready." from the tool result. The toolbox refuses details the customer never typed in my FakeModel test, the model asked to change B100's pickup to 3 pm when the customer had only said "Please change the pickup on order B100", so the toolbox returned "The customer hasn't given that time" and nothing was queued. I added two sentences to the instructions, greet the customer and ask how to help if they only say hello, and ask for the missing detail if they want a pickup change without both the order ID and the time. I added them because a model can guess a missing detail, and the toolbox should be the last line of defense, not the first. A pickup change waits in the queue until a baker approves it, and approving it a second time changes nothing.
