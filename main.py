import time
import csv
from reviews import StoreReviews


def get_store_id(start, num):
    f = open("./data/store food.csv", "r+")
    csv.reader(f)
    fieldnames = [
        "store_id",
        "store_name",
        "city",
        "industry",
        "store_score",
    ]
    reader = csv.DictReader(f, fieldnames=fieldnames)
    count = 0
    header = True
    result = []
    for line in reader:

        if header:
            header = not header
            continue
        if start > 0:
            start -= 1
            continue
        result.append({"id": line["store_id"], "city": line["city"]})
        count += 1
        if count == num:
            print(f"end at store line {start + num}")
            break

    f.close()

    return result


if __name__ == "__main__":
    stores = get_store_id(0, 10)
    # stores = []
    #
    for store in stores:
        StoreReviews(store["id"], store["city"], "美食").run()
        time.sleep(10)
