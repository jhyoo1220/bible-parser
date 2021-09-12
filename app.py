import codecs
import io
from flask import Flask, request, render_template, jsonify, send_from_directory
from bible_parser.bible_reader import BibleReader, KOR_BOOK_TO_ENG
from bible_parser.book_chapter_verse_extractor import BookChapterVerseExtractor
from bible_parser.file_util import FileUtil
from bible_parser.pptx_builder import PPTX_OUTPUT_DIR, PPTXBuilder
from datetime import datetime

app = Flask(__name__)

KOR_BIBLE   = "./data/dbs/kor_bible.db"
ENG_BIBLE   = "./data/dbs/eng_bible.db"

def get_bible_text(bible_word, b_remove_annotation):
    kor_reader = BibleReader(KOR_BIBLE)
    eng_reader = BibleReader(ENG_BIBLE)

    divided = bible_word.split(' ')
    if not divided or len(divided) != 2:
        return jsonify(result="Error")

    extractor = BookChapterVerseExtractor()
    book_fullname = divided[0]
    chapter_verse = divided[1]
    chapter = extractor.extract_chapter(chapter_verse)
    verse_list = extractor.extract_verses(chapter_verse)

    bible_info = {
        'kor_book': book_fullname,
        'chapter': chapter,
        'verse_list': verse_list,
        'b_remove_annotation': b_remove_annotation,
    }

    kor_text = kor_reader.get_text(**bible_info)
    eng_text = eng_reader.get_text(**bible_info)

    kor_reader.close_connection()
    eng_reader.close_connection()

    book_eng = KOR_BOOK_TO_ENG.get(book_fullname)
    bible_text = {
        'book_kor': book_fullname,
        'book_eng': book_eng,
        'chapter_verse': chapter_verse,
    }
    text_list = []
    for verse in verse_list:
        verse_str = str(verse)
        curr_text = {
            'text_kor': f"{verse_str}. {kor_text.get(verse_str)}",
            'text_eng': f"{verse_str}. {eng_text.get(verse_str)}",
        }
        text_list.append(curr_text)
    bible_text['text_list'] = text_list

    return bible_text

@app.route("/")
def get_main_page():
    kor_books = list(KOR_BOOK_TO_ENG.keys())
    kor_books.sort()

    return render_template("index.html", bible_books=kor_books)

@app.route("/_parse_message")
def parse_message():
    message = request.args.get('message')

    extractor = BookChapterVerseExtractor()
    book_chapter_verse_list = extractor.extract_content_all(message, 'book_chapter_verse')

    results = []
    for book_chapter_verse in book_chapter_verse_list:
        book_abbr = extractor.extract_content(book_chapter_verse, 'book')
        chapter_verse = extractor.extract_content(book_chapter_verse, 'chapter_verse')

        book_fullname = extractor.get_book_fullname(book_abbr)
        extracted_chapter = extractor.extract_chapter(chapter_verse)
        extracted_verses = extractor.extract_verses(chapter_verse)

        if book_fullname is not None and extracted_chapter > 0 and len(extracted_verses) > 0:
            curr_result = f"{book_fullname} {chapter_verse}"
            results.append(curr_result)

    return jsonify(result=results)

@app.route("/_show_bible_text")
def show_bible_text():
    bible_word = request.args.get('bible_word')
    b_remove_annotation = True if request.args.get('remove_annotation') == 'true' else False

    bible_text = get_bible_text(bible_word, b_remove_annotation)
    content = bible_word
    for text in bible_text['text_list']:
        content += "\n" + text['text_kor']
        content += "\n" + text['text_eng']

    return jsonify(result=content)

@app.route("/_build_pptx_file")
def build_pptx_file():
    bible_word = request.args.get('bible_word')
    b_remove_annotation = True if request.args.get('remove_annotation') == 'true' else False

    bible_text = get_bible_text(bible_word, b_remove_annotation)

    FileUtil.remove_directory(PPTX_OUTPUT_DIR)
    output_filename = PPTXBuilder.build(**bible_text)

    return send_from_directory(PPTX_OUTPUT_DIR, output_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
