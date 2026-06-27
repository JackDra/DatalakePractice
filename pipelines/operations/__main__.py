import argparse

from operations import upload_sample


def main() -> None:
    parser = argparse.ArgumentParser(prog="operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    upload_parser = subparsers.add_parser(
        "upload-sample",
        help="Upload the local sample raw data files to ADLS.",
    )
    upload_parser.set_defaults(func=lambda _args: upload_sample.main())

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
