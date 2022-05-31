from vk_api.bot_longpoll import VkBotEventType
from event_handlers import longpoll

from Settings_bot.event_handlers import MessageNew, MessageEvent

for event in longpoll.listen():

    if event.type == VkBotEventType.MESSAGE_NEW:
        chat1 = MessageNew(event)

    elif event.type == VkBotEventType.MESSAGE_EVENT:
        chat2 = MessageEvent(event)

if __name__ == '__main__':
    pass
