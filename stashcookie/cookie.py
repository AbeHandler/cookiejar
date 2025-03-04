import argparse

def main():
    parser = argparse.ArgumentParser(description="A custom command for initialization.")
    parser.add_argument("init", type=str, help="Initialization argument")

    args = parser.parse_args()

    print(f"✅ Received argument: {args.init}")

if __name__ == "__main__":
    main()
