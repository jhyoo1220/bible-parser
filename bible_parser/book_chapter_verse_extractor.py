import re


BOOK_ABBR_TO_FULLNAME = {
    '창': '창세기',
    '출': '출애굽기',
    '레': '레위기',
    '민': '민수기',
    '신': '신명기',
    '수': '여호수아',
    '삿': '사사기',
    '룻': '룻기',
    '삼상': '사무엘상',
    '삼하': '사무엘하',
    '왕상': '열왕기상',
    '왕하': '열왕기하',
    '대상': '역대상',
    '대하': '역대하',
    '스': '에스라',
    '느': '느헤미야',
    '에': '에스더',
    '욥': '욥기',
    '시': '시편',
    '잠': '잠언',
    '전': '전도서',
    '아': '아가',
    '사': '이사야',
    '렘': '예레미야',
    '애': '예레미야애가',
    '겔': '에스겔',
    '단': '다니엘',
    '호': '호세아',
    '욜': '요엘',
    '암': '아모스',
    '옵': '오바댜',
    '욘': '요나',
    '미': '미가',
    '나': '나훔',
    '합': '하박국',
    '습': '스바냐',
    '학': '학개',
    '슥': '스가랴',
    '말': '말라기',
    '마': '마태복음',
    '막': '마가복음',
    '눅': '누가복음',
    '요': '요한복음',
    '행': '사도행전',
    '롬': '로마서',
    '고전': '고린도전서',
    '고후': '고린도후서',
    '갈': '갈라디아서',
    '엡': '에베소서',
    '빌': '빌립보서',
    '골': '골로새서',
    '살전': '데살로니가전서',
    '살후': '데살로니가후서',
    '딤전': '디모데전서',
    '딤후': '디모데후서',
    '딛': '디도서',
    '몬': '빌레몬서',
    '히': '히브리서',
    '약': '야고보서',
    '벧전': '베드로전서',
    '벧후': '베드로후서',
    '요일': '요한일서',
    '요이': '요한이서',
    '요삼': '요한삼서',
    '유': '유다서',
    '계': '요한계시록',
}

PATTERN_BOOK = "[가-힣]{1,2}"
PATTERN_CHAPTER_VERSE = "[0-9]{1,3}\:[0-9|\-|\~|\,]*[0-9]"


class BookChapterVerseExtractor(object):
    def __init__(self):
        self._book_chapter_verse_pattern = re.compile(PATTERN_BOOK + "[ ]?" + PATTERN_CHAPTER_VERSE)
        self._book_pattern = re.compile(PATTERN_BOOK)
        self._chapter_verse_pattern = re.compile(PATTERN_CHAPTER_VERSE)

    def extract_content_all(self, content, content_type):
        content_type_to_pattern = {
            'book_chapter_verse': self._book_chapter_verse_pattern,
            'book': self._book_pattern,
            'chapter_verse': self._chapter_verse_pattern,
        }

        pattern = content_type_to_pattern[content_type]
        return pattern.findall(content)

    def extract_content(self, content, content_type):
        result_list = self.extract_content_all(content, content_type)
        if result_list is None or len(result_list) <= 0:
            return None

        return result_list[0].replace('~', '-')

    @classmethod
    def get_book_fullname(cls, book_abbr):
        return BOOK_ABBR_TO_FULLNAME.get(book_abbr)

    def extract_chapter(self, content):
        if ':' not in content:
            return -1

        pos = content.index(':')
        return int(content[:pos])

    def extract_verses(self, content):
        if ':' not in content:
            return []

        pos = content.index(':')
        result_list = []

        prv_num = num = op = ""
        for ch in content[(pos + 1):]:
            if ch in '0123456789':
                num += ch
            else:
                if len(prv_num) <= 0:
                    if ch == ',':
                        result_list.append(int(num))
                        prv_num = num = op = ""
                    else:
                        prv_num = num
                        num = ""
                        op = ch
                else:
                    curr_list = self.extract_verse_range(prv_num, num)
                    if curr_list and len(curr_list) > 0:
                        result_list.extend(curr_list)
                    prv_num = num = op = ""

        if len(op) <= 0:
            result_list.append(int(num))
        else:
            curr_list = self.extract_verse_range(prv_num, num)
            if curr_list and len(curr_list) > 0:
                result_list.extend(curr_list)

        return result_list

    def extract_verse_range(self, str_from, str_to):
        int_from = int(str_from)
        int_to = int(str_to)

        if int_from >= int_to:
            return None

        return range(int_from, (int_to + 1))


if __name__ == '__main__':
    content = """
        살후1:8-9
        계20:10,14-15
        계21:8(두려워~~~~)
        벧후2:4 막9:42~48
        계22:15 마25:46"""

    extractor = BookChapterVerseExtractor()
    book_chapter_verse_list = extractor.extract_content_all(content, "book_chapter_verse")

    for book_chapter_verse in book_chapter_verse_list:
        book_abbr = extractor.extract_content(book_chapter_verse, "book")
        chapter_verse = extractor.extract_content(book_chapter_verse, "chapter_verse")
        print(book_abbr + " " + chapter_verse)

        book_fullname = extractor.get_book_fullname(book_abbr)
        extracted_chapter = extractor.extract_chapter(chapter_verse)
        extracted_verses = extractor.extract_verses(chapter_verse)

        if book_fullname is not None and extracted_chapter > 0 and len(extracted_verses) > 0:
            print(book_fullname + " " + str(extracted_chapter) + ":" + str(extracted_verses))

        print()
