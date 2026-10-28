import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

TOKEN = "9284761407:AAHrlhlN6pSHzxJHyJ2EjAse7OKCvadcapc"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Registration(StatesGroup):
    name = State()
    age = State()
    phone = State()


@dp.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}!\nRo‘yxatdan o‘tish uchun ismingizni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.name)


@dp.message(Registration.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Yoshingizni kiriting (raqamda):")
    await state.set_state(Registration.age)


@dp.message(Registration.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, yoshingizni faqat raqamda kiriting!")
        return
    
    await state.update_data(age=int(message.text))
    
    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=" Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Telefon raqamingizni yuboring yoki quyidagi tugmani bosing:", reply_markup=phone_keyboard)
    await state.set_state(Registration.phone)


@dp.message(Registration.phone)
async def process_phone(message: Message, state: FSMContext):
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    await state.update_data(phone=phone)
    data = await state.get_data()

    # Ma'lumotlarni ko'rsatish
    text = (
        " **Ro‘yxatdan o‘tish muvaffaqiyatli yakunlandi!**\n\n"
        f" **Ism:** {data['name']}\n"
        f" **Yosh:** {data['age']}\n"
        f" **Telefon:** {data['phone']}"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    
   
    await state.clear()


@dp.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Bekor qilinadigan faol jarayon yo‘q.")
        return

    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=ReplyKeyboardRemove())

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())