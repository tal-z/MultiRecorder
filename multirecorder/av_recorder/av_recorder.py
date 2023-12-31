import datetime
import logging
import subprocess

from multirecorder.utils.av_exceptions import AVException
from multirecorder.utils.get_device_names import get_device_names

logging.basicConfig(filename='av_record.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

device_names = get_device_names()

MICROPHONE_NAME = device_names["MICROPHONE_NAME"]
SPEAKERS_NAME = device_names["SPEAKERS_NAME"]
WEBCAM_NAME = device_names["WEBCAM_NAME"]

RECORD_SPEAKERS_COMMAND_ARGS = f'-f dshow -i audio="{SPEAKERS_NAME}"'
RECORD_MICROPHONE_COMMAND_ARGS = f'-f dshow -i audio="{MICROPHONE_NAME}"'
RECORD_MONITOR_COMMAND_ARGS = '-f gdigrab -framerate 30 -thread_queue_size 512 -i desktop'
RECORD_WEBCAM_COMMAND_ARGS = '-f dshow -i video="Logi C270 HD WebCam"'


def record_av(audio_source, video_source, filename="output_file", duration=None):
    try:
        if not audio_source or not video_source:
            raise AVException("Audio or video input source not specified")

        if audio_source.lower() in {"s", "speaker", "speakers"}:
            audio_command_args = RECORD_SPEAKERS_COMMAND_ARGS
        elif audio_source.lower() in {"m", "mic", "microphone"}:
            audio_command_args = RECORD_MICROPHONE_COMMAND_ARGS
        else:
            raise AVException("audio_source input not recognized. Accepted values include 'speakers' and 'microphone'")

        if video_source.lower() in {"m", "monitor", "d", "desktop"}:
            video_command_args = RECORD_MONITOR_COMMAND_ARGS
        elif video_source.lower() in {"c", "camera", "w", "webcam"}:
            video_command_args = RECORD_WEBCAM_COMMAND_ARGS
        else:
            raise AVException("video_source input not recognized. Accepted values include 'monitor' and 'webcam'")

        duration_args = f'-t {duration}' if duration else ''

        command = (
            'ffmpeg',
            video_command_args,
            audio_command_args,
            '-c:v libxvid -q:v 0',  # specifies video codec
            '-c:a aac -strict experimental -b:a 192k',  # specifies audio codec
            duration_args,
            f'{filename}.avi',
        )

        logging.info(f"Running command: {' '.join(command)}")

        subprocess.run(" ".join(command))
        logging.info(f"Recording completed successfully.")
    except AVException as e:
        logging.error(f"AVException occurred: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    now = datetime.datetime.now().strftime("%Y%m%dT%H%M")
    record_av(
        audio_source="s",
        video_source="m",
        filename=f"recording_{now}",
        duration=30
    )
