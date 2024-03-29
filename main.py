import pandas as pd
import logging
import argparse

from pathlib import Path
from py_pdf_parser.loaders import load_file

logger = logging.getLogger('TBC_Statement')
logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)

arg_parser = argparse.ArgumentParser(description="TBC Bank Statements Parser")
arg_parser.add_argument('--input_file', type=Path, help='Statement PDF File to parse', required=True)
arg_parser.add_argument('--output_file', type=Path, help='path to parquet file to save', required=True)
args = arg_parser.parse_args()

document = load_file(args.input_file)

txt = "თარიღი\nDate"
els = document.elements.filter_by_text_contains(txt)

def by_row(row):
    rows = document.elements.below(row)
    container = []
    for row in rows:
        obj = {}
        row_text = row.text()
        logger.debug("|+| %s [%s]" % (row.text(), row.bounding_box))
        belows = document.elements.below(row)
        for below in belows:
            if below in rows:
                break
            row_text += below.text()
            logger.debug(f"\t|.| B: {below.text()} [{below.bounding_box}]")
        for eel in document.elements.to_the_right_of(row):
            logger.debug(f"\t|-> R: {eel.text()} [{eel.bounding_box}]")
            if eel.bounding_box.x0 > 660 and eel.bounding_box.x0 < 700:
                obj['spent'] = float(eel.text())
            if eel.bounding_box.x0 > 700 and eel.bounding_box.x0 < 760:
                obj['added'] = float(eel.text())
            if eel.bounding_box.x0 > 765:
                obj['total'] = float(eel.text())
            if eel.bounding_box.x0 < 430:
                obj['bank_desc'] = eel.text()
        obj['desc'] = row_text
        container.append(obj)
        logger.debug(obj)
        logger.debug("*"*10)
    return container

global_container = [i for el in els for i in by_row(el)]
logger.debug(global_container)

df = pd.DataFrame(global_container)
logger.info(df)

args.output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(args.output_file)