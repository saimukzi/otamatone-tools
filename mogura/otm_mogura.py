import argparse
import runtime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?')
    parser.add_argument('--speed', default=0, type=int)
    args = parser.parse_args()

    runtime.run(**vars(args))


if __name__=="__main__":
    main()
