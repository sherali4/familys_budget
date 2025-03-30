# import emoji
# print(emoji.emojize(":watermelon:"))  # 🍉
# print(emoji.emojize(":grapes:"))      # 🍇
# print(emoji.emojize(":Vine:", language="alias", variant='emoji_type'))
# print(emoji.EMOJI_DATA.keys())  # Mavjud barcha emoji'lar


import emoji
from difflib import get_close_matches
from deep_translator import GoogleTranslator


def find_best_emoji(product_name):
    """Kiritilgan mahsulot nomiga mos emoji topish"""
    product_name = product_name.lower()

    # 1️⃣ Tarjima qilish (agar so‘z o‘zbek tilida bo‘lsa)
    translated = GoogleTranslator(source="uz", target="en").translate(product_name)
    translated = translated.lower()

    # 2️⃣ To‘g‘ridan-to‘g‘ri emojini tekshirish
    emoji_text = f":{translated}:"
    emojized = emoji.emojize(emoji_text, language="en")

    if emojized != emoji_text:  # Agar emoji topilgan bo‘lsa
        return emojized

    # 3️⃣ O‘xshash nomli emoji topish
    emoji_aliases = emoji.EMOJI_DATA.keys()  # Barcha emoji kalit so‘zlari
    close_matches = get_close_matches(translated, emoji_aliases, n=1, cutoff=0.6)

    if close_matches:
        return emoji.emojize(f":{close_matches[0]}:", language="alias")

    # 4️⃣ Agar hech qanday mos keladigan emoji topilmasa
    return "🔹"


# 🔍 Test qilish:
test_products = ["yeryong‘oq", "karam", "olma", "anor", "non", "baliq", "tuxum", "random"]
for product in test_products:
    translated = GoogleTranslator(source="uz", target="en").translate(product)
    print(f"{product} - {translated}: {find_best_emoji(product)}")


print('------------------------')
text = 'Python is 👍'

print(text[10:11])