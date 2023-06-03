from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove
import kbin
from random import randint

API_TOKEN = "6266300066:AAHBNw-B-N4lNYz2c_pbX-ZWtxsN10UChTs"

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# sender, interceptor, reciever
players = [0, 0, 0]
chos_players = []
info = {}
info['turn'] = -1
info['round'] = 1

class Game(StatesGroup):
    role = State()

class Sender(StatesGroup):
    basis = State()
    degree = State()

class Interceptor(StatesGroup):
    todo = State()
    basis1 = State()
    basis2 = State()
    degree = State()

class Reciever(StatesGroup):
    basis = State()

@dp.message_handler(commands=['start'], state='*')
async def start_game(message: types.Message):
    if len(chos_players) < 3:
        if message.chat.id not in chos_players: 
            chos_players.append(message.chat.id)
            info[message.chat.id] = {}
            info[message.chat.id]['basis'] = ''
            info[message.chat.id]['bit'] = -1
            info[message.chat.id]['last_message'] = -1
            await Game.role.set()
            last_message = await message.answer("Выберите роль!", reply_markup=kbin.roles(players))
            info[message.chat.id]['last_message'] = last_message.message_id
    else:
        await message.answer("Уже есть 3 игрока")

@dp.callback_query_handler(state=Game.role)
async def choosing_role(call: types.CallbackQuery, state: FSMContext):
    if call.data in ["отправитель", "перехватчик", "получатель"]:
        if players.count(0) > 0:
            role_id = 0 if call.data == "отправитель" else 1 if call.data == "перехватчик" else 2
            if players[role_id] == 0:
                players[role_id] = call.message.chat.id
                await state.finish()
                if call.data == "отправитель":
                    await Sender.basis.set()
                if call.data == "перехватчик":
                    await Interceptor.todo.set()
                if call.data == "получатель":
                    await Reciever.basis.set()
                try:
                    await bot.delete_message(call.message.chat.id, info[call.message.chat.id]['last_message'])
                except:
                    pass
                await call.message.answer(f"Ваша роль - {call.data}", reply_markup = ReplyKeyboardRemove())
                for user_id in chos_players:
                    if user_id not in players:
                        try:
                            await bot.delete_message(user_id, info[user_id]['last_message'])
                        except:
                            pass
                        last_message = await bot.send_message(user_id, f"Роль {call.data} выбрана\nВыберите роль", reply_markup = kbin.roles(players))
                        info[user_id]['last_message'] = last_message.message_id
                if players.count(0) == 0:
                    for user_id in players:
                        try:
                            await bot.delete_message(user_id, info[user_id]['last_message'])
                        except:
                            pass
                    info['turn'] = 0
                    last_message = await bot.send_message(players[0], "Выберите базис", reply_markup = kbin.basis_kb)
                    info[players[0]]['last_message'] = last_message.message_id
                    last_message = await bot.send_message(players[1], "ждем отправителя")
                    info[players[1]]['last_message'] = last_message.message_id
                    last_message = await bot.send_message(players[2], "ждем отправителя")
                    info[players[2]]['last_message'] = last_message.message_id
            else:
                try:
                    await bot.delete_message(call.message.chat.id, info[call.message.chat.id]['last_message'])
                except:
                    pass
                last_message = await call.message.answer("Данная роль уже занята", reply_markup = kbin.roles(players))
                info[call.message.chat.id]['last_message'] = last_message.message_id
        else:
            try:
                await bot.delete_message(call.message.chat.id, info[call.message.chat.id]['last_message'])
            except:
                pass
            last_message = await call.message.answer("Уже есть 3 игрока", reply_markup = ReplyKeyboardRemove())
            info[call.message.chat.id]['last_message'] = last_message.message_id
    else:
        last_message = await call.message.answer("Выберите роль из данных ниже", reply_markup = kbin.roles(players))


