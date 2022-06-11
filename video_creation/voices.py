from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track
from fifteen_api import FifteenAPI
from pydub import AudioSegment
import re
import os


def sanitize_text(reddit_obj):
    """
    Sanitizes the text for tts.
    What gets removed:
    - following characters`^_~@!&;#:-%“”‘"%*/{}[]()\|<>?=+`
    - any http or https links
    """

    # remove any urls from the text
    regex_urls = r"((http|https)://[^\s]+)"
    result = re.sub(regex_urls, " ", reddit_obj)

    # note: not removing apostrophes
    regex_expr = r"\s['|’]|['|’]\s|[\^_~@!&;#:\-%“”‘\"%\*/{}\[\]\(\)\\|<>=+]"
    result = re.sub(regex_expr, " ", result)

    # remove extra whitespace
    return " ".join(result.split())


def save_text_to_mp3(reddit_obj):
    """Saves Text to MP3 files.

    Args:
        reddit_obj : The reddit object you received from the reddit API in the askreddit.py file.
    """
    print_step("Saving Text to MP3 files...")
    length = 0

    tts_api = FifteenAPI()

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    thread_title = sanitize_text(reddit_obj["thread_title"])
    tts_api.save_to_file("Rise Kujikawa",thread_title, "assets/mp3/title.wav")
    AudioSegment.from_wav("assets/mp3/title.wav").export("assets/mp3/title.mp3", format="mp3")
    os.remove("assets/mp3/title.wav")
    length += MP3(f"assets/mp3/title.mp3").info.length

    try:
        Path(f"assets/mp3/posttext.mp3").unlink()
    except OSError as e:
        pass

    if reddit_obj["thread_post"] != "":
        thread_post = sanitize_text(reddit_obj["thread_post"])
        tts_api.save_to_file("Rise Kujikawa",thread_post, "assets/mp3/posttext.wav")
        AudioSegment.from_wav("assets/mp3/posttext.wav").export("assets/mp3/posttext.mp3", format="mp3")
        os.remove("assets/mp3/posttext.wav")
        length += MP3(f"assets/mp3/posttext.mp3").info.length

    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 50:
            break
        comment = sanitize_text(comment["comment_body"])
        tts_api.save_to_file("Rise Kujikawa",comment, f"assets/mp3/{idx}.wav")
        AudioSegment.from_wav(f"assets/mp3/{idx}.wav").export(f"assets/mp3/{idx}.mp3", format="mp3")
        os.remove(f"assets/mp3/{idx}.wav")
        length += MP3(f"assets/mp3/{idx}.mp3").info.length

    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
