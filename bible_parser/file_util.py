import shutil, errno
import codecs
import os

class FileUtil(object):
    @staticmethod
    def copy_directory(src_dir, dest_dir):
        try:
            shutil.copytree(src_dir, dest_dir)
        except OSError as exc:
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src_dir, dest_dir)
            else: 
                raise

    @staticmethod
    def zip_directory(src_dir, dest_file):
        shutil.make_archive(dest_file, 'zip', src_dir)

    @staticmethod
    def remove_directory(target_dir):
        shutil.rmtree(target_dir)

    @staticmethod
    def remove_file(target_file):
        os.remove(target_file)

    @staticmethod
    def rename_file(src_file, dest_file):
        shutil.move(src_file, dest_file)

    @staticmethod
    def copy_file(src_file, dest_file):
        shutil.copyfile(src_file, dest_file)

    @staticmethod
    def list_files_in_dir(target_dir):
        return os.listdir(target_dir)

    @staticmethod
    def read_file_content(filename):
        with codecs.open(filename, 'r', encoding='utf8') as f:
            return f.read()

        return None

    @staticmethod
    def read_binary_file(filename):
        with open(filename, 'rb') as f:
            return f.read()

        return None

    @staticmethod
    def write_file_content(content, filename):
        with codecs.open(filename, 'w', encoding='utf8') as f:
            f.write(content)

    @staticmethod
    def get_file_created_time(filename):
        return os.path.getmtime(filename)
