import subprocess
import re
import logging


def get_device_names():
    logging.info("Getting device names...")
    command = "ffmpeg -list_devices true -f dshow -i dummy"
    logging.debug(f"Running command: {command}")

    # Run the command and capture the output
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Check for errors
    if result.returncode != 0:
        logging.error(f"Error: {result.stderr}")
        return None

    result_str = str(result)

    # Use regular expressions to extract device names
    microphone_pattern = re.compile(r'] "(Microphone .*?)" \(audio\)')
    speakers_pattern = re.compile(r'] "(Stereo Mix .*?)" \(audio\)')
    webcam_pattern = re.compile(r'] "(.*?)" \(video\)')

    microphone_match = microphone_pattern.search(result_str)
    speakers_match = speakers_pattern.search(result_str)
    webcam_match = webcam_pattern.search(result_str)

    # Check if matches are found
    if microphone_match and speakers_match and webcam_match:
        microphone_name = microphone_match.group(1)
        speakers_name = speakers_match.group(1)
        webcam_name = webcam_match.group(1)

        logging.info(f"Microphone name: {microphone_name}")
        logging.info(f"Speakers name: {speakers_name}")
        logging.info(f"Webcam name: {webcam_name}")

        return {
            "MICROPHONE_NAME": microphone_name,
            "SPEAKERS_NAME": speakers_name,
            "WEBCAM_NAME": webcam_name
        }
    else:
        logging.warning("Device names not found in the output.")

