from compute_patient_data.compute_output_data_v2 import *
import warnings
import time


warnings.filterwarnings('ignore')

start = time.time()
generate_datasheets('3ME')
generate_datasheets('6ME')
generate_datasheets('9ME')
generate_datasheets('12ME')
end = time.time()

print(f"Generazione datasheets completata in: {round(end - start, 3)} secondi.")

