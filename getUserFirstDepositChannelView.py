import matplotlib.pyplot as plt
import seaborn as sns

data = {
    "PAYSTACK_CARD (20)": 231,
    "PAYSTACK_BANK (21)": 15,
    "PAYSTACK_TRANSFER (25)": 2862,
    "QUICKTELLER (50)": 71,
    "PALMPAY_E_WALLET (51)": 25,
    "GTB (60)": 67,
    "BILLER_ZENITH (1011)": 9,
    "BILLER_UBA (1012)": 11,
    "BILLER_OPAY (1016)": 18747,
    "BILLER_KUDA (1017)": 379,
    "BILLER_PALM_PAY (1018)": 2349,
    "BILLER_CORAL_PAY (1020)": 144,
    "BILLER_PALM_PAY_V2 (1021)": 3756,
    "BILLER_MONNIFY (1022)": 2,
    "OPAY_CHECKOUT (1203)": 2927
}



total_value = sum(data.values())
percentage_data = {k: (v / total_value) * 100 for k, v in data.items()}
sorted_percentage_data = sorted(percentage_data.items(), key=lambda x: x[1], reverse=True)
labels = [item[0] for item in sorted_percentage_data]
percentages = [item[1] for item in sorted_percentage_data]
sns.set_theme(style="whitegrid")
colors = sns.color_palette("magma", len(data))  
plt.figure(figsize=(12, 10))
ax = sns.barplot(x=percentages, y=labels, palette=colors)
plt.title("350 User(Required update name) First Deposit Channel", fontsize=18)
plt.xlabel("Percentage (%)", fontsize=14)
plt.ylabel("Channel", fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
sns.despine()
for i, p in enumerate(percentages):
    ax.text(p + 1, i + 0.1, f'{p:.2f}%', fontsize=10, va='center')

plt.tight_layout()
plt.savefig("350_deposit_channels.png")  
plt.show()
