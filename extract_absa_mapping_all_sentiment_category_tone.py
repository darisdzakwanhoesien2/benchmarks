import pandas as pd

# Load the CSV file
df = pd.read_csv('data/ground_truth/absa_mapping.csv')

# List all columns that contain category, sentiment, or tone (case-insensitive)
cols_to_extract = [col for col in df.columns if any(key in col.lower() for key in ['category', 'sentiment', 'tone'])]

# Extract and save
extracted_df = df[cols_to_extract]
extracted_df.to_csv('data/ground_truth/absa_mapping_all_sentiment_category_tone.csv', index=False)

print('Saved absa_mapping_all_sentiment_category_tone.csv with columns:', cols_to_extract)
