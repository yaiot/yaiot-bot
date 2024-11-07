from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

router = Router()


@router.message(Command("links"))
async def cmd_links(message: Message):
    # TODO: Достать ссылки для тг-пользователя из базы

    links = []  # Заглушка

    if len(links) == 0:
        await message.answer("You have no available links to share")
        return

    response = "Available links:\n\n"

    for link in links:
        response += f"id: {link['id']}\n" f"link: {link['link']}\n"

    await message.answer(response)


@router.message(Command("revoke_link"))
async def cmd_revoke_links(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer(
            "Please provide scenario ID.\n" "Example: /revoke_link 12345"
        )
        return

    args = command.args.split(" ")

    if len(args) > 1:
        await message.answer(
            "Wrong command format\n" "Correct format: /revoke_link <id>"
        )
        return

    # TODO: Удалить ссылку из базы по id = args[0]. Сделать RETURNING link

    link = "ex"  # Заглушка

    await message.answer(f"Link {link} was successfully revoked")
