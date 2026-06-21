from unittest.mock import AsyncMock, patch

import pytest
from aiogram.types import Message

from services import transcribe_audio
from tests.conftest import make_event


class TestHandleAudioOrVideo:
    @patch.object(Message, "edit_text", new_callable=AsyncMock)
    @pytest.mark.asyncio
    async def test_transcribe_audio(self, mock_edit, tiny_model, monkeypatch):
        event = make_event()
        monkeypatch.setattr("services._model", tiny_model)

        await transcribe_audio(event, "tests/test.ogg")

        assert mock_edit.call_count > 0
        assert len(mock_edit.call_args_list[-1].args[0]) > 0
