import csv
import json
import re
import matplotlib.pyplot as plt

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

def load_csv(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            print(f"CSV columns: {reader.fieldnames}")
            print(f"Sample row: {data[0] if data else 'No data'}")
            return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def parse_submission_content(content):
    try:
        return json.loads(content.replace('""', '"'))
    except json.JSONDecodeError:
        print(f"Error parsing JSON: {content}")
        return {}

def create_visualizations(status_counts, similarities):
    plt.figure(figsize=(8, 8))
    labels = [f"Status {status}" for status in status_counts.keys()]
    sizes = list(status_counts.values())
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    plt.title('Status Distribution')
    plt.savefig('status_distribution.png')
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.hist(similarities, bins=20, edgecolor='black')
    plt.title('Name Similarity Distribution')
    plt.xlabel('Similarity')
    plt.ylabel('Frequency')
    plt.savefig('name_similarity_distribution.png')
    plt.close()

def main():
    input_file = "/Users/evanslin/Desktop/BATCH&SHELL/path_to_your_csv_file.csv"  # Replace with your actual CSV file name
    
    data = load_csv(input_file)
    
    if not data:
        print("Unable to process data. Program terminated.")
        return

    similarity_service = SimilarityNameService()
    similarities = []
    status_counts = {}

    for row in data:
        submission_content = parse_submission_content(row.get('submission_content', '{}'))
        current_first = submission_content.get('currentFirstName', '')
        current_last = submission_content.get('currentLastName', '')
        submitted_first = submission_content.get('submittedFirstName', '')
        submitted_last = submission_content.get('submittedLastName', '')

        current_name = f"{current_first} {current_last}".strip()
        submitted_name = f"{submitted_first} {submitted_last}".strip()
        
        if not current_name or not submitted_name:
            print(f"Warning: Empty name for user ID {row.get('user_id')}")
            continue

        similarity = similarity_service.process_v1(current_name, submitted_name)
        similarities.append(similarity)

        status = row.get('status')
        status_counts[status] = status_counts.get(status, 0) + 1

        print(f"User ID: {row.get('user_id')}")
        print(f"Names: '{current_name}' vs '{submitted_name}'")
        print(f"Similarity: {similarity:.2%}")
        print(f"Status: {status}")
        print()

    total_count = sum(status_counts.values())
    print("Status Distribution:")
    for status, count in status_counts.items():
        percentage = (count / total_count) * 100 if total_count > 0 else 0
        print(f"Status {status}: {count} ({percentage:.2f}%)")

    if similarities:
        create_visualizations(status_counts, similarities)
        print("\nVisualization charts have been generated: 'status_distribution.png' and 'name_similarity_distribution.png'")
    else:
        print("No valid name comparisons were made. Unable to generate visualizations.")

if __name__ == "__main__":
    main()