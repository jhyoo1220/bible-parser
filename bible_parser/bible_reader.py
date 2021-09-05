import re
import sqlite3

KOR_BOOK_TO_ENG = {
	'창세기': 'Genesis',
	'출애굽기': 'Exodus',
	'레위기': 'Leviticus',
	'민수기': 'Numbers',
	'신명기': 'Deuteronomy',
	'여호수아': 'Joshua',
	'사사기': 'Judges',
	'룻기': 'Ruth',
	'사무엘상': 'FirstSamuel',
	'사무엘하': 'SecondSamuel',
	'열왕기상': 'FirstKings',
	'열왕기하': 'SecondKings',
	'역대상': 'FirstChronicles',
	'역대하': 'SecondChronicles',
	'에스라': 'Ezra',
	'느헤미야': 'Nehemiah',
	'에스더': 'Esther',
	'욥기': 'Job',
	'시편': 'Psalms',
	'잠언': 'Proverbs',
	'전도서': 'Ecclesiastes',
	'아가': 'SongOfSongs',
	'이사야': 'Isaiah',
	'예레미야': 'Jeremiah',
	'예레미야애가': 'Lamentations',
	'에스겔': 'Ezekiel',
	'다니엘': 'Daniel',
	'호세아': 'Hosea',
	'요엘': 'Joel',
	'아모스': 'Amos',
	'오바댜': 'Obadiah',
	'요나': 'Jonah',
	'미가': 'Micah',
	'나훔': 'Nahum',
	'하박국': 'Habakkuk',
	'스바냐': 'Zephaniah',
	'학개': 'Haggai',
	'스가랴': 'Zechariah',
	'말라기': 'Malachi',
	'마태복음': 'Matthew',
	'마가복음': 'Mark',
	'누가복음': 'Luke',
	'요한복음': 'John',
	'사도행전': 'Acts',
	'로마서': 'Romans',
	'고린도전서': 'FirstCorinthians',
	'고린도후서': 'SecondCorinthians',
	'갈라디아서': 'Galatians',
	'에베소서': 'Ephesians',
	'빌립보서': 'Philippians',
	'골로새서': 'Colossians',
	'데살로니가전서': 'FirstThessalonians',
	'데살로니가후서': 'SecondThessalonians',
	'디모데전서': 'FirstTimothy',
	'디모데후서': 'SecondTimothy',
	'디도서': 'Titus',
	'빌레몬서': 'Philemon',
	'히브리서': 'Hebrews',
	'야고보서': 'James',
	'베드로전서': 'FirstPeter',
	'베드로후서': 'SecondPeter',
	'요한일서': 'FirstJohn',
	'요한이서': 'SecondJohn',
	'요한삼서': 'ThirdJohn',
	'유다서': 'Jude',
	'요한계시록': 'Revelation',
}

class BibleReader(object):
	def __init__(self, db_file):
		self._conn = sqlite3.connect(db_file)
		self._cursor = self._conn.cursor()

	@classmethod
	def is_valid(cls, kor_book):
		return kor_book in KOR_BOOK_TO_ENG.keys()

	@classmethod
	def _get_eng_book(cls, kor_book):
		return KOR_BOOK_TO_ENG.get(kor_book)

	@classmethod
	def _is_alpha_unicode(cls, ch):
		ord_val = ord(ch)
		if ord_val >= ord('a') and ord_val <= ord('z') or ord_val >= ord('A') and ord_val <= ord('Z'):
			return True

		return False

	def _read_text_from_db(self, kor_book, chapter, verse_list):
		eng_book = self._get_eng_book(kor_book)
		if eng_book is None:
			return {}

		self._cursor.execute("""SELECT * FROM %(book)s 
			WHERE contents_type = 1 AND chapter = %(chapter)s 
			AND verse IN (%(verses)s) 
			ORDER BY chapter ASC, verse ASC, verseIdx ASC""" % {
				'book': eng_book,
				'chapter': chapter, 
				'verses': ", ".join(str(x) for x in verse_list),
			}
		)

		results = {}
		for curr in self._cursor:
			chapter = curr[1]
			verse = curr[2]
			text = curr[5]

			# Some bible texts are divided into multiple verses.
			key = str(verse)
			if key in results:
				results[key] += " " + text
			else:
				results[key] = text

		return results

	def _remove_annotation(self, text):
		if not re.search("[가-힣]+", text):
			return text

		refined = ""
		cnt_bracket = 0
		for ch in text:
			if ch == '(':
				cnt_bracket += 1

			if cnt_bracket > 0:
				if ch == ')':
					cnt_bracket -= 1

				continue

			if not self._is_alpha_unicode(ch):
				refined += ch

		return refined

	def get_text(self, kor_book, chapter, verse_list, b_remove_annotation):
		text = self._read_text_from_db(kor_book, chapter, verse_list)
		refined_text = dict()

		for verse in text.keys():
			if b_remove_annotation:
				refined_content = self._remove_annotation(text[verse])
			else:
				refined_content = text[verse]
			refined_text[verse] = refined_content

		return refined_text

	def close_connection(self):
		self._conn.close()

if __name__ == '__main__':
	reader = BibleReader("./data/dbs/kor_bible.db")

	verse_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
	text = reader.get_text("시편", 1, verse_list, True)
	print(text)

	reader.close_connection()
