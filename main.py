import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import time
import re


def scrape_vandale_word_meaning(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the <div class="snippets"> element
            snippets_div = soup.find('div', class_='snippets')

            # Extract the plain text from the HTML content within the <div class="snippets"> element
            plain_text = snippets_div.get_text(separator=' ')

            return plain_text.strip()  # Remove leading/trailing whitespaces

        else:
            return f"Error: Unable to retrieve data. Status code: {response.status_code}"

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"


# Read words from the "input.txt" file where words are separated by line breaks
with open("input.txt", "r") as input_file:
    word_list = input_file.read().splitlines()

# Define the output file
output_file = "output.txt"

# Create an empty list to store the results
results = []

# Define the base URL without the word parameter
base_url = "https://www.vandale.nl/opzoeken?pattern="

# Use ThreadPoolExecutor to send GET requests simultaneously with a one-second delay
with ThreadPoolExecutor(max_workers=2) as executor:
    for word in word_list:
        # Build the URL for the current word
        url_nn = f"{base_url}{word}&lang=nn"
        url_ne = f"{base_url}{word}&lang=ne"

        # Send requests for both languages
        future_nn = executor.submit(scrape_vandale_word_meaning, url_nn)
        future_ne = executor.submit(scrape_vandale_word_meaning, url_ne)

        # Get the results
        result_nn = future_nn.result()
        result_ne = future_ne.result()

        # Remove multiple consecutive white spaces with a single space
        result_nn = re.sub(r'\s+\)', ')', result_nn).strip()
        result_nn = re.sub(r'\s+', ' ', result_nn)
        result_ne = re.sub(r'\s+', ' ', result_ne)

        # Remove space before the comma
        result_nn = re.sub(r'\( ', '(', result_nn)
        result_ne = re.sub(r' ,', ',', result_ne)

        # Append the results to the list
        results.append((word, result_nn, result_ne))
        print(word)
        print("\nNederlands")
        print(result_nn)

        print("\nEnglish")
        print(result_ne)
        print("-" * 40)  # Separate each word's results

        # Wait for one second before making the next request
        time.sleep(1)
# Write the results to the output file
with open(output_file, "a") as f:
    for word, result_nn, result_ne in results:
        f.write(f"{word}\n")
        f.write("Nederlands\n")
        f.write(result_nn + "\n\n")
        f.write("English\n")
        f.write(result_ne + "\n\n")
        f.write("-" * 40 + "\n")

print(f"Results have been appended to {output_file}")
