import csv
import json
import requests
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
from requests.exceptions import JSONDecodeError


# 您提供的相似度計算工具
class SimilarUtil:
    @staticmethod
    def get_spin_similarity_ratio(str1: str, str2: str) -> float:
        if not str1 or not str2:
            return 0
        if str1.lower() == str2.lower():
            return 1.0

        len_str1 = len(str1)
        spin_ratio = 0.0

        for i in range(len_str1):
            temp = str1[len_str1-i:] + str1[:len_str1-i]
            score = SimilarUtil.get_similarity_ratio(temp, str2)
            spin_ratio = max(score, spin_ratio)

        return spin_ratio

    @staticmethod
    def get_similarity_ratio(str1: str, str2: str) -> float:
        max_len = max(len(str1), len(str2))
        return 1 - SimilarUtil.compare(str1, str2) / max_len if max_len > 0 else 0

    @staticmethod
    def compare(str1: str, str2: str) -> int:
        n, m = len(str1), len(str2)
        if n == 0:
            return m
        if m == 0:
            return n

        d = [[0] * (m + 1) for _ in range(n + 1)]

        for i in range(n + 1):
            d[i][0] = i
        for j in range(m + 1):
            d[0][j] = j

        for i in range(1, n + 1):
            ch1 = str1[i - 1]
            for j in range(1, m + 1):
                ch2 = str2[j - 1]
                if ch1.lower() == ch2.lower():
                    temp = 0
                else:
                    temp = 1
                d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + temp)

        return d[n][m]

class SimilarityNameService:
    def process_v1(self, source: str, target: str) -> float:
        return SimilarUtil.get_spin_similarity_ratio(
            re.sub(r'\s+', ' ', source),
            re.sub(r'\s+', ' ', target)
        )

# 初始化相似度計算服務
similarity_service = SimilarityNameService()

# 讀取原始 CSV 文件並處理每一行
input_file = '350UserPhone.csv'
output_file = 'InvetigateOpay350UserPhone.xlsx'
api_url = 'https://api.paystack.co/bank/resolve'
headers = {
    'Authorization': 'Bearer sk_test_28d4a1335c818459bd6b0af73474ffd8ba359405'
}
# 并行处理函数
def process_row(row):
    phone = row['phone']
    submission_content = json.loads(row['submission_content'])
    
    # 组合 currentFirstName 和 currentLastName
    current_first_name = submission_content.get('currentFirstName', '')
    current_last_name = submission_content.get('currentLastName', '')
    current_full_name = f"{current_first_name} {current_last_name}".strip()

    # 组合 submittedFirstName 和 submittedLastName
    submitted_first_name = submission_content.get('submittedFirstName', '')
    submitted_last_name = submission_content.get('submittedLastName', '')
    submitted_full_name = f"{submitted_first_name} {submitted_last_name}".strip()

    # 发送 API 请求
    params = {
        'account_number': phone,
        'bank_code': '999992'  # 根据实际情况修改 bank_code
    }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        response.raise_for_status()  # 如果请求失败，抛出异常
        response_data = response.json()
        print(response_data)
    except JSONDecodeError:
        print(f"Error decoding JSON for phone {phone}, response content: {response.text}")
        response_data = None
    except requests.exceptions.RequestException as e:
        print(f"Request failed for phone {phone}: {e}")
        response_data = None

    # 提取 account_name 并计算相似度
    if response_data and response_data.get('status') and 'data' in response_data:
        account_name = response_data['data'].get('account_name', '')
        similarity_with_account_name = similarity_service.process_v1(current_full_name, account_name)
    else:
        account_name = 'N/A'
        similarity_with_account_name = 0.0
    
    # 计算 currentFullName 与 submittedFullName 的相似度
    similarity_with_submitted_name = similarity_service.process_v1(current_full_name, submitted_full_name)

    return {
        'id': row['id'],
        'phone': phone,
        'currentFullName': current_full_name,
        'account_name': account_name,
        'similarity_with_account_name': similarity_with_account_name,
        'submittedFullName': submitted_full_name,
        'similarity_with_submitted_name': similarity_with_submitted_name
    }

# 使用多线程并行请求
results = []
with open(input_file, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    
    # 使用 ThreadPoolExecutor 并行处理
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(process_row, row) for row in reader]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)

# 转换为 DataFrame 并保存到 Excel 文件
df = pd.DataFrame(results)
df.to_excel(output_file, index=False)

# 统计和绘图
# 1. 有 currentFullName 且拿到 account_name 的比例
df_with_fullname = df[df['currentFullName'] != '']
account_name_retrieval_rate = (df_with_fullname['account_name'] != 'N/A').mean()

print(f"有拿到 account name 的比例: {account_name_retrieval_rate:.2%}")

# 2. 有 account_name 的相似度分布图
similarity_account_name = df_with_fullname[df_with_fullname['account_name'] != 'N/A']['similarity_with_account_name']
similarity_submitted_name = df_with_fullname['similarity_with_submitted_name']

# 绘制相似度分布图
plt.figure(figsize=(14, 7))
plt.hist(similarity_account_name, bins=20, alpha=0.5, label='Similarity with Account Name')
plt.hist(similarity_submitted_name, bins=20, alpha=0.5, label='Similarity with Submitted Name')
plt.xlabel('Similarity Score')
plt.ylabel('Frequency')
plt.title('Similarity Distribution')
plt.legend(loc='upper right')
plt.grid(True)
plt.show()

print(f"处理完成，结果已写入 {output_file}")