@dp.callback_query_handler(state=Sender.basis)
async def sender_basis(call: types.CallbackQuery, state: FSMContext):
    if info['turn'] == 0:
        if call.data == 'Вертикальный базис':
            info[call.message.chat.id]['basis'] = call.data
            await bot.delete_message(call.message.chat.id, info[call.message.chat.id]['last_message'])
            last_message = await call.message.answer("Выберите направление", reply_markup = kbin.vertic_kb)
            info[call.message.chat.id]['last_message'] = last_message.message_id
            await Sender.degree.set()
        elif call.data == 'Диагональный базис':
            info[call.message.chat.id]['basis'] = call.data
            await bot.delete_message(chat_id=call.message.chat.id, message_id=info[call.message.chat.id]['last_message'])
            last_message = await call.message.answer("Выберите направление", reply_markup = kbin.diag_kb)
            info[call.message.chat.id]['last_message'] = last_message.message_id
            await Sender.degree.set()
        else:
            await call.message.answer("Выберите базис из кнопок", reply_markup = kbin.basis_kb)
    else:
        await call.message.answer("Не ваш ход")


@dp.callback_query_handler(state=Sender.degree)
async def sender_degree(call: types.CallbackQuery, state: FSMContext):
    if (info[call.message.chat.id]['basis'] == "Вертикальный базис" and (call.data == "90°" or call.data == "0°")) or (info[call.message.chat.id]['basis'] == "Диагональный базис" and (call.data == "45°" or call.data == "-45°")):
        await Sender.basis.set()
        info[call.message.chat.id]['bit'] = 1 if call.data == "90°" or call.data == "45°" else 0
        try:    
            await bot.delete_message(call.message.chat.id, info[call.message.chat.id]['last_message'])
        except:
            pass
        await call.message.answer(f"{info['round']} бит = {info[call.message.chat.id]['bit']}\n{info[call.message.chat.id]['basis']}", reply_markup = ReplyKeyboardRemove()) 
        try:
            await bot.delete_message(players[1], info[players[1]]['last_message'])
        except:
            pass
        last_message = await bot.send_message(players[1], "Перехватить?", reply_markup = kbin.todo_kb)
        info[players[1]]['last_message'] = last_message.message_id
        info['turn'] = 1
    else:
        await call.message.answer("Выберите направление из кнопок", reply_markup = kbin.basis_kb)


@dp.callback_query_handler(state=Interceptor.todo)
async def interceptor_todo(call: types.CallbackQuery, state: FSMContext):
    if info['turn'] == 1:
        if call.data == "Да":
            try:
                await bot.delete_message(players[1], info[players[1]]['last_message'])
            except:
                pass
            last_message = await bot.send_message(players[1], "Выберите базис", reply_markup = kbin.basis_kb)
            info[players[1]]['last_message'] = last_message.message_id            
            await Interceptor.basis1.set()
        else:
            try:
                await bot.delete_message(players[1], info[players[1]]['last_message'])
            except:
                pass
            await Interceptor.todo.set()
            info[players[1]]['basis'] = info[players[0]]['basis']
            info[players[1]]['bit'] = info[players[0]]['bit']
            info['turn'] = 2
            await call.message.answer("Перехват отменен", reply_markup = ReplyKeyboardRemove())
            try:
                await bot.delete_message(players[2], info[players[2]]['last_message'])
            except:
                pass
            last_message = await bot.send_message(players[2], "Выберите базис", reply_markup = kbin.basis_kb)
            info[players[2]]['last_message'] = last_message.message_id
    else:
        await call.message.answer("Не ваш ход")

@dp.callback_query_handler(state=Interceptor.basis1)
async def interceptor_basis1(call: types.CallbackQuery, state: FSMContext):
    if call.data in ["Вертикальный базис", "Диагональный базис"]:
        info[call.message.chat.id]['basis'] = call.data
        info[call.message.chat.id]['bit'] = info[players[0]]['bit'] if call.data == info[players[0]]['basis'] else randint(0, 1)
        try:
            await bot.delete_message(call.message.chat.id, info[call.message.chat.id]['last_message'])
        except:
            pass
        await call.message.answer(f"{info['round']} бит полученный = {info[call.message.chat.id]['bit']}\n{call.data}") 
        last_message = await call.message.answer("Выберите базис", reply_markup = kbin.basis_kb)
        info[call.message.chat.id]['last_message'] = last_message.message_id
        await Interceptor.basis2.set()
    else:
        await call.message.answer("Выберите базис из кнопок", reply_markup = kbin.basis_kb)

