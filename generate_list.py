def generate_markdown(wordlist_path):
    char_0 = '○'
    char_1 = '●'

    try:
        with open(wordlist_path, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]

        if len(words) != 4096:
            print(f"Warning: Expected 4096 words, found {len(words)}.")

        # Print Markdown Table Header
        print("| Index | Word | Group 1 | Group 2 | Group 3 |")
        print("| --- | --- | --- | --- | --- |")

        for i, word in enumerate(words):
            # Convert index to 12-bit binary string (e.g., '000000000000')
            binary_str = format(i, '012b')

            # Replace 0s and 1s with circles
            circle_str = binary_str.replace('0', char_0).replace('1', char_1)

            # Split into 3 groups of 4 bits each
            group_1 = circle_str[0:4]
            group_2 = circle_str[4:8]
            group_3 = circle_str[8:12]

            print(f"| {i} | {word} | {group_1} | {group_2} | {group_3} |")

    except FileNotFoundError:
        print(f"Error: Could not find '{wordlist_path}'. Please ensure it is in the same directory.")

if __name__ == "__main__":
    generate_markdown("wordlist4096.txt")
