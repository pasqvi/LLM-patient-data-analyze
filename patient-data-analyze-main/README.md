
#- Per generare i datasets globali seguire la seguente guida scritta da Florian Monfort:

## Install

* Use a recent version of Python (3.12 recommended)
* Create a Python virtual environment: `python -m venv venv`
* Activate your virtual environment: `source ./venv/bin/activate`

## Computing data on patients

**NOTA BENE**: per generare il dataset usando PDD o DDD bisogna eseguire modifiche manualmente nel codice (alla riga 63 di ./src/compute_patient_data/compute_ouput_data.py è spiegato tutto). Per cambiare il nome del file generato recarsi alla riga 64 di ./src/utils/generate_datasheets.py .

* Install required dependencies: `pip install ".[compute]"` (or `python -m pip install ".[compute]"`)
* `python src/generate_datasheets.py -f <YOUR_DATA_FILE.xlsx> [-o <output_directory>]`
  * For example, with the provided training file: `python src/generate_datasheets.py -f "./data/V3 estrazione dati antiemicranici al 9-5-24 con PDD.xlsx"`

The generated datasheets will be in the `output` folder by default. Use `-o <path>` or `--output-dir <path>` to change output directory. The path is created if necessary.

Use `-g` (`--only-global`) to only output the datasheet for all drugs.

#- Per generare i datasets ad intervalli seguire invece quest'altra:




