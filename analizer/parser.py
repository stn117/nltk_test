from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

import string
# import re
import nltk


class TokensParser(object):
    """Summary
    
    Attributes:
        call_ins (list): Списое методов/классов которые принимают параметром
                         слово и оперируют им
        eng_alphabet (str): алфавит
        have_fake (bool): замечено мошенничество
        lang (str): основной язык текста
        loathing (float): Тошнота
        rapid (float): коэфициэнт для determineLang
        rus_alphabet (str): алфавит
        symbols_map (dict): {язык:[потенциально заменяемые символы]}
    """
    eng_alphabet = string.ascii_letters
    rus_alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦ"\
                   "ЧШЩЪЫЬЭЮЯ"

    def __init__(self, text_lang, default_symbols):
        self.lang = text_lang
        self.symbols_map = {text_lang: default_symbols}
        self.have_fake = False
        self.loathing = -1
        self.call_ins = [self.checkFakeSymbols]
        self.rapid = 0.25
        # self.rx_punct = re.compile('[%s]' % re.escape(string.punctuation))

    def addMethod(self, instance):
        self.call_ins.append(instance)

    def addSymbolMap(self, lang, symbols):
        self.symbols_map[lang] = symbols

    def rmSymbolMap(self, lang):
        if lang == self.lang:
            return
        del(self.symbols_map[lang])

    def normalized_words(self, text):
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(text)
        tokens = [self.modifyToken(t) for t in tokens]
        tokens = [x.lower() for x in tokens
                  if x not in stopwords.words(self.lang)]
        return tokens

    def modifyToken(self, token):
        for ins in self.call_ins:
            token = ins(token)
        return token

    def analize(self, text):
        tokens = self.normalized_words(text)
        counts = [c for k, c in FreqDist(tokens).most_common(5)]
        self.loathing = round(sum(counts) / len(tokens), 4)
        return self.have_fake, self.loathing

    def determineLang(self, token):
        """Невероятный костыль, полностью ломает парсер как таковой за счет
        использования потенциально не существующих словарей.

        Должен определять родной язык входящего слова. Сделано через вычисление
        отношения символов какого-либо алфавита к длине слова и сравнение с
        коэффициэнтом "self.rapid"

        Худший вариант - написание стоп-слов на иностранных языках.

        Args:
            token (str): input token

        Returns:
            str: lang type
        """
        rus_lenght = 0
        eng_lenght = 0
        for sym in token:
            if sym in self.rus_alphabet:
                rus_lenght += 1
            if sym in self.eng_alphabet:
                eng_lenght += 1

        if not rus_lenght:
            return 'english'

        if not rus_lenght:
            return 'russian'

        rus_ratio = rus_lenght / len(token)
        eng_lenght = eng_lenght / len(token)

        if rus_ratio < self.rapid:
            return 'english'

        if eng_lenght < self.rapid:
            return 'russian'
        return self.lang

    def checkFakeSymbols(self, token):
        # print(self.getLang(token))
        lang = self.determineLang(token)
        sym_map = self.symbols_map[lang]
        ret_value = ''
        for sym in token:
            contain_foreign = next((
                x for x in sym_map if sym == x[0]), None)
            if contain_foreign:
                self.have_fake = True
                ret_value += contain_foreign[1]
                continue
            ret_value += sym

        return ret_value

