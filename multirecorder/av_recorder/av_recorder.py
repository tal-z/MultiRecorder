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
MONITOR_NAME = device_names["MONITOR_NAME"]

RECORD_MICROPHONE_COMMAND_ARGS = f'-f dshow -i audio="{MICROPHONE_NAME}" -thread_queue_size 512'
RECORD_SPEAKERS_COMMAND_ARGS = f'-f dshow -i audio="{SPEAKERS_NAME}" -thread_queue_size 512'
RECORD_WEBCAM_COMMAND_ARGS = F'-f dshow -i video="{WEBCAM_NAME}" -framerate 32 -thread_queue_size 512'
RECORD_MONITOR_COMMAND_ARGS = f'-f gdigrab -framerate 32 -thread_queue_size 512 -i {MONITOR_NAME}'


def record_av(audio_source, video_source, picture_in_picture_video_source='', picture_in_picture_scale=1, filename="output_file", duration=None):
    """
    Record audio and video from multiple sources, using FFmpeg.

    Parameters:
    - audio_source (str): Specifies the audio input source. Accepted values are 'speakers' or 'microphone'.
    - video_source (str): Specifies the video input source. Accepted values are 'monitor' or 'webcam'.
    - picture_in_picture_video_source (str, optional): Specifies the picture-in-picture video source.
      Accepted values are 'monitor' or 'webcam'. Default is an empty string (no picture-in-picture).
    - picture_in_picture_scale (float, optional): Specifies the scale factor for the picture-in-picture video.
      Default is 1.0 (no scaling).
    - filename (str, optional): Specifies the output filename without extension. Default is "output_file".
    - duration (float, optional): Specifies the recording duration in seconds. Default is None (no time limit).

    Raises:
    - AVException: If the input sources or their values are not recognized or specified incorrectly.

    Note:
    - The function uses FFmpeg to record audio and video, with optional picture-in-picture.
    - The output file will be in AVI format with video codec libxvid and audio codec aac.

    Example:
    ```python
    record_av(audio_source='speakers', video_source='monitor', picture_in_picture_video_source='webcam', duration=60)
    ```

    """
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

        if picture_in_picture_video_source.lower() in {"m", "monitor", "d", "desktop"}:
            picture_in_picture_video_command_args = RECORD_MONITOR_COMMAND_ARGS
            scale_factor = 10 / picture_in_picture_scale
            scale = f"iw/{scale_factor}:ih/{scale_factor}"

        elif picture_in_picture_video_source.lower() in {"c", "camera", "w", "webcam"}:
            picture_in_picture_video_command_args = RECORD_WEBCAM_COMMAND_ARGS
            scale_factor = 1 / picture_in_picture_scale
            scale = f"iw/{scale_factor}:ih/{scale_factor}"

        elif not picture_in_picture_video_source:
            picture_in_picture_video_command_args = ""

        else:
            raise AVException("picture_in_picture_video_source input not recognized. Accepted values include 'monitor' and 'webcam'")

        filter_args = (
            (
                f'-filter_complex "[1:v]scale={scale} [overlay]'
                f';[0:v][overlay]overlay=W-w-10:H-h-10[v01];[2:a]aformat=sample_fmts=fltp:channel_layouts=stereo '
                '[a];[a][2:a]amerge=inputs=2[aout]" -map "[v01]" -map "[aout]"'
            )
            if picture_in_picture_video_command_args
            else ''
        )

        duration_args = f"-t {duration}" if duration else ""

        command = (
            'ffmpeg',
            video_command_args,
            picture_in_picture_video_command_args,
            audio_command_args,
            '-c:v libxvid -q:v 0',  # specifies video codec
            '-c:a aac -strict experimental -b:a 192k',  # specifies audio codec
            filter_args,
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
        audio_source="m",
        video_source="w",
        picture_in_picture_video_source="m",
        filename=f"recording_{now}",
        duration=5
    )
