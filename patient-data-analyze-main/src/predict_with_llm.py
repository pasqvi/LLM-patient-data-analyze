import argparse
import json
import logging
import os

import torch
from datasets import Dataset
from peft import PeftModel

from constants import BASE_MODEL_ID, FINETUNED_MODEL_ID
from predict_patient_data.generate_prediction_prompt import generate_prediction_prompt
from predict_patient_data.load_model_config import load_model_config
from predict_patient_data.load_tokenizer import load_tokenizer
from predict_patient_data.retrieve_output_data import retrieve_output_data


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
        help="Generated datasheet file (with patient adherence, shift and follow-up persistence)",
    )
    return parser.parse_args()


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    args = getargs()
    logger.info("Arguments parsed successfully.")

    # Retrieve the output data as a dataframe with unused columns filtered out
    output_data = retrieve_output_data(args.input_file)
    logger.info("Output file loaded successfully.")

    # Convert the pandas dataframe into a pytorch tensor
    dataset = Dataset.from_pandas(output_data)

    # Load the model from the base model ID and the PEFT result
    model = load_model_config(BASE_MODEL_ID)
    model = PeftModel.from_pretrained(model, FINETUNED_MODEL_ID)

    # Load the tokenizer
    tokenizer = load_tokenizer(FINETUNED_MODEL_ID, local_files_only=True)
    logger.info("Model and tokenizer loaded successfully.")

    # Make predictions with the fine-tuned model
    model.eval()
    with torch.no_grad():
        for i, patient in enumerate(dataset):
            patient_input = generate_prediction_prompt(patient)
            model_input = tokenizer(patient_input, return_tensors="pt").to("cuda")
            result = tokenizer.decode(model.generate(**model_input, max_new_tokens=512)[0], skip_special_tokens=True)
            print(result)  # Stampa il risultato direttamente
