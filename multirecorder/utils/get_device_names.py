import subprocess
import re
import logging
import os


def execute_ffmpeg_command(command):
    """
    Execute an FFmpeg command and return the result string.

    Parameters:
    - command (str): The FFmpeg command to be executed.

    Returns:
    - str or None: The result string if the command is successful, None otherwise.
    """
    logging.debug(f"Running command: {command}")

    # Run the command and capture the output
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Check for errors
    if result.returncode != 0:
        logging.error(f"Error: {result.stderr}")
        return None

    return str(result)


def extract_device_name(pattern, result_str, env_variable, device_type):
    """
    Extract a device name from the result string using a specified regex pattern.

    Parameters:
    - pattern (re.Pattern): The compiled regex pattern for matching the device name.
    - result_str (str): The result string obtained from FFmpeg command execution.
    - env_variable (str or None): The value of the device name from environment variable.
    - device_type (str): The type of the device (e.g., "Microphone", "Speakers", "Webcam").

    Returns:
    - str: The extracted device name.
    """
    match = pattern.search(result_str)
    if env_variable is None and match:
        device_name = match.group(1)
        logging.info(f"{device_type} name (from ffmpeg): {device_name}")
        return device_name
    else:
        logging.info(f"{device_type} name (from environment variable): {env_variable}")
        return env_variable


def get_monitor_name():
    """
    Get the name of the monitor for recording.

    The function checks if the environment variable 'MONITOR_NAME' is set. If set,
    it returns the specified monitor name. If not set, it defaults to 'desktop'.

    Returns:
    - str: The name of the monitor for recording.
    """
    # Check if an environment variable is set for the monitor name
    monitor_name = os.environ.get("MONITOR_NAME")

    if monitor_name:
        logging.info(f"Monitor name (from environment variable): {monitor_name}")
        return monitor_name
    else:
        # Default monitor name when the environment variable is not set
        default_monitor_name = "desktop"
        logging.info(f"Monitor name not specified. Using default: {default_monitor_name}")
        return default_monitor_name


def get_device_names():
    """
    Get device names for Microphone, Speakers, and Webcam.

    Returns:
    - dict: A dictionary containing device names for Microphone, Speakers, and Webcam.
    """
    logging.info("Getting device names...")

    # Check if environment variables are set for specific device names
    microphone_name = os.environ.get("MICROPHONE_NAME")
    speakers_name = os.environ.get("SPEAKERS_NAME")
    webcam_name = os.environ.get("WEBCAM_NAME")
    monitor_name = get_monitor_name()

    # Check if any of the specific device names are missing
    if None in (microphone_name, speakers_name, webcam_name):
        logging.warning("Some or all device names not found in environment variables. Using ffmpeg commands.")

        # Use ffmpeg commands to get the missing device names
        command = "ffmpeg -list_devices true -f dshow -i dummy"
        result_str = execute_ffmpeg_command(command)

        if result_str is not None:
            # Use regular expressions to extract device names
            microphone_pattern = re.compile(r'] "(Microphone .*?)" \(audio\)')
            speakers_pattern = re.compile(r'] "(Stereo Mix .*?)" \(audio\)')
            webcam_pattern = re.compile(r'] "(.*?)" \(video\)')

            # Update only the missing device names
            microphone_name = extract_device_name(microphone_pattern, result_str, microphone_name, "Microphone")
            speakers_name = extract_device_name(speakers_pattern, result_str, speakers_name, "Speakers")
            webcam_name = extract_device_name(webcam_pattern, result_str, webcam_name, "Webcam")

    return {
        "MICROPHONE_NAME": microphone_name,
        "SPEAKERS_NAME": speakers_name,
        "WEBCAM_NAME": webcam_name,
        "MONITOR_NAME": monitor_name,
    }
