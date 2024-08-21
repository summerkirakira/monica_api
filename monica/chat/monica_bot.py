from typing import AsyncIterator, Optional, Tuple

from .bot import BaseBot
from monica.config import get_config, Config
from httpx import AsyncClient
import json
from .model import ChatRequestBody, Item, Data1, Data
import uuid
from typing import Literal, Optional


def get_uuid() -> str:
    return str(uuid.uuid4()).lower()


def get_msg_id() -> str:
    return f"msg:{get_uuid()}"


def get_conv_id() -> str:
    return f"conv:{get_uuid()}"


def get_task_id() -> str:
    return f"task:{get_uuid()}"


class MonicaBot(BaseBot):
    def __init__(self, conv_id: Optional[str]):
        super().__init__()
        self.config: Config = get_config()
        self.client = self.get_client()
        if conv_id is None:
            self.conv_id = get_conv_id()

        self.conv_dict = {
            self.conv_id: {
                "parent_item_id": None,
                "pre_generated_reply_id": get_msg_id(),
                "parent_content": None
            }
        }
        self.is_frozen = False

    def get_text_item(self, item_type: str, item_id: str, content: str, parent_item_id: Optional[str]) -> Item:

        return Item(
            item_id=item_id,
            conversation_id=self.conv_id,
            item_type=item_type,
            summary=content,
            parent_item_id=parent_item_id,
            data=Data1(
                type="text",
                content=content,
                render_in_streaming=item_type == "question",
                quote_content="",
                chat_model=self.config.chat.chat_model
            )
        )

    def change_conversion(self, conv_id: str):
        self.conv_id = conv_id

    def freeze_conversion(self) -> str:
        self.is_frozen = True
        return self.conv_id

    def get_chat_request_body(self, message: str) -> ChatRequestBody:
        items: list[Item] = []
        if self.conv_dict[self.conv_id]["parent_item_id"] is not None:
            items.append(
                self.get_text_item(
                    item_type="reply",
                    item_id=self.conv_dict[self.conv_id]["parent_item_id"],
                    content=self.conv_dict[self.conv_id]["parent_content"],
                    parent_item_id=None
                )
            )
        new_message_id = get_msg_id()
        items.append(
            self.get_text_item(
                item_type="question",
                item_id=new_message_id,
                content=message,
                parent_item_id=self.conv_dict[self.conv_id]["parent_item_id"]
            )
        )

        conv_data = Data(
            conversation_id=self.conv_id,
            items=items,
            pre_generated_reply_id=self.conv_dict[self.conv_id]["pre_generated_reply_id"],
            pre_parent_item_id=new_message_id
        )

        return ChatRequestBody(
            task_uid=get_task_id(),
            data=conv_data
        )

    def chat(self, conv_id: Optional[str], message: str) -> AsyncIterator[str]:
        request_body = self.get_chat_request_body(message)
        return self.process_sse(request_body)

    def after_reply(self, reply: str):
        if self.is_frozen:
            return
        self.conv_dict[self.conv_id]["parent_item_id"] = self.conv_dict[self.conv_id]["pre_generated_reply_id"]
        self.conv_dict[self.conv_id]["parent_content"] = reply
        self.conv_dict[self.conv_id]["pre_generated_reply_id"] = get_msg_id()

    async def process_sse(self, request_body: ChatRequestBody) -> AsyncIterator[str]:
        total_reply = ""
        async with self.client.stream('POST', 'https://monica.im/api/custom_bot/chat', content=request_body.model_dump_json()) as response:
            async for line in response.aiter_lines():
                if line.startswith('data:'):
                    event_data = line[5:].strip()
                    data = json.loads(event_data)
                    total_reply += data['text']
                    if data.get('finished', False):
                        self.after_reply(total_reply)
                    yield data['text']

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'cookie': self.config.auth.cookie,
            "origin": "chrome-extension://ofpnmcalabcbjgholdjcjblkibolbppb",
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
        }

    def get_client(self) -> AsyncClient:
        return AsyncClient(
            headers=self.get_headers(),
            timeout=self.config.timeout
        )
