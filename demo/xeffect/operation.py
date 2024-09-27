def load_csv(filename: str) -> str:
    # mock loading behavior
    if filename.endswith(".csv"):
        return "my,super,csv"
    else:
        raise FileNotFoundError(f"{filename} is not a csv file")
