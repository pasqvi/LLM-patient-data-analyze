import pandas as pd


def rimuovi_righe_da_csv(n):
    # Percorso del file CSV fisso
    file_csv = './output_global.csv'

    # Legge il file CSV in un DataFrame
    df = pd.read_csv(file_csv)

    # Controlla che n non sia maggiore del numero totale di righe
    if n >= len(df):
        print("Errore: il numero di righe da rimuovere è maggiore o uguale al numero totale di righe nel file.")
        return

    # Rimuove le ultime n righe
    df = df.iloc[:-n]

    # Sovrascrive il file originale con il DataFrame aggiornato
    df.to_csv(file_csv, index=False)
    print(f"Sono state rimosse le ultime {n} righe dal file '{file_csv}'.")

# Esempio di utilizzo
rimuovi_righe_da_csv(130)  # Sostituisci `n` con il numero di righe da rimuovere
