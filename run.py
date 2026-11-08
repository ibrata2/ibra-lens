import sys

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--selftest":
        from ibralens.selftest import main
        sys.exit(main(sys.argv[2]))
    from ibralens.ui import run
    run()
