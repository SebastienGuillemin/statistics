import psycopg2
import pandas as pd
import dataloader as dl
import random
from samples_dataset import SamplesDataset
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from tqdm.notebook import tqdm
import csv

quanti_cols_df_names = ['id', '_3_4_methylenedioxyethylamphetamine', '_3_4_methylene_dioxy_methylamphetamine', '_3_4_methylenedioxyphenylacetone', '_4f_mdmb_butinaca', '_5f_adb', '_5f_mdmb_pica', 'acetylcodeine', 'acetylthebaol', 'acide_4_hydroxybutanoique', 'acide_benzoique', 'acide_borique', 'adb_butinaca', 'amidon', 'aminopyrine', 'amoxycilline', 'amphetamine', 'benzocaine', 'benzoylecgonine', 'bicarbonate_de_sodium', 'bicarbonates', 'buprenorphine', 'cafeine', 'cannabidiol', 'cannabigerol', 'cannabinol', 'cis_cinnamoylcocaine', 'clonazepam', 'clotrimazole', 'cocaine', 'codeine', 'creatine', 'delta8_tetrahydrocannabinol', 'delta9_tetrahydrocannabinol', 'dextromethorphane', 'diametre', 'diltiazem', 'dimethylterephtalate', 'diphenydramine', 'ecgonidine', 'ecgoninemethylester', 'epaisseur', 'fub_amb', 'gammabutyrolactone', 'glucose', 'griseofulvine', 'guaifenesine', 'hauteur', 'heroine', 'hydroxyzine', 'ibuprofene', 'inositol', 'isoleucine', 'ketamine', 'lactitol', 'lactose', 'largeur', 'leucine', 'levamisole', 'lidocaine', 'longueur', 'maltose', 'mannitol', 'masse', 'mdmb_4en_pinaca', 'meconine', 'methamphetamine', 'methylecgonidine', 'monoacetylmorphine', 'morphine', 'nicotine', 'n_methyl_tryptamine', 'norcocaine', 'noscapine', 'o3_monoacetylmorphine_', 'o6_monoacetylmorphine', 'oxycodone', 'papaverine', 'paracetamol', 'phenacetine', 'piracetam', 'procaine', 'pv8', 'saccharose', 'sorbitol', 'talc', 'taux_cbd', 'taux_cbn', 'terephtalates', 'tetracaine', 'tramadol', 'trans_cinnamoylcocaine', 'tropacocaine', 'uree', 'valine', 'vanilline', 'id_lot']

quali_cols_df_names = ['abime', 'cbd', 'cbn', 'couleur', 'couleur_exterieur', 'couleur_exterieur_1', 'couleur_exterieur_2', 'couleur_interieur', 'etiquette', 'forme', 'logo', 'ovule', 'presentation', 'secabilite_recto', 'secabilite_verso', 'type_drogue', 'visqueux']

def clean_samples(samples):
    empty_cols = samples.columns[(samples == 0).all()]
    clean_samples = samples.drop(columns=empty_cols)
    clean_samples = clean_samples.drop(columns=['id'])
    print(f'Cleaning samples columns : {len(empty_cols) + 2} columns dropped.')

    return clean_samples

def process_quantiative_data(samples, normalize=True):
    # Quantitative columns
    quanti = samples[quanti_cols_df_names].astype(float)
    
    # ----Normalize if needed
    if normalize:
        max_quanti = quanti.max()
        quanti = quanti.divide(max_quanti)

    quanti = quanti.fillna(value=0.0)
    # quanti = clean_samples(samples=quanti)
    
    return quanti

def process_qualitative_data(samples):
    # Qualitative columns
    quali = samples[quali_cols_df_names]
    quali = quali.replace(to_replace='Oui', value='1')
    quali = quali.replace(to_replace='Non', value='0')
    quali = pd.get_dummies(quali, drop_first=True, dtype=float)
    quali = quali.replace(to_replace=1, value=0.5)
    
    return quali

def load_samples(positive_examples_count=-1, normalize=True, drug_type=None):
    # Loading data
    conn = psycopg2.connect(database="full_STUPS",
                            user="postgres",
                            host='localhost',
                            password="postgres",
                            port=5432)
    cur = conn.cursor()

    query =  '''select distinct ep.*, id_lot
                from echantillon_propriete ep
                    inner join echantillon e on e.id = ep.id
                    inner join composition c on c.id = e.id_composition
                    inner join lot_complet lc on (
                        lc.e1 = c.id
                        or lc.e2 = c.id
                    )'''
    
    if drug_type != None:
        query += f'WHERE type_drogue = \'{drug_type}\''

    cur.execute(query)

    samples = cur.fetchall()
    conn.commit()
    conn.close()
    colnames = [desc[0] for desc in cur.description]

    samples = pd.DataFrame(list(samples), columns=colnames)
    
    quanti = process_quantiative_data(samples=samples, normalize=normalize)
    quali = process_qualitative_data(samples=samples)
    
    # Merge quantitative and qualitative
    samples = pd.merge(quali, quanti, left_index=True, right_index=True)
    print(samples.shape)
    
    columns_names_1 = list(samples.columns)
    columns_names_1.remove('id_lot')
    columns_names_2 = list(map(lambda name: name + '_ech2', columns_names_1))

    columns_names = columns_names_1 + columns_names_2
    print(columns_names)
    print(len(columns_names))
    
    # Subsampling data if needed
    if positive_examples_count != -1:
        samples = samples.iloc[:positive_examples_count, :]

    return samples, columns_names

def create_positive_examples(samples):
    print('Creating positive examples.')
    dataset_tuples = []
    ids = samples['id_lot'].unique()
    print(f'{len(ids)} different ids.')

    # Matrix without unnecessary columns.
    clean = samples.drop(columns=['id_lot'])
    
    for id_index in tqdm(range(len(ids))):
        id = ids[id_index]
        batch_samples = list(clean.loc[samples['id_lot'] == id].itertuples(index=False, name=None))
        batch_samples_size = len(batch_samples)

        for i in range(0, batch_samples_size):
            sample1 = batch_samples[i]

            for j in range(0, batch_samples_size):
                if i != j:
                    sample2 = batch_samples[j]
                    dataset_tuples.append((sample1, sample2, 1))
                    
    return dataset_tuples

def create_negative_examples(dataset_tuples, replication_factor=2):
    print('Creating negative examples.')
    dataset_tuples_size = len(dataset_tuples)
    counter_examples = []

    print('Creating negative examples.')
    for tuple_index in tqdm(range(len(dataset_tuples))):
        for i in range(replication_factor):
            tuple = dataset_tuples[tuple_index]
            new_tuple = (tuple[0], dataset_tuples[random.randint(3, dataset_tuples_size - 1)][1], 1)

            while new_tuple in dataset_tuples:
                new_tuple = (tuple[0], dataset_tuples[random.randint(3, dataset_tuples_size - 1)][1], 1)

            new_tuple = (new_tuple[0], new_tuple[1], 0)
            counter_examples.append(new_tuple)

    dataset_tuples += counter_examples
    return dataset_tuples
    
def load_samples_dataset(positive_examples_count=-1, drug_type=None, export_as_csv=False, from_csv=False):
    dataset = None
    if not from_csv:
        samples, columns_names = load_samples(positive_examples_count=positive_examples_count, drug_type=drug_type)

        dataset_tuples = create_positive_examples(samples=samples)
        dataset_tuples = create_negative_examples(dataset_tuples=dataset_tuples)
        
        dataset = SamplesDataset(dataset_tuples, columns_names=columns_names)
        
        if export_as_csv:
            dataset.export_as_csv(path='../data/dataset.csv')
    else:
        dataset = SamplesDataset()
        dataset.load_csv(path='../data/dataset.csv')

    print(f'Dataset size : {len(dataset)}')
        
    return dataset
    
