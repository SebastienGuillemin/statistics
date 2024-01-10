import psycopg2
import pandas as pd
import dataloader as dl
import random
from samples_dataset import SamplesDataset
from torch.utils.data import DataLoader
from torch.utils.data import random_split
from tqdm.notebook import tqdm


def load_samples(subsample_size=-1):
    # Loading data
    conn = psycopg2.connect(database="full_STUPS",
                            user="postgres",
                            host='localhost',
                            password="postgres",
                            port=5432)
    cur = conn.cursor()
    cur.execute('''select distinct ep.id, _3_4_methylenedioxyethylamphetamine, _3_4_methylene_dioxy_methylamphetamine, _5f_adb, _5f_mdmb_pica, acide_4_hydroxybutanoique, adb_butinaca, amphetamine, buprenorphine, cafeine, cannabidiol, cannabinol, clonazepam, cocaine, delta8_tetrahydrocannabinol, delta9_tetrahydrocannabinol, diametre, epaisseur, fub_amb, gammabutyrolactone, hauteur, heroine, ketamine, largeur, levamisole, lidocaine, longueur, masse, mdmb_4en_pinaca, methamphetamine, morphine, noscapine, o6_monoacetylmorphine, paracetamol, phenacetine, procaine, id_lot
                from echantillon_propriete ep
                inner join echantillon e on e.id = ep.id
                inner join composition c on c.id = e.id_composition
                inner join lot_complet lc on (lc.e1 = c.id or lc.e2 = c.id)
                order by id_lot''')

    samples = cur.fetchall()
    conn.commit()
    conn.close()
    colnames = [desc[0] for desc in cur.description]

    samples = pd.DataFrame(list(samples), columns=colnames)

    # Transforming None values to 0.0 for quantitative columns.
    quanti = samples[['_3_4_methylenedioxyethylamphetamine', '_3_4_methylene_dioxy_methylamphetamine', '_5f_adb', '_5f_mdmb_pica', 'acide_4_hydroxybutanoique', 'adb_butinaca', 'amphetamine', 'buprenorphine', 'cafeine', 'cannabidiol', 'cannabinol', 'clonazepam', 'cocaine', 'delta8_tetrahydrocannabinol', 'delta9_tetrahydrocannabinol', 'diametre', 'epaisseur', 'fub_amb', 'gammabutyrolactone', 'hauteur', 'heroine', 'ketamine', 'largeur', 'levamisole', 'lidocaine', 'longueur', 'masse', 'mdmb_4en_pinaca', 'methamphetamine', 'morphine', 'noscapine', 'o6_monoacetylmorphine', 'paracetamol', 'phenacetine', 'procaine']]
    quanti = quanti.fillna(value=0.0).astype(float)
    
    samples[['_3_4_methylenedioxyethylamphetamine', '_3_4_methylene_dioxy_methylamphetamine', '_5f_adb', '_5f_mdmb_pica', 'acide_4_hydroxybutanoique', 'adb_butinaca', 'amphetamine', 'buprenorphine', 'cafeine', 'cannabidiol', 'cannabinol', 'clonazepam', 'cocaine', 'delta8_tetrahydrocannabinol', 'delta9_tetrahydrocannabinol', 'diametre', 'epaisseur', 'fub_amb', 'gammabutyrolactone', 'hauteur', 'heroine', 'ketamine', 'largeur', 'levamisole', 'lidocaine', 'longueur', 'masse', 'mdmb_4en_pinaca', 'methamphetamine', 'morphine', 'noscapine', 'o6_monoacetylmorphine', 'paracetamol', 'phenacetine', 'procaine']] = quanti[['_3_4_methylenedioxyethylamphetamine', '_3_4_methylene_dioxy_methylamphetamine', '_5f_adb', '_5f_mdmb_pica', 'acide_4_hydroxybutanoique', 'adb_butinaca', 'amphetamine', 'buprenorphine', 'cafeine', 'cannabidiol', 'cannabinol', 'clonazepam', 'cocaine', 'delta8_tetrahydrocannabinol', 'delta9_tetrahydrocannabinol', 'diametre', 'epaisseur', 'fub_amb', 'gammabutyrolactone', 'hauteur', 'heroine', 'ketamine', 'largeur', 'levamisole', 'lidocaine', 'longueur', 'masse', 'mdmb_4en_pinaca', 'methamphetamine', 'morphine', 'noscapine', 'o6_monoacetylmorphine', 'paracetamol', 'phenacetine', 'procaine']]

    # Subsampling data
    if subsample_size != -1:
        samples = samples.iloc[:subsample_size, :]

    return samples


def load_samples_dataset(size=-1):
    samples = dl.load_samples(subsample_size=size)
    # clean_samples = samples.drop(columns=['id', 'num_echantillon', 'id_lot'])
    clean_samples = samples.drop(columns=['id', 'id_lot'])

    dataset_tuples = []
    ids = samples['id_lot'].unique()

    print('Creating positive examples.')
    for id_index in tqdm(range(len(ids))):

        id = ids[id_index]
        batch_samples = list(clean_samples.loc[samples['id_lot'] == id].itertuples(index=False, name=None))
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