from aiogram import Router, F
from aiogram.types import Message
from aiogram.types import FSInputFile

import logging

router = Router()


@router.message(F.text)
async def all_message(message: Message) -> None:
    logging.info(f'all_message')
    if message.text == '/get_logfile':
        file_path = "py_log.log"
        await message.answer_document(FSInputFile(file_path))
    if message.text == '/get_dbfile':
        file_path = "database.db"
        await message.answer_document(FSInputFile(file_path))