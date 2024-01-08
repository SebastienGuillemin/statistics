import psycopg2
import pandas as pd

def load_samples(subsample_size=-1):
    # Loading data
    conn = psycopg2.connect(database="full_STUPS",
                            user="postgres",
                            host='localhost',
                            password="postgres",
                            port=5432)
    cur = conn.cursor()
    cur.execute('''select distinct ep.*, id_lot
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


    #samples = samples.drop(columns=['id', 'num_echantillon'])

    # Subsampling data
    if subsample_size != -1:
        samples = samples.iloc[:subsample_size, :]

    return samples