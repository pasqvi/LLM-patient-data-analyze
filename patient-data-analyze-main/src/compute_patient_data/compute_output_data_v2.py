import pandas as pd
from datetime import timedelta

#V3 estrazione dati antiemicranici al 9-5-24 con PDD.xlsx     Z2 estrazione dati antiemicranici 10-5-24 - 19-9-24 - con PDD - per invio.adjusted.xls


def generate_datasheets(frequenza):

    # Caricamento del file Excel
    file_path = '../data/V3 estrazione dati antiemicranici al 9-5-24 con PDD.xlsx'  #cambiare il nome del file qui (alla riga 4 ci sono i due file per fare copia e incolla)

    if file_path.endswith('.xlsx'):
        data = pd.read_excel(file_path)
    else:
        data = pd.read_excel(file_path, parse_dates=['DT_EROG'], engine='xlrd')

    # Funzione per calcolare la data di fine intervallo basata sui giorni per mese
    def calculate_end_date(start_date, days_per_month):
        match frequenza:
            case '3ME':
                return start_date + timedelta(days=days_per_month * 3)
            case '6ME':
                return start_date + timedelta(days=days_per_month * 6)
            case '9ME':
                return start_date + timedelta(days=days_per_month * 9)
            case '12ME':
                return start_date + timedelta(days=days_per_month * 12)

    # (1 mese = 30 giorni) arrotondo per eccesso i pazienti del tipo 1 mese = 28 giorni
    days_in_month = 30
    data['end_date'] = data['DT_EROG'].apply(lambda x: calculate_end_date(x, days_in_month))

    # Ordino i dati per paziente e data di erogazione
    data_sorted = data.sort_values(by=['CODICE PAZIENTE UNIVOCO', 'DT_EROG'])

    # Creo una colonna per identificare il farmaco precedentemente usato per ciascun paziente
    data_sorted['previous_minsan'] = data_sorted.groupby('CODICE PAZIENTE UNIVOCO')['MINSAN'].shift(1)

    # Controllo se c'è stato un cambio di farmaco
    data_sorted['is_shift'] = (data_sorted['MINSAN'] != data_sorted['previous_minsan']).astype(int)

    # Calcolo i cambiamenti all'interno di ogni intervallo di x mesi
    shifts_per_interval = data_sorted.groupby(['CODICE PAZIENTE UNIVOCO', pd.Grouper(key='DT_EROG', freq=frequenza)])['is_shift'].sum().reset_index()
    shifts_per_interval.columns = ['CODICE PAZIENTE UNIVOCO', 'Inizio Intervallo', 'SHIFT']

    # Eseguo raggruppamento per paziente e intervallo di x mesi
    grouped_data = data_sorted.groupby(['CODICE PAZIENTE UNIVOCO', 'SESSO', 'DT_NAS', 'COMUNE NASCITA', 'COMUNE_RESIDENZA',pd.Grouper(key='DT_EROG', freq=frequenza)])


    summed_data = grouped_data['mg tot erogati'].sum().reset_index()
    summed_data.columns = ['CODICE PAZIENTE UNIVOCO', 'SESSO', 'DT_NAS', 'COMUNE NASCITA', 'COMUNE RESIDENZA','Inizio Intervallo', 'mg tot assunti']

    def months_for_frequency(frequenza):
        match frequenza:
            case '3ME':
                return 3
            case '6ME':
                return 6
            case '9ME':
                return 9
            case '12ME':
                return 12

    # Calcolo delle date di fine intervallo
    months = months_for_frequency(frequenza)
    summed_data['Fine Intervallo'] = summed_data['Inizio Intervallo'] + pd.DateOffset(months=months) - pd.DateOffset(days=1)

    # Aggrego la colonna SHIFT
    summed_data_with_shifts = pd.merge(summed_data, shifts_per_interval,on=['CODICE PAZIENTE UNIVOCO', 'Inizio Intervallo'], how='left')

    # Calcolo del max_delivery_date, ovvero l'ultima data di erogazione tra tutti i pazienti
    max_delivery_date = data_sorted['DT_EROG'].max()

    # Trovo il last_delivery_qta per ogni paziente e intervallo di x mesi
    last_delivery_data = data_sorted.groupby(['CODICE PAZIENTE UNIVOCO', pd.Grouper(key='DT_EROG', freq=frequenza)])['QTA'].last().reset_index()
    last_delivery_data.columns = ['CODICE PAZIENTE UNIVOCO', 'Inizio Intervallo', 'last_delivery_qta']

    # Aggiungo temporanenamente la colonna del last_delivery_qta
    summed_data_full = pd.merge(summed_data_with_shifts, last_delivery_data,on=['CODICE PAZIENTE UNIVOCO', 'Inizio Intervallo'], how='left')

    # Aggiungo la colonna PRIMO PRODOTTO ASSUNTO
    first_minsan = data_sorted.groupby('CODICE PAZIENTE UNIVOCO')['MINSAN'].first().reset_index()
    first_minsan.columns = ['CODICE PAZIENTE UNIVOCO', 'PRIMO PRODOTTO ASSUNTO']
    summed_data_full = pd.merge(summed_data_full, first_minsan, on='CODICE PAZIENTE UNIVOCO', how='left')

    # Funzione per calcolare il numeratore dell'aderenza
    def calculate_adherence_numerator_pdd(group):
        if len(group) > 1:
            return group["giorni di terapia reali (PDD)"][:-1].sum()
        else:
            return 0


    def calculate_adherence_numerator_ddd(group):
        if len(group) > 1:
            return group["giorni terapia teorici (DDD)"][:-1].sum()
        else:
            return 0

    # Funzione per calcolare il denominatore dell'aderenza
    def calculate_adherence_denominator(first_delivery_date, last_delivery_date):
        return (last_delivery_date - first_delivery_date).days


    # Calcolo dell'aderenza per ciascun paziente
    adherence_list = []

    for _, group in data_sorted.groupby(['CODICE PAZIENTE UNIVOCO', pd.Grouper(key='DT_EROG', freq=frequenza)]):
        adherence_numerator = calculate_adherence_numerator_pdd(group)  # Cambiare pdd con ddd a seconda del tipo di calcolo che si vuole
        adherence_denominator = calculate_adherence_denominator(group['DT_EROG'].min(), group['DT_EROG'].max())

        if adherence_denominator > 0:
            adherence = round(100 * (adherence_numerator / adherence_denominator), 2)
        else:
            adherence = None  # Per evitare le divisioni per zero

        adherence_list.append(adherence)

    # Aggiungo la colonna aderenza
    summed_data_full['ADERENZA'] = adherence_list


    # Funzione per calcolare Follow Up Persistence
    def calculate_follow_up_persistence(row, max_date):
        interval_days = (max_date - row['Fine Intervallo']).days
        if interval_days > 30 * (1 + row['last_delivery_qta']):
            return 1
        else:
            return 0


    summed_data_full['Follow Up Persistence'] = summed_data_full.apply(lambda row: calculate_follow_up_persistence(row, max_delivery_date), axis=1)

    summed_data_full['ADERENZA'] = pd.Series(adherence_list)

    summed_data_full["BASSA ADERENZA"] = (summed_data_full['ADERENZA'] < 40).astype(int)
    summed_data_full["INTERMEDIA ADERENZA"] = ((40 <= summed_data_full['ADERENZA']) & (summed_data_full['ADERENZA'] < 80)).astype(int)
    summed_data_full["ALTA ADERENZA"] = (summed_data_full['ADERENZA'] >= 80).astype(int)


    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
    # Nel caso si volessero aggiungere nuove colonne al datasheet, inserire qui dentro.
    # Dopodichè modificare il codice per il calcolo della media (Aggiungi le nuove colonne che devono rimanere vuote)

    # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

    # Calcolo dei valori medi di SHIFT, ADERENZA, e Follow Up Persistence (arrotondati alla seconda cifra decimale)
    mean_shift = round(summed_data_full['SHIFT'].mean(), 2)
    mean_adherence = round(summed_data_full['ADERENZA'].mean(), 2)
    mean_follow_up = round(summed_data_full['Follow Up Persistence'].mean(), 2)


    # Creo riga con i valori medi e celle vuote per colmare
    mean_row = pd.DataFrame({
        'SHIFT': [mean_shift],
        'ADERENZA': [mean_adherence],
        'Follow Up Persistence': [mean_follow_up],
        'CODICE PAZIENTE UNIVOCO': ['VALORI MEDI'],
        'SESSO': [''], 'DT_NAS': [''], 'COMUNE NASCITA': [''], 'COMUNE RESIDENZA': [''],
        'Inizio Intervallo': [None], 'Fine Intervallo': [None], 'mg tot assunti': [None],
        'PRIMO PRODOTTO ASSUNTO': [''], 'BASSA ADERENZA' : [''], 'INTERMEDIA ADERENZA' : [''], 'ALTA ADERENZA' : ['']
    })

    # Aggiungo la riga dei valori medi al DataFrame
    summed_data_full = pd.concat([summed_data_full, mean_row], ignore_index=True)

    """Nel caso si volessero i risultati di shift e follow up come interi, decommentare:"""
    #summed_data_full['SHIFT'] = summed_data_full['SHIFT'].astype(int, errors='ignore')
    #summed_data_full['Follow Up Persistence'] = summed_data_full['Follow Up Persistence'].astype(int, errors='ignore')

    # Rimuovo le colonne non necessarie dal DataFrame prima di salvare il file finale
    final_data = summed_data_full.drop(['last_delivery_qta'], axis=1)


    # Commentare per eliminare il filtro delle righe con aderenza >= 560
    unacceptable_rows_indices = final_data[final_data["ADERENZA"] >= 560].index
    final_data.drop(unacceptable_rows_indices, inplace=True)

    # Salvataggio del file finale
    final_output_cleaned_file_path = f'../output/output_{frequenza}_PDD.csv'
    final_data.to_csv(final_output_cleaned_file_path, index=False)
