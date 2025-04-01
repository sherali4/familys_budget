import emoji

# def find_first_emoji(text):
#     for index, char in enumerate(text):
#         if char in emoji.EMOJI_DATA:
#             return index  # Birinchi emoji qayerda joylashganini qaytaradi
#     return None  # Agar emoji bo‘lmasa
#
# # 🔍 Test
# text = "karam: 🥬, olma 🍎"
# print(find_first_emoji(text))  # 7 (🥬 emojisi 7-joyda)
# print(text[7])


from functions.emoji import Emojilar

print(Emojilar('olma 🍎').topish())

