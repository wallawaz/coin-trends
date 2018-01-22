import argparse
from scraper.app import create_app
from scraper.four_chan import FourChanBoardScraper
from scraper.db import DBCreator
from scraper.scripts.get_tickers import TickerUpdater
from scraper.sentiment import SentimentApp

parser = argparse.ArgumentParser()
parser.add_argument(
    "action",
    help="action to perform",
    choices=["create_db", "sentiment", "serve", "scrape", "tickers"],
)
parser.add_argument(
    "-b", "--board", help="name of 4chan board to scrape",
    default="biz",
)
parser.add_argument("--drop-first", action="store_true", default=False,
                    help="DROP ALL tables in sqlite db.")

args = parser.parse_args()

if __name__ == "__main__":
    if args.action == "scrape":
        _app = FourChanBoardScraper(args.board)
    if args.action == "create_db":
        _app = DBCreator(drop_first=args.drop_first)
    if args.action == "tickers":
        _app = TickerUpdater()
    if args.action in ("sentiment", "serve"):
        _app = SentimentApp()
    
    if args.action == "serve":
        _app.connect_to_db()
        app = create_app(_app)

    else:
        app = _app
    
    app.run()