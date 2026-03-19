import pandas as pd

# Load the CSV file
df = pd.read_csv('data/ground_truth/absa_mapping.csv')

# Extract only the relevant columns
cols_to_extract = ['majority_category', 'majority_sentiment', 'majority_tone']
extracted_df = df[cols_to_extract]

# Save to a new CSV file
extracted_df.to_csv('data/ground_truth/absa_mapping_simple.csv', index=False)

print('Saved absa_mapping_simple.csv with columns:', cols_to_extract)
