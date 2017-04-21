"""
entry point
"""
import sys
from dotenv import load_dotenv, find_dotenv
from .bot import PSBot

def main():
    """main"""

    load_dotenv(find_dotenv())

    try:
        bot = PSBot()
        bot.start()
    except KeyboardInterrupt:
        bot.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
