from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from filters.is_admin import IsAdmin
from keyboards.inline.admin_panel_keyboard import back_button_keyboard
from loader import bot, get_admin_panel
from states.editing_message_state import MessageEditing
from loader import get_current_message_id
from utils.files_rw import save_admin_panel

router = Router()


@router.callback_query(F.data == "edit_message_button", IsAdmin())
async def start_editing_message(call: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="Отправьте новое сообщение", chat_id=call.from_user.id,
                                message_id=get_current_message_id(call.from_user.id),
                                reply_markup=back_button_keyboard)
    await state.set_state(MessageEditing.MessageEditing)
    await call.answer()


@router.message(MessageEditing.MessageEditing, IsAdmin())
async def edit_message_text(message: types.Message, state: FSMContext):
    text = message.text
    admin_panel = get_admin_panel()
    admin_panel.set_message_text(text)
    save_admin_panel(admin_panel)
    await bot.edit_message_text(text=f"Сообщение изменено. Новый текст: \n{message.text}", chat_id=message.from_user.id,
                                message_id=get_current_message_id(message.from_user.id),
                                reply_markup=back_button_keyboard)
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await state.clear()
