import csv, sqlite3


def main():
    con = sqlite3.connect("dick_or_don.db")
    cur = con.cursor()

    with open('dick_or_don.csv') as fin:
        # csv.DictReader uses first line in file for column headings by default
        dr = csv.DictReader(fin) # comma is default delimiter
        to_db = [(i['quote'], i['utterer']) for i in dr]

    cur.executemany("INSERT OR IGNORE INTO quotes (quote, utterer) VALUES (?, ?);", to_db)
    con.commit()
    con.close()


if __name__ == "__main__":
    main()