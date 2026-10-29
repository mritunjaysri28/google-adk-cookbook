from datetime import datetime, timedelta
import os
import pandas as pd
from docx import Document # Requires python-docx
from pypdf import PdfReader # Requires pypdf

def get_date(x_days_from_today:int):
    """
    Retrieves a date for today or a day relative to today.

    Args:
        x_days_from_today (int): how many days from today? (use 0 for today)

    Returns:
        A dict with the date in a formal writing format. For example:
        {"date": "Wednesday, May 7, 2025"}
    """

    target_date = datetime.today() + timedelta(days=x_days_from_today)
    date_string = target_date.strftime("%A, %B %d, %Y")

    return {"date": date_string}

def read_document_content(file_path: str) -> str:
    """Reads content from various file types and returns a single text string."""

    file_extension = os.path.splitext(file_path)[1].lower()

    try:
        if file_extension in ['.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        elif file_extension == '.docx':
            doc = Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])

        elif file_extension == '.pdf':
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text

        elif file_extension == '.csv':
            df = pd.read_csv(file_path)
            # Convert the DataFrame structure into a readable string
            return "CSV Data:\n" + df.to_string()

        else:
            return f"Unsupported file type: {file_extension}"

    except Exception as e:
        return f"Error processing file {os.path.basename(file_path)}: {e}"


def search_local_documents(query: str) -> str:
    """
    Searches all documents in the './docs/a' directory for content relevant
    to the user's inquiry...
    """
    query = query.lower()
    results = []

    # Define the path to your documents relative to where the agent is run
    LOCAL_DOC_PATH = os.path.join(os.path.dirname(__file__), 'data', 'planet-search-docs')


    # Iterate over all items in the target directory
    for item in os.listdir(LOCAL_DOC_PATH):
        file_path = os.path.join(LOCAL_DOC_PATH, item)
        if os.path.isdir(file_path):
            continue

        # Use the new universal function to get content
        content = read_document_content(file_path)

        # Check for errors from the content reader
        if content.startswith("Error") or content.startswith("Unsupported"):
             results.append(f"Error for {item}: {content}")
             continue

        content_lower = content.lower()
        results.append(f"--- Document: {item} ---\n...{content_lower}...\n")

    # 3. Compile the final result for the LLM

    if not results:
        return f"No relevant information found for the query: '{query}' in local documents."

    # Return a combined string of all snippets, truncated if too long for the LLM
    final_result = "\n".join(results)

    return final_result