from __future__ import annotations

from typing import List, Optional, Union, Literal

from pydantic import BaseModel


class Data1(BaseModel):
    type: Literal['text']
    content: str
    render_in_streaming: bool = ...
    quote_content: str = ...
    chat_model: str = ...


class Item(BaseModel):
    item_id: str
    conversation_id: str
    item_type: Literal['question', 'reply']
    summary: str
    data: Data1
    parent_item_id: Optional[str] = None


class Data(BaseModel):
    conversation_id: str
    items: List[Item]
    pre_generated_reply_id: str
    pre_parent_item_id: str
    origin: str = 'chrome-extension://ofpnmcalabcbjgholdjcjblkibolbppb/chatTab.html?tab=chat&botName=Monica&botUid=monica'
    origin_page_title: str = '聊天 - Monica'
    trigger_by: str = 'auto'
    use_model: str = 'gpt-4'
    knowledge_source: str = 'web'


class SysSkillListItem1(BaseModel):
    allow_user_modify: bool = False
    enable: bool = True
    force_enable: bool = False
    uid: str = 'web_access'


class SysSkillListItem2(BaseModel):
    uid: str = 'artifacts'
    enable: bool = True


class ToolData(BaseModel):
    sys_skill_list: List[Union[SysSkillListItem1, SysSkillListItem2]] = [SysSkillListItem1(), SysSkillListItem2()]


class ChatRequestBody(BaseModel):
    task_uid: str
    bot_uid: str = 'monica'
    data: Data
    language: str = 'auto'
    locale: str = 'zh_CN'
    task_type: str = 'chat_with_custom_bot'
    tool_data: ToolData = ToolData()
    ai_resp_language: str = 'Chinese (Simplified)'
