"""
Generate datasheets of computed data for each patient in the base file
"""

import argparse
import logging
import os
import time

import pandas

from compute_patient_data.compute_output_data import compute_dataframe_for_minsan
from utils.dir_path import dir_path


def getargs():
    """
    Define and parse command line arguments
    :return: command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f", "--file",
        required=True,
        type=argparse.FileType("r"),
        dest="input_file",
        metavar="<input data file>",
        help="Input patients datasheet file",
    )
    parser.add_argument(
        "-o", "--output-dir",
        required=False,
        type=dir_path,
        default=os.path.join(os.getcwd(), "output"),
        dest="output_directory",
        metavar="<output directory>",
        help="Output directory for computed datasheets",
    )
    parser.add_argument(
        "-g", "--only-global",
        action="store_false",
        dest="export_minsan_files",
        help="Also export a specific datasheet for each drug",
    )
    return parser.parse_args()


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    args = getargs()
    logger.info("Arguments parsed successfully.")

    # Read the input file
    input_data = pandas.read_excel(args.input_file.name, parse_dates=["DT_EROG", "DT_NAS"], date_format="%d/%m/%Y")
    input_data = input_data.sort_values(by='DT_EROG')
    logger.info("Input file read successfully.")

    # Compute resulting data and generate a CSV file for all drugs mixed
    logger.info("")
    start = time.time()
    output_data = compute_dataframe_for_minsan(input_data, mixed_minsan=True)
    output_file = os.path.join(args.output_directory, "output_global.csv")  #cambiare qui il nome del file di output (e.g. "output_global_PDD.csv")
    output_data.to_csv(output_file, index=False)
    end = time.time()
    logger.info(f"Output computed for all drugs in {round(end - start, 3)} s.")
    logger.info(f"Results written in {output_file}.")

    # Then do the same for each drug (MINSAN code) apart
    if args.export_minsan_files:
        for minsan_code in input_data["MINSAN"].unique():
            logger.info("")
            start = time.time()
            output_data = compute_dataframe_for_minsan(input_data[input_data["MINSAN"] == minsan_code])
            output_file = os.path.join(args.output_directory, f"output_{minsan_code}.csv")
            output_data.to_csv(output_file, index=False)
            end = time.time()
            logger.info(f"Output computed for {minsan_code} drug in {round(end - start, 3)} s.")
            logger.info(f"Results written in {output_file}.")
