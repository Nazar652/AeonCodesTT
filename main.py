import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from ai import *
from config import bot_token


router = Router()


class UploadingPDF(StatesGroup):
    uploading_pdf = State()
    ready_to_answer = State()


@router.message(Command(commands=["start"]))
async def command_start(m: Message, state: FSMContext) -> None:

    await m.answer(f"Hello, i'm bot from technical task for AeonCodes.\n\n"
                   f"Send me PDF-file, from which i'll learn.")
    await state.set_state(UploadingPDF.uploading_pdf)


@router.message(UploadingPDF.uploading_pdf, F.document.file_name.contains('.pdf'))
async def upload_pdf(m: Message, state: FSMContext) -> None:
    message = await m.answer('File received, wait a few seconds.')
    file_id = m.document.file_id
    filename = f'docs/{str(uuid.uuid4())}.pdf'
    await bot.download(file_id, filename)
    new_qa = QA(filename)
    await state.update_data(qa=new_qa)
    await state.set_state(UploadingPDF.ready_to_answer)
    await message.edit_text('File processing is finished. Ask your question.')


@router.message(UploadingPDF.ready_to_answer)
async def answer(m: Message, state: FSMContext) -> None:
    data = await state.get_data()
    qa = data['qa']
    text: str = m.text
    message: Message = await m.answer(f"Request\n<code>{text}</code>\nreceived.\n\nWait a few seconds.")
    response: dict = qa.get_response(text)
    await message.edit_text(response['result'])
    await m.answer("Ask next question")


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    dp.include_router(router)
    bot = Bot(bot_token, parse_mode='HTML')
    asyncio.run(main())
