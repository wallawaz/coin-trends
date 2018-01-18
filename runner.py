import argparse
from scraper.app import FourChanBoardScraper
from scraper.db import DBCreator
from scraper.scripts import get_tickers as gt

parser = argparse.ArgumentParser()
parser.add_argument(
    "action",
    help="action to perform",
    choices=["scrape", "create_db", "tickers"],
)
parser.add_argument()


parser.add_argument(
    "-b", "--board", help="name of 4chan board to scrape",
    default="biz",
)
parser.add_argument("--drop-first", action="store_true", default=False,
                    help="DROP ALL tables in sqlite db.")

args = parser.parse_args()

if __name__ == "__main__":
    if args.action == "scrape":
        app = FourChanBoardScraper(args.board)
    if args.action == "create_db":
        app.DBCreator(drop_first=args.drop_first)

    app.run()