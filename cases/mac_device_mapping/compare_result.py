import json
import os


def diff_json(file1, file2, output_file):
    """
    Compares two JSON files and writes the differences to an output JSON file,
    ignoring the order of elements within dictionaries and lists.

    Args:
        file1: The path to the first JSON file.
        file2: The path to the second JSON file.
        output_file: The path to the output JSON file where differences will be stored.
    """
    try:
        with open(file1, "r") as f1, open(file2, "r") as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)
    except (IOError, json.JSONDecodeError) as e:
        print(f"An error occured: {e}")
        return False

    def compare(path1, path2, value1, value2, differences):
        if isinstance(value1, dict) and isinstance(value2, dict):
            # Compare dictionaries, ignoring order of keys
            set1 = set(value1.keys())
            set2 = set(value2.keys())
            missing_keys = set1.difference(set2)
            extra_keys = set2.difference(set1)
            for key in missing_keys:
                differences.append(f"Path: {path1}/{key}, Missing in second JSON")
            for key in extra_keys:
                differences.append(f"Path: {path2}/{key}, Extra key in second JSON")
            for key in set1.intersection(set2):
                compare(
                    f"{path1}/{key}",
                    f"{path2}/{key}",
                    value1[key],
                    value2[key],
                    differences,
                )
        elif isinstance(value1, list) and isinstance(value2, list):
            # Compare lists, treating them as sets and ignoring order
            set1 = set(value1)
            set2 = set(value2)
            missing_elements = set1.difference(set2)
            extra_elements = set2.difference(set1)
            for element in missing_elements:
                differences.append(f"Path: {path1}, Missing element: {element}")
            for element in extra_elements:
                differences.append(f"Path: {path2}, Extra element: {element}")
        else:
            # Compare primitive values
            if value1 != value2:
                differences.append(
                    f"Path: {path1}, Values differ: {value1} vs {value2}"
                )

    differences = []
    compare("", "", data1, data2, differences)

    if differences:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(differences, f, indent=4)
        print(f"Differences found and written to: {output_file}")
    else:
        print("No differences found between the JSON files.")


def count_row(data: json) -> int:
    count = 0
    for row in data:
        count += 1

    return count


def count_json_rows(file1, file2):
    """
    Compares the content of two JSON files and returns True if they are equal, False otherwise.

    Args:
    file1: The path to the first JSON file.
    file2: The path to the second JSON file.

    Returns:
    True if the JSON files have the same content, False otherwise.
    """
    try:
        with open(file1, "r") as f1, open(file2, "r") as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)
    except (IOError, json.JSONDecodeError) as e:
        print(f"An error occured: {e}")
        return False

    print("DATA1 row count: " + str(count_row(data1)))
    print("DATA2 row count: " + str(count_row(data2)))


def _compare_json(data1, data2, path):
    """
    Recursive helper function that compares two JSON objects/arrays element-wise.

    Args:
        data1: The first JSON object/array to compare.
        data2: The second JSON object/array to compare.
        path: The current path within the JSON structure (used for error messages).

    Returns:
        True if the data structures are equal, False otherwise.
    """

    if type(data1) != type(data2):
        print(f"Path: {path}, Data type mismatch: {type(data1)} vs {type(data2)}")
        return False

    if isinstance(data1, dict):
        # Compare dictionaries
        if set(data1.keys()) != set(data2.keys()):
            print(f"Path: {path}, Key mismatch in dictionaries")
            return False
        for key in data1.keys():
            if not _compare_json(data1[key], data2[key], f"{path}/{key}"):
                return False
        return True
    elif isinstance(data1, list):
        # Compare lists element-wise
        if len(data1) != len(data2):
            print(f"Path: {path}, List length mismatch: {len(data1)} vs {len(data2)}")
            return False
        for i in range(len(data1)):
            if not _compare_json(data1[i], data2[i], f"{path}[{i}]"):
                return False
        return True
    else:
        # Compare primitive values
        if data1 != data2:
            print(f"Path: {path}, Values differ: {data1} vs {data2}")
            return False
        return True


def compare_json_files(file1, file2):
    """
    Compares the content of two JSON files and returns True if they are equal, False otherwise.

    Args:
    file1: The path to the first JSON file.
    file2: The path to the second JSON file.

    Returns:
    True if the JSON files have the same content, False otherwise.
    """
    try:
        with open(file1, "r") as f1, open(file2, "r") as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)
    except (IOError, json.JSONDecodeError) as e:
        print(f"An error occured: {e}")
        return False
    return _compare_json(data1, data2, path="")


# Change working directory to the directory of the script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

file1 = "./merge_clients.json"
file2 = "./merge_clients_1.json"

if compare_json_files(file1, file2):
    print("The JSON files have the same content.")
else:
    print("The JSON files have different content.")

output_file = "new_differences.json"


count_json_rows(file1, file2)
diff_json(file1, file2, output_file)