@dp.callback_query_handler(state=Interceptor.basis2)
async def interceptor_basis2(call: types.CallbackQuery, state: FSMContext):
    if call.data in ["Вертикальный базис", "Диагональный базис"]:
        info[call.message.chat.id]['basis'] = call.data
        if call.data == "Вертикальный базис":
            await bot.delete_message(call.message.chat.id, info[call.message.chat.id]['last_message'])
            last_message = await call.message.answer("Выберите направление", reply_markup = kbin.vertic_kb) 
            info[call.message.chat.id]['last_message'] = last_message.message_id
        else:
            await bot.delete_message(call.message.chat.id, info[call.message.chat.id]['last_message'])
            last_message = await call.message.answer("Выберите направление", reply_markup = kbin.diag_kb) 
            info[call.message.chat.id]['last_message'] = last_message.message_id
        await Interceptor.degree.set()
    else:
        await call.message.answer("Выберите базис из кнопок", reply_markup = kbin.basis_kb)


@dp.callback_query_handler(state=Interceptor.degree)
async def interceptor_degree(call: types.CallbackQuery, state: FSMContext):
    if (info[call.message.chat.id]['basis'] == "Вертикальный базис" and (call.data == "90°" or call.data == "0°")) or (info[call.message.chat.id]['basis'] == "Диагональный базис" and (call.data == "45°" or call.data == "-45°")):
        await Interceptor.basis1.set()
        info[call.message.chat.id]['bit'] = 1 if call.data == "90°" or call.data == "45°" else 0
        try:
            await bot.delete_message(call.message.chat.id, info[call.message.chat.id]['last_message'])
        except:
            pass
        await call.message.answer(f"{info['round']} бит отправленный = {info[call.message.chat.id]['bit']}\n{info[call.message.chat.id]['basis']}", reply_markup = ReplyKeyboardRemove()) 
        try:
            await bot.delete_message(players[2], info[players[2]]['last_message'])
        except:
            pass
        last_message = await bot.send_message(players[2], "Выберите базис", reply_markup = kbin.basis_kb)
        info[players[2]]['last_message'] = last_message.message_id
        info['turn'] = 2
    else:
        await call.message.answer("Выберите направление из кнопок", reply_markup = kbin.basis_kb)


@dp.callback_query_handler(state=Reciever.basis)
async def reciever_basis(call: types.CallbackQuery, state: FSMContext):
    if info['turn'] == 2:
        if call.data in ["Вертикальный базис", "Диагональный базис"]:
            info[call.message.chat.id]['bit'] = info[players[1]]['bit'] if call.data == info[players[1]]['basis'] else randint(0, 1)
            try:
                await bot.delete_message(call.message.chat.id, info[call.message.chat.id]['last_message'])
            except:
                pass
            last_message = await call.message.answer(f"{info['round']} бит = {info[call.message.chat.id]['bit']} \n {call.data}", reply_markup = ReplyKeyboardRemove()) 
            for user_id in players:
                await bot.send_message(user_id, f"{info['round']} раунд завершен")
            info["turn"] = 0
            info['round'] += 1
            try:
                await bot.delete_message(players[0], info[players[0]]['last_message'])
            except:
                pass
            last_message = await bot.send_message(players[0], "Выберите базис", reply_markup = kbin.basis_kb)
            info[players[0]]['last_message'] = last_message.message_id
        else:
            await call.message.answer("Выберите базис из кнопок", reply_markup = kbin.basis_kb)
    else:
        await call.message.answer("Не ваш ход")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
