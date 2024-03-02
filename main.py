test_file_path = "./test/statement-816879476-1.pdf"

from py_pdf_parser.loaders import load_file
from py_pdf_parser import tables

document = load_file(test_file_path)

txt = "თარიღი\nDate"
els = document.elements.filter_by_text_contains(txt)

def by_col(el):
    extended_headers = document.elements.to_the_right_of(el)
    for eh in [el] + list(extended_headers):
        print(f"COL: {eh.text()} [{eh.bounding_box}]")
        belows = document.elements.below(eh)
        print(f"+: {len(belows)} elements:")
        for b in belows:
            print(f"\t---- {b.text()} [{b.bounding_box}]")


def by_row(row):
    rows = document.elements.below(row)
    container = []
    for row in rows:
        obj = {}
        row_text = row.text()
        print("|+| %s [%s]" % (row.text(), row.bounding_box))
        belows = document.elements.below(row)
        for below in belows:
            if below in rows:
                print("GOTCHA!")
                break
            row_text += below.text()
            print(f"\t|.| B: {below.text()} [{below.bounding_box}]")
        for eel in document.elements.to_the_right_of(row):
            print(f"\t|-> R: {eel.text()} [{eel.bounding_box}]")
            if eel.bounding_box.x0 > 660 and eel.bounding_box.x0 < 700:
                obj['spent'] = eel.text()
            if eel.bounding_box.x0 > 700 and eel.bounding_box.x0 < 760:
                obj['added'] = eel.text()
            if eel.bounding_box.x0 > 765:
                obj['total'] = eel.text()
            if eel.bounding_box.x0 < 430:
                obj['bank_desc'] = eel.text()
        obj['desc'] = row_text
        print(obj)
        print("*"*10)

by_row(els[1])

print("ALL")