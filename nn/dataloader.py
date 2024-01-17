import psycopg2
import pandas as pd
import dataloader as dl
import random
from samples_dataset import SamplesDataset
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from tqdm.notebook import tqdm

quanti_cols_df_names = ['id', '_3_4_methylenedioxyethylamphetamine', '_3_4_methylene_dioxy_methylamphetamine', '_3_4_methylenedioxyphenylacetone', '_4f_mdmb_butinaca', '_5f_adb', '_5f_mdmb_pica', 'acetylcodeine', 'acetylthebaol', 'acide_4_hydroxybutanoique', 'acide_benzoique', 'acide_borique', 'adb_butinaca', 'amidon', 'aminopyrine', 'amoxycilline', 'amphetamine', 'benzocaine', 'benzoylecgonine', 'bicarbonate_de_sodium', 'bicarbonates', 'buprenorphine', 'cafeine', 'cannabidiol', 'cannabigerol', 'cannabinol', 'cis_cinnamoylcocaine', 'clonazepam', 'clotrimazole', 'cocaine', 'codeine', 'creatine', 'delta8_tetrahydrocannabinol', 'delta9_tetrahydrocannabinol', 'dextromethorphane', 'diametre', 'diltiazem', 'dimethylterephtalate', 'diphenydramine', 'ecgonidine', 'ecgoninemethylester', 'epaisseur', 'fub_amb', 'gammabutyrolactone', 'glucose', 'griseofulvine', 'guaifenesine', 'hauteur', 'heroine', 'hydroxyzine', 'ibuprofene', 'inositol', 'isoleucine', 'ketamine', 'lactitol', 'lactose', 'largeur', 'leucine', 'levamisole', 'lidocaine', 'longueur', 'maltose', 'mannitol', 'masse', 'mdmb_4en_pinaca', 'meconine', 'methamphetamine', 'methylecgonidine', 'monoacetylmorphine', 'morphine', 'nicotine', 'n_methyl_tryptamine', 'norcocaine', 'noscapine', 'o3_monoacetylmorphine_', 'o6_monoacetylmorphine', 'oxycodone', 'papaverine', 'paracetamol', 'phenacetine', 'piracetam', 'procaine', 'pv8', 'saccharose', 'sorbitol', 'talc', 'taux_cbd', 'taux_cbn', 'terephtalates', 'tetracaine', 'tramadol', 'trans_cinnamoylcocaine', 'tropacocaine', 'uree', 'valine', 'vanilline', 'id_lot']

quali_cols_df_names = ['abime', 'cbd', 'cbn', 'couleur', 'couleur_exterieur', 'couleur_exterieur_1', 'couleur_exterieur_2', 'couleur_interieur', 'description_de_l_objet', 'etiquette', 'forme', 'logo', 'nom_de_logo', 'numero_echantillon', 'ovule', 'presentation', 'secabilite_recto', 'secabilite_verso', 'type_drogue', 'visqueux']

def clean_samples(samples):
    empty_cols = samples.columns[(samples == 0).all()]
    clean_samples = samples.drop(columns=empty_cols)
    clean_samples = clean_samples.drop(columns=['id'])
    print(f'Cleaning samples columns : {len(empty_cols) + 2} columns dropped.')

    return clean_samples

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
    samples.drop(columns=['description_de_l_objet', 'nom_de_logo', 'numero_echantillon', ])

    # Quantitative columns
    quanti_cols = samples[quanti_cols_df_names].astype(float)
    
    # ----Normalize if needed
    if normalize:
        max_quanti_cols = quanti_cols.max()
        quanti_cols = quanti_cols.divide(max_quanti_cols)

    quanti_cols = quanti_cols.fillna(value=0.0)
    quanti_cols = clean_samples(samples=quanti_cols)

    # Qualitative columns
    quali_cols = samples[quali_cols_df_names]
    quali_cols = quali_cols.replace(to_replace='Oui', value='1')
    quali_cols = quali_cols.replace(to_replace='Non', value='0')
    quali_cols = pd.get_dummies(quali_cols, drop_first=True, dtype=float)
    
    # Merge quantitative and qualitative
    samples = pd.merge(quali_cols, quanti_cols, left_index=True, right_index=True)


    # Subsampling data if needed
    if positive_examples_count != -1:
        samples = samples.iloc[:positive_examples_count, :]

    return samples


def load_samples_dataset(positive_examples_count=-1, drug_type=None):
    samples = load_samples(positive_examples_count=positive_examples_count, drug_type=drug_type)

    dataset_tuples = []
    ids = samples['id_lot'].unique()

    # Matrix without unnecessary columns.
    clean = samples.drop(columns=['id_lot'])

    print('Creating positive examples.')
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

    dataset_size = len(dataset_tuples)
    counter_examples = []

    print('Creating negative examples.')
    for tuple_index in tqdm(range(len(dataset_tuples))):

        tuple = dataset_tuples[tuple_index]
        new_tuple = (tuple[0], dataset_tuples[random.randint(3, dataset_size - 1)][1], 1)

        while new_tuple in dataset_tuples:
            new_tuple = (tuple[0], dataset_tuples[random.randint(3, dataset_size - 1)][1], 1)

        new_tuple = (new_tuple[0], new_tuple[1], 0)
        counter_examples.append(new_tuple)

    dataset_tuples += counter_examples

    print(f'Dataset size : {len(dataset_tuples)}')

    return SamplesDataset(dataset_tuples)


def split_dataset(full_dataset, split_ratio=0.8):
    print(f'Spliting dataset. Ratio : {split_ratio}.')
    train_size = int(split_ratio * len(full_dataset))
    test_size = len(full_dataset) - train_size

    return random_split(full_dataset, [train_size, test_size])


def get_dataloaders(samples_count=-1, split_ratio=0.8, device=None):
    print(f'Creating dataset using {"all available" if samples_count == -1 else samples_count} samples.')
    samples_dataset = load_samples_dataset(size=samples_count)
    print(f'Dataset created : {len(samples_dataset)} examples ({samples_dataset.get_positive_examples_number()} positive examples, {samples_dataset.get_negative_examples_number()} nagative examples)')

    train_dataset, test_dataset = split_dataset(samples_dataset, split_ratio)

    train_dataloader = DataLoader(train_dataset, batch_size=64, shuffle=True, pin_memory=True)
    test_dataloader = DataLoader(test_dataset, batch_size=64, shuffle=True, pin_memory=True)

    print(f'Training dataset size : {len(train_dataloader.dataset)}. Testing dataset size : {len(test_dataloader.dataset)}.')

    if device != None:
        train_dataloader.to(device)
        test_dataset.to(device)

    return train_dataloader, test_dataloader