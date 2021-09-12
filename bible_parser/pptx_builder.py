from copy import deepcopy
from bible_parser.file_util import FileUtil
import os
import time


PPTX_DATA_DIR = "./data/pptx"
PPTX_DATA_BASE = f"{PPTX_DATA_DIR}/base"
PPTX_DATA_TEMPLATES = f"{PPTX_DATA_DIR}/templates"
PPTX_DATA_FILES = f"{PPTX_DATA_DIR}/files"
PPTX_DATA_ERROR_FILE = f"{PPTX_DATA_DIR}/files/error.pptx"

PPTX_OUTPUT_DIR = "./output"

REPLACEMENT_POS = "replacement_position"


class PPTXBuilder(object):
	@classmethod
	def build(cls, book_kor, book_eng, chapter_verse, text_list):
		if text_list is None or len(text_list) <= 0:
			return PPTX_DATA_ERROR_FILE

		output_filename = str(time.time())
		working_dir = f"{PPTX_OUTPUT_DIR}/{output_filename}"

		FileUtil.copy_directory(PPTX_DATA_BASE, working_dir)

		no_slides = len(text_list)

		content_types_content = cls.build_content_types(no_slides)
		FileUtil.write_file_content(content_types_content, f"{working_dir}/[Content_Types].xml")

		presentation_content = cls.build_presentation(no_slides)
		FileUtil.write_file_content(presentation_content, f"{working_dir}/ppt/presentation.xml")

		presentation_rels_content = cls.build_presentation_rels(no_slides)
		FileUtil.write_file_content(presentation_rels_content, f"{working_dir}/ppt/_rels/presentation.xml.rels")

		base_slide_info = {
			'book_kor': book_kor,
			'book_eng': book_eng,
			'chapter_verse': chapter_verse,
		}
		for idx, curr_text_info in enumerate(text_list):
			slide_info = deepcopy(base_slide_info)
			slide_info['text_kor'] = curr_text_info['text_kor']
			slide_info['text_eng'] = curr_text_info['text_eng']
			slide_content = cls.build_slide(**slide_info)

			slide_filename = f"{working_dir}/ppt/slides/slide{(idx + 1)}.xml"
			FileUtil.write_file_content(slide_content, slide_filename)

			FileUtil.copy_file(f"{PPTX_DATA_TEMPLATES}/ppt/slides/_rels/slide.xml.rels", f"{working_dir}/ppt/slides/_rels/slide{(idx + 1)}.xml.rels")

		FileUtil.remove_file(f"{working_dir}/ppt/_rels/.keep")
		FileUtil.remove_file(f"{working_dir}/ppt/slides/_rels/.keep")

		FileUtil.zip_directory(working_dir, working_dir)
		FileUtil.remove_directory(working_dir)

		chapter_verse_filename = chapter_verse.replace(':', '_')
		output_filename = f"{book_eng} {chapter_verse_filename}.pptx"
		output_full_path = f"{PPTX_OUTPUT_DIR}/{output_filename}"
		FileUtil.rename_file(f"{working_dir}.zip", output_full_path)

		return output_filename

	@classmethod
	def build_content_types(cls, no_slides):
		content = ""
		for index in range(0, no_slides):
			content += f"""<Override ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml" PartName="/ppt/slides/slide{(index + 1)}.xml"/>"""

		content_types_filename = f"{PPTX_DATA_TEMPLATES}/[Content_Types].xml"
		content_types_content = FileUtil.read_file_content(content_types_filename)

		return content_types_content.replace(REPLACEMENT_POS, content)

	@classmethod
	def build_presentation(cls, no_slides):
		content = "<p:sldIdLst>"
		for index in range(0, no_slides):
			content += f"""<p:sldId r:id="rId{(index + 11)}" id="{(index + 256)}"/>"""
		content += "</p:sldIdLst>"

		presentation_filename = f"{PPTX_DATA_TEMPLATES}/ppt/presentation.xml"
		presentation_content = FileUtil.read_file_content(presentation_filename)

		return presentation_content.replace(REPLACEMENT_POS, content)

	@classmethod
	def build_presentation_rels(cls, no_slides):
		content = ""
		for index in range(0, no_slides):
			content += f"""<Relationship Target="slides/slide{(index + 1)}.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Id="rId{(index + 11)}"/>"""

		presentation_rels_filename = f"{PPTX_DATA_TEMPLATES}/ppt/_rels/presentation.xml.rels"
		presentation_rels_content = FileUtil.read_file_content(presentation_rels_filename)

		return presentation_rels_content.replace(REPLACEMENT_POS, content)

	@classmethod
	def build_slide(cls, book_kor, book_eng, chapter_verse, text_kor, text_eng):
		slide_template_filename = f"{PPTX_DATA_TEMPLATES}/ppt/slides/slide.xml"
		slide_template = FileUtil.read_file_content(slide_template_filename)

		book_kor_replaced = slide_template.replace("book_kor", book_kor)
		book_eng_replaced = book_kor_replaced.replace("book_eng", book_eng)

		chapter_verse_replaced = book_eng_replaced.replace("chapter_verse", chapter_verse)

		text_kor_replaced = chapter_verse_replaced.replace("text_kor", text_kor)
		text_eng_replaced = text_kor_replaced.replace("text_eng", text_eng)

		return text_eng_replaced


if __name__ == '__main__':
	book_kor = "잠언"
	book_eng = "Proverbs"
	chapter_verse = "18:12,13"
	text_list = [
		{
			'text_kor': "12. 사람의 마음의 교만은 멸망의 선봉이요 겸손은 존귀의 길잡이니라",
			'text_eng': "12. Before a downfall the heart is haughty, but humility comes before honor.",
		},
		{
			'text_kor': "13. 사연을 듣기 전에 대답하는 자는 미련하여 욕을 당하느니라",
			'text_eng': "13. To answer before listening- that is folly and shame.",
		},
	]

	result = PPTXBuilder.build_slide(
		book_kor=book_kor,
		book_eng=book_eng,
		chapter_verse=chapter_verse,
		text_kor=text_list[0]['text_kor'],
		text_eng=text_list[0]['text_eng'],
	)

	print(result)

	output_filename = PPTXBuilder.build(
		book_kor=book_kor,
		book_eng=book_eng,
		chapter_verse=chapter_verse,
		text_list=text_list,
	)

	print(output_filename)
