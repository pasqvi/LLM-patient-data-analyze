import pandas as pd

# Carica i dati dal file CSV
data = pd.read_csv('output_global_V3_DDD.csv')

# Combina le colonne "BASSA ADERENZA" e "INTERMEDIA ADERENZA"
data['BASSA ADERENZA'] = (data['BASSA ADERENZA'] | data['INTERMEDIA ADERENZA']).astype(int)

# Rimuovi la colonna "INTERMEDIA ADERENZA"
data.drop(columns='INTERMEDIA ADERENZA', inplace=True)

# Salva il nuovo file CSV con le modifiche
data.to_csv('V3_DDD_merged.csv', index=False)
