import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('InvetigateOpay350UserPhone1.csv')

def is_empty(value):
    return pd.isna(value) or str(value).strip() == ''

data_filtered = data[~(data['account_name'].apply(is_empty) | data['currentFullName'].apply(is_empty))]
print(f"Total rows: {len(data)}")
print(f"Rows after filtering out empty account_name or currentFullName: {len(data_filtered)}")
zero_similarity = data_filtered[
    (data_filtered['similarity_with_account_name'] == 0) | 
    (data_filtered['similarity_with_submitted_name'] == 0)
]
print(f"\nRows with zero similarity scores: {len(zero_similarity)}")
print("\nSample of rows with zero similarity scores:")
print(zero_similarity[['account_name', 'currentFullName', 'submittedFullName', 'similarity_with_account_name', 'similarity_with_submitted_name']].head())

zero_similarity.to_csv('zero_similarity_cases.csv', index=False)
print("Zero similarity cases saved to 'zero_similarity_cases.csv'")

plt.figure(figsize=(12, 6))
sns.kdeplot(data=data_filtered, x='similarity_with_account_name', fill=True, color='#ff9999', label='Account Name')
sns.kdeplot(data=data_filtered, x='similarity_with_submitted_name', fill=True, color='#66b3ff', label='Submitted Name')
plt.title('Distribution of Similarity Scores')
plt.xlabel('Similarity Score')
plt.ylabel('Density')
plt.legend()
plt.savefig('similarity_distribution2.png')
plt.close()
plt.figure(figsize=(10, 6))
plt.scatter(data_filtered['similarity_with_account_name'], 
            data_filtered['similarity_with_submitted_name'], 
            alpha=0.5)
plt.title('Scatter Plot of Similarity Scores')
plt.xlabel('Similarity with Account Name')
plt.ylabel('Similarity with Submitted Name')
plt.savefig('similarity_scatter.2png')
plt.close()

total_rows = len(data)
valid_rows = len(data_filtered)
plt.figure(figsize=(10, 6))
plt.pie([valid_rows, total_rows - valid_rows], 
        labels=['Valid', 'Invalid'], 
        autopct='%1.1f%%', 
        colors=['#66b3ff', '#ff9999'])
plt.title('Proportion of Rows with Non-empty account_name and currentFullName')
plt.axis('equal')
plt.savefig('data_validity_proportion2.png')
plt.close()

print("\nGraphs have been saved as 'similarity_distribution.png', 'similarity_scatter.png', and 'data_validity_proportion.png'.")