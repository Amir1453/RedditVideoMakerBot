from rich.console import Console
from utils.console import print_markdown, print_step, print_substep
from dotenv import load_dotenv

console = Console()
import os, random, praw, re

def has_integer(string):
    return any(char.isdigit() for char in string)


def get_subreddit_threads():
    global submission
    """
    Returns a list of threads from the AskReddit subreddit.
    """

    load_dotenv()

    if os.getenv("REDDIT_2FA", default="no").casefold() == "yes":
        print(
            "\nEnter your two-factor authentication code from your authenticator app.\n"
        )
        code = input("> ")
        print()
        pw = os.getenv("REDDIT_PASSWORD")
        passkey = f"{pw}:{code}"
    else:
        passkey = os.getenv("REDDIT_PASSWORD")

    content = {}
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="Accessing AskReddit threads",
        username=os.getenv("REDDIT_USERNAME"),
        password=passkey,
    )

    # If the user specifies that he doesnt want a random thread, or if he doesn't insert the "RANDOM_THREAD" variable at all, ask the thread link
    if not os.getenv("RANDOM_THREAD") or os.getenv("RANDOM_THREAD") == "no":
        print_substep("Insert the full thread link:", style="bold green")
        thread_link = input()
        print_step(f"Getting the inserted thread...")
        submission = reddit.submission(url=thread_link)
    else:
        # Otherwise, picks a random thread from the inserted subreddit
        if os.getenv("SUBREDDIT"):
            subreddit = reddit.subreddit(re.sub(r"r\/", "", os.getenv("SUBREDDIT")))
        else:
            # ! Prompt the user to enter a subreddit
            try:
                subreddit = reddit.subreddit(
                    re.sub(r"r\/", "",input("What subreddit would you like to pull from? "))
                )
            except ValueError:
                subreddit = reddit.subreddit("askreddit")
                print_substep("Subreddit not defined. Using AskReddit.")

        threads = subreddit.hot(limit=25)
        f1 = open("created.txt", "r")
        lines = f1.readlines()
        lines = [line.strip() for line in lines]
        for thread in threads:
            if thread.title not in lines:
                submission = thread
                break
        f1.close()
        f1 = open("created.txt", "a")
        f1.write(submission.title + "\n")
        f1.close()

    print_substep(f"Video will be: {submission.title} :thumbsup:")
    console.log("Getting video comments...")
    try:
        content["thread_url"] = submission.url
        content["thread_title"] = submission.title
        content["thread_post"] = submission.selftext
        content["comments"] = []

        for top_level_comment in submission.comments:
            if not top_level_comment.stickied and not top_level_comment.author == "AutoModerator" and len(top_level_comment.body) < 200 and len(top_level_comment.body) >= 5 and not has_integer(top_level_comment.body):
                content["comments"].append(
                    {
                        "comment_body": top_level_comment.body,
                        "comment_url": top_level_comment.permalink,
                        "comment_id": top_level_comment.id,
                    }
                )

    except AttributeError as e:
        pass
    print_substep("Received AskReddit threads successfully.", style="bold green")

    return content
