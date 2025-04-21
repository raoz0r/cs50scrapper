import sys
from .scrapper import fetch_and_parse
from .utils import dump_json

def main():
    if len(sys.argv) != 2:
        print("Usage: cs50scrapper <course_page_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    data = fetch_and_parse(url) # derive folder name from path segment after "cs50/" e.g. https://cs50.havard.edu/python/2022/weeks/0/ > python
    folder = url.split("/cs50/")[1].split("/")[0]
    dump_json(data, folder)
    print(f"> JSON written to cs50/{folder}/{data['title']}.json")

if __name__ == "__main__":
    main()