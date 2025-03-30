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


class Emojilar:

    def __init__(self, matn):
        self.matn = matn

    def topish(self):
        for index, char in enumerate(self.matn):
            if char in emoji.EMOJI_DATA:
                # return index  # Birinchi emoji qayerda joylashganini qaytaradi
                return self.matn[index]
        return False  # Agar emoji bo‘lmasa

