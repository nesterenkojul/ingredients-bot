from time import sleep
from database import Ingredients, session
import telebot

bot = telebot.TeleBot("Bot id here")
CURRENT_INGREDIENTS = []


def access_database(ingredient):
    try:
        s = session()
        table = s.query(Ingredients).filter(Ingredients.ingredient == ingredient)\
                 .order_by(Ingredients.count.desc()).all()
        s.close()
        pairings = (row.pairing for row in table) if table else None
        return pairings
    except Exception:
        return "Error"


def get_answer(message):
    info = bot.send_message(message.chat.id, "Send me an ingredient to add to your recipe")
    bot.register_next_step_handler(info, process_ingredient)


def adding_choice(message, ingredient):
    if message.text == "Finish":
        return finish(message)
    if message.text == "Try another one":
        return get_answer(message)
    if message.text == "Add to the recipe anyway":
        CURRENT_INGREDIENTS.append(ingredient)
        return get_answer(message)

    process_ingredient(message)


def suggest_alternative(message):
    CURRENT_INGREDIENTS.pop()
    s = session()
    suggestions = {}
    for item in message.text.split():
        table = s.query(Ingredients).filter(Ingredients.ingredient.contains(item.lower())).all()
        for row in table:
            if row.ingredient not in suggestions:
                suggestions[row.ingredient] = 1
            else:
                suggestions[row.ingredient] += 1
    s.close()
    alternatives = set(sorted(suggestions, key=suggestions.get, reverse=True))
    start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if alternatives:
        for alt in alternatives:
            if alt not in CURRENT_INGREDIENTS:
                start_markup.row(alt)
            else:
                alternatives.remove(alt)
    start_markup.row("Add to the recipe anyway")
    start_markup.row("Try another one")
    start_markup.row("Finish")
    reply = ("Haven't found this exact ingredient. Maybe one of these will work?" if alternatives else
             "Haven't found any pairings for this ingredient :(")
    info = bot.send_message(message.chat.id, reply, reply_markup=start_markup)
    bot.register_next_step_handler(info, adding_choice, message.text.strip().lower())


def again(message):
    if message.text == "Yeah":
        return start(message)
    bot.send_message(message.chat.id, "It was fun building with you :)")


def finish(message):
    global CURRENT_INGREDIENTS
    if len(CURRENT_INGREDIENTS) < 2:
        bot.send_message(message.chat.id, "Sorry that you haven't found what you've been looking for :(")
    else:
        recipe = "\n".join(CURRENT_INGREDIENTS)
        bot.send_message(message.chat.id, f"Here is the recipe that you've build\n\n{recipe}")
    sleep(2)
    start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    start_markup.row("Yeah")
    start_markup.row("Nah")
    info = bot.send_message(message.chat.id, "Wanna try again?", reply_markup=start_markup)
    bot.register_next_step_handler(info, again)


def choose_pairing(message):
    if message.text == "Add my own ingredient":
        return get_answer(message)
    if message.text == "Finish choosing":
        return finish(message)
    process_ingredient(message)


def process_ingredient(message):
    ingredient = message.text.strip().lower()
    global CURRENT_INGREDIENTS
    CURRENT_INGREDIENTS.append(ingredient)
    start_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    pairings = access_database(ingredient)
    if pairings == "Error":
        bot.send_message(message.chat.id, "Sorry, something went wrong :(\n Please, try again later")
        return None
    if not pairings:
        return suggest_alternative(message)
    counter = 0
    for pair in pairings:
        if pair not in CURRENT_INGREDIENTS:
            start_markup.row(pair)
            counter += 1
        if counter > 30:
            break
    start_markup.row("Add my own ingredient")
    start_markup.row("Finish choosing")
    info = bot.send_message(message.chat.id, "Choose a pairing", reply_markup=start_markup)
    bot.register_next_step_handler(info, choose_pairing)


@bot.message_handler(commands=["start"])
def info(message):
    bot.send_message(message.chat.id, "Hey! This bot helps you to construct a recipe with any ingredients\n"
                                      "based on their best pairings.\n\nWhat to do:\n"
                                      "1. Name the first ingredient.\n"
                                      "2. Choose a pairing from the list.\n"
                                      "3. Then choose another combo for this pairing or add a new one.\n"
                                      "4. Continue until you're satisfied with your choice.\n"
                                      "5. Ta-da! You have an ingredient combo to create your own unique recipe.")
    start(message)


def start(message):
    sleep(0.5)
    global CURRENT_INGREDIENTS
    CURRENT_INGREDIENTS = []
    info = bot.send_message(message.chat.id, "Send me an ingredient to start with")
    bot.register_next_step_handler(info, process_ingredient)


bot.infinity_polling()