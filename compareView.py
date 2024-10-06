import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('InvetigateOpay350UserPhone1.csv')

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16))

def plot_histogram(ax, data, title):
    ax.hist(data, bins=20, range=(0, 1), edgecolor='black', color='skyblue')
    ax.set_title(title)
    ax.set_xlabel('Similarity')
    ax.set_ylabel('Frequency')
    ax.set_xlim(0, 1)

plot_histogram(ax1, df['similarity_with_account_name'].dropna(), 
               'Name Similarity Distribution - Account Name')

plot_histogram(ax2, df['similarity_with_submitted_name'].dropna(), 
               'Name Similarity Distribution - Submitted Name')

plt.tight_layout()
plt.savefig('name_similarity_distribution3333.png')
plt.close()

print("Histogram saved as 'name_similarity_distribution.png'")
print(f"Records for Account Name Similarity: {df['similarity_with_account_name'].notna().sum()}")
print(f"Records for Submitted Name Similarity: {df['similarity_with_submitted_name'].notna().sum()}")