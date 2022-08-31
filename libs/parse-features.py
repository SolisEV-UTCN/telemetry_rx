if __name__ == "__main__":
    with open("qt-features.txt", "r") as features, open(
        "parsed-features.txt", "w"
    ) as parsed_features:
        for line in features.readlines():
            feature = f" -no-feature-{line.split('.')[0]}\\\n"
            parsed_features.write(feature)
