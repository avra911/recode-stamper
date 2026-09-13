def generate_markdown(wordlist_path):
    # The two characters to use for 0 and 1
    char_0 = '○'
    char_1 = '●'
    
    try:
        with open(wordlist_path, 'r', encoding='utf-8') as f:
            words = [line.strip() for line in f if line.strip()]
            
        if len(words) != 4096:
            print(f"Warning: Expected 4096 words, found {len(words)}.")

        print("```markdown")
        for i, word in enumerate(words):
            # Convert index to 12-bit binary string (e.g., '000000000001')
            binary_str = format(i, '012b')
            
            # Replace '0' with ○ and '1' with ●
            circle_repr = binary_str.replace('0', char_0).replace('1', char_1)
            
            # Format output matching the desired representation
            print(f"{i:<4} {word:<12} {circle_repr}")
        print("```")
        
    except FileNotFoundError:
        print(f"Error: Could not find '{wordlist_path}'. Please ensure it is in the same directory.")

if __name__ == "__main__":
    generate_markdown("wordlist4096.txt")