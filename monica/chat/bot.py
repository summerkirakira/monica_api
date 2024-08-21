from typing import Optional, AsyncIterator
from abc import abstractmethod

from pydantic import BaseModel


class BaseBot:

    @abstractmethod
    def chat(self, conv_id: Optional[str], message: str) -> AsyncIterator[str]:
        pass
