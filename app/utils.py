import base64
import datetime
import os
import tempfile
import subprocess


def convert_bytes_to_megabytes(bytes_size):
    megabytes = bytes_size / (1024 * 1024)
    return "{:.1f}MB".format(megabytes)


def extract_thumbnail(video_path, time_in_seconds=10):
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        temp_file_path = temp_file.name
        subprocess.call(['ffmpeg', '-y', '-i', video_path, '-ss', '00:00:00.000', '-vframes', '1', temp_file_path])

        with open(temp_file_path, 'rb') as img_file:
            img_bytes = img_file.read()
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    return img_base64


def get_files_with_metadata(folder_path):
    files_with_metadata = []

    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                creation_time = datetime.datetime.fromtimestamp(file_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
                file_size_bytes = file_stat.st_size
                file_size_megabytes = convert_bytes_to_megabytes(file_size_bytes)
                metadata = {'title': filename, 'creation_date': creation_time, 'size': file_size_megabytes,
                            "thumbnail": extract_thumbnail(file_path), "file_path": file_path}
                files_with_metadata.append(metadata)
    except OSError as e:
        print(f"Error: {e}")

    return files_with_metadata
