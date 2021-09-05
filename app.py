import codecs
import io
from flask import Flask, request, render_template, jsonify, send_from_directory
from extractor import BibleWordExtractor, Book, ChapterVerseExtractor
from bible import Bible
from db_connector import Execution, DBBook
from datetime import datetime
from log import Log
from base64 import b64encode
from pptx import build_pptx, remove_old_pptx, PPTX_FILES, PPTX_ERROR_FILE

app = Flask(__name__)

KOR_BIBLE   = 'db/kor_bible.db'
ENG_BIBLE   = 'db/eng_bible.db'

def extract_bible_word(message):
    extractor = BibleWordExtractor()
    bible_word_list = extractor.extract_bible_word(message)

    if not bible_word_list:
        return []

    results = []
    for curr in bible_word_list:
        book = extractor.extract_book(curr)
        chapter_verse = extractor.extract_chapter_verse(curr)

        book_fullname = Book.get_fullname(book)
        if book_fullname is not None and ChapterVerseExtractor.extract_chapter(chapter_verse) > 0 and len(ChapterVerseExtractor.extract_verses(chapter_verse)) > 0:
            results.append(encode_bible_word_form(book_fullname, chapter_verse))

    return results

def encode_bible_word_form(book_fullname, chapter_verse):
    return book_fullname + u' ' + chapter_verse

def decode_bible_word_form(bible_word_form):
    content = bible_word_form.split(u' ')
    if not content or len(content) != 2:
        return None, None

    return content[0], content[1]

@app.route('/')
def get_main_page():
    book_fullnames = DBBook.book_fullname_to_db.keys()
    book_fullnames.sort()
    return render_template('index.html', bible_books=book_fullnames)

@app.route('/_parse_message')
def parse_message():
    message = request.args.get('message')
    bible_word_list = extract_bible_word(message)
    Log.log_parsed_bible_word(message, bible_word_list)
    return jsonify(result=bible_word_list)

@app.route('/_show_bible_text')
def show_bible_text():
    version_list = [KOR_BIBLE, ENG_BIBLE]
    query_with_version = {}
    query_with_version[KOR_BIBLE] = Execution(KOR_BIBLE)
    query_with_version[ENG_BIBLE] = Execution(ENG_BIBLE)

    bible_word = request.args.get('bible_word')
    b_remove_annotation = True if request.args.get('remove_annotation') == 'true' else False
    
    book_fullname, chapter_verse = decode_bible_word_form(bible_word)
    if book_fullname is None or chapter_verse is None:
        return jsonify(result='Error')

    chapter = ChapterVerseExtractor.extract_chapter(chapter_verse)
    verses = ChapterVerseExtractor.extract_verses(chapter_verse)
    bible = Bible(book_fullname, chapter, verses, chapter_verse)

    for version in version_list:
        text = query_with_version[version].get_text(bible)
        bible.add_text(version, text)
    content = bible.get_print_str(version_list, False, b_remove_annotation)

    for version in version_list:
        query_with_version[version].close_connection()

    return jsonify(result=content)
    
@app.route('/_build_pptx_file')
def build_pptx_file():
    version_list = [KOR_BIBLE, ENG_BIBLE]
    query_with_version = {}
    query_with_version[KOR_BIBLE] = Execution(KOR_BIBLE)
    query_with_version[ENG_BIBLE] = Execution(ENG_BIBLE)

    bible_word = request.args.get('bible_word')
    b_remove_annotation = True if request.args.get('remove_annotation') == 'true' else False
    
    book_fullname, chapter_verse = decode_bible_word_form(bible_word)
    if book_fullname is None or chapter_verse is None:
        return send_from_directory(PPTX_FILES, PPTX_ERROR_FILE, as_attachment=True)

    chapter = ChapterVerseExtractor.extract_chapter(chapter_verse)
    verses = ChapterVerseExtractor.extract_verses(chapter_verse)
    bible = Bible(book_fullname, chapter, verses, chapter_verse)

    for version in version_list:
        text = query_with_version[version].get_text(bible)
        is_eng_bible = version == ENG_BIBLE
        bible.add_text(version, text, is_eng_bible)
    pptx_content = bible.get_pptx_content(version_list, b_remove_annotation)

    for version in version_list:
        query_with_version[version].close_connection()
        
    pptx_file = build_pptx(pptx_content)
    remove_old_pptx()
    return send_from_directory(PPTX_FILES, pptx_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
