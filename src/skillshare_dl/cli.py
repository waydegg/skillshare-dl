import argparse

from .main import download


def main():
    parser = argparse.ArgumentParser(
        description="Download lessons from a Skillshare course."
    )
    parser.add_argument("url", type=str, help="A URL to a Skillshare lesson.")
    parser.add_argument(
        "access_token", type=str, help="An access token stored as a browser cookie."
    )
    parser.add_argument(
        "-d",
        "--download-dir",
        type=str,
        default="./",
        help="The directory where data should be downloaded. Defaults to a 'data' folder in the current directory.",
    )
    args = parser.parse_args()

    download(
        url=args.url, access_token=args.access_token, download_dir=args.download_dir
    )


if __name__ == "__main__":
    main()
