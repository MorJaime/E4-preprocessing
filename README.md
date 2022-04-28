# E4-preprocessing
Empatica E-4 raw data extraction &amp; timestamp addition

# Functinality

## By Batch

### batch_e4_to_csv.py
batch_e4_to_csv.py --path-to-raw G:\JaimeMorales\Codes\open-pack\data\raw --path-output G:\JaimeMorales\Codes\open-pack\data\interim --path-to-shifts G:\JaimeMorales\Codes\open-pack\data\wearable_shifts.csv --users all --devices all --sensors all --timezone Japan --unit g

### batch_e4_to_adl.py
batch_e4_to_adl.py --path-to-raw G:\JaimeMorales\Codes\open-pack\data\raw --path-output G:\JaimeMorales\Codes\open-pack\data\ADLTagger --path-to-shifts G:\JaimeMorales\Codes\open-pack\data\wearable_shifts.csv --users all --devices all --timezone Japan --unit g
