import pandas as pd
import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt

def load_file(file_path):
    try:
        safe_path = Path(file_path).resolve()
        if not safe_path.is_file():
            raise FileNotFoundError(f"'{file_path}' is not a valid file.")

        if safe_path.stat().st_size > 100 * 1024 * 1024:
            raise ValueError(f"File '{file_path}' is too large (>100MB).")

        file_extension = safe_path.suffix.lower()
        if file_extension == '.csv':
            df = pd.read_csv(safe_path)
        elif file_extension == '.json':
            df = pd.read_json(safe_path)
        elif file_extension == '.xml':
            import defusedxml.ElementTree as ET
            tree = ET.parse(safe_path)
            df = pd.DataFrame(tree.getroot())
        else:
            raise ValueError(f"Unsupported file format '{file_extension}'")
        return df
    except Exception as e:
        raise Exception(f"Unable to parse '{file_path}'. {str(e)}")

def display_columns(df):
    print("\nAvailable columns:")
    for col in df.columns:
        print(f"- {col}")

def process_query(df, query):
    try:
        result = df.query(query)
        return result
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        return None

def visualize_data(df, column):
    if column not in df.columns:
        print(f"Error: Column '{column}' not found in the data.")
        return

    if df[column].dtype not in ['int64', 'float64']:
        print(f"Warning: Column '{column}' is not numeric. Displaying top 10 values.")
        value_counts = df[column].value_counts().nlargest(10)
    else:
        value_counts = df[column].value_counts()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    value_counts.plot(kind='bar', ax=ax1)
    ax1.set_title(f'Bar Chart: {column}')
    ax1.set_xlabel(column)
    ax1.set_ylabel('Count')

    value_counts.plot(kind='pie', ax=ax2, autopct='%1.1f%%')
    ax2.set_title(f'Pie Chart: {column}')

    plt.tight_layout()
    plt.show()

def main():
    while True:
        file_path = input("Enter the path to your log file (CSV, JSON, or XML), or 'quit' to exit: ")
        
        if file_path.lower() == 'quit':
            break

        try:
            df = load_file(file_path)
        except Exception as e:
            print(f"Error loading file: {str(e)}")
            continue

        display_columns(df)
        
        while True:
            user_input = input("\nEnter your query in boolean, 'visualize <column>', or 'back' to choose another file: ")
            
            if user_input.lower() == 'back':
                break
            
            if user_input.lower().startswith('visualize'):
                try:
                    _, column = user_input.split(maxsplit=1)
                    visualize_data(df, column)
                except ValueError:
                    print("Invalid visualization command. Use 'visualize <column>'.")
            else:
                result = process_query(df, user_input)
                
                if result is not None:
                    print("\nQuery result:")
                    print(result.to_string(index=False))
                    print(f"\nNumber of rows: {len(result)}")

    print("Thank you for using the log analyzer!")

if __name__ == "__main__":
    main()
