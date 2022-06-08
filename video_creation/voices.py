from gtts import gTTS
from pathlib import Path
from mutagen.mp3 import MP3
from utils.console import print_step, print_substep
from rich.progress import track
import re


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

    # Create a folder for the mp3 files.
    Path("assets/mp3").mkdir(parents=True, exist_ok=True)

    thread_title = sanitize_text(reddit_obj["thread_title"])
    tts = gTTS(text=thread_title, lang="en", slow=False)
    tts.save(f"assets/mp3/title.mp3")
    length += MP3(f"assets/mp3/title.mp3").info.length

    try:
        Path(f"assets/mp3/posttext.mp3").unlink()
    except OSError as e:
        pass

    if reddit_obj["thread_post"] != "":
        thread_post = sanitize_text(reddit_obj["thread_post"])
        tts = gTTS(text=thread_post, lang="en", slow=False)
        tts.save(f"assets/mp3/posttext.mp3")
        length += MP3(f"assets/mp3/posttext.mp3").info.length

    for idx, comment in track(enumerate(reddit_obj["comments"]), "Saving..."):
        # ! Stop creating mp3 files if the length is greater than 50 seconds. This can be longer, but this is just a good starting point
        if length > 50:
            break
        comment = sanitize_text(comment["comment_body"])
        tts = gTTS(text=comment, lang="en", slow=False)
        tts.save(f"assets/mp3/{idx}.mp3")
        length += MP3(f"assets/mp3/{idx}.mp3").info.length

    print_substep("Saved Text to MP3 files successfully.", style="bold green")
    # ! Return the index so we know how many screenshots of comments we need to make.
    return length, idx
