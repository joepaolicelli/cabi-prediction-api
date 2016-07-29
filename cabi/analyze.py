# analyze


def analyze(db_engine, station_id, prep_type, techniques):
    """
    Run tests and print results using the passed techniques.

    Parameters:
        db_engine - sqlalchemy engine
        selector - WHERE section of sql query to select data
        prep_type - list of feature selection methods
        techniques - list of model creation methods
    """

    print("\n\nRESULTS")
    print("=" * 78, "\n")

    for ques in ["empty", "full"]:
        data = []

        for prep in prep_type:
            raw_data = prep(
                db_engine, station_id, "01/01/2015", "12/31/2015",
                sample_size=int(1.0e5))
            # 70% of data for training, 30% for testing
            cutoff = int(0.7 * len(raw_data["X"]))
            data_parts = {
                "Xtrain": raw_data["X"][:cutoff],
                "yemptytrain": raw_data["yempty"][:cutoff],
                "yfulltrain": raw_data["yfull"][:cutoff],
                "Xtest": raw_data["X"][cutoff:],
                "yemptytest": raw_data["yempty"][cutoff:],
                "yfulltest": raw_data["yfull"][cutoff:]
            }

            data.append((prep.__name__, data_parts))

        print(ques)
        print("=" * 78, "\n")

        for tnq in techniques:
            print(tnq.__name__)
            print("-" * 78)

            for dt in data:
                if len(data) > 1:
                    print(dt[0], ":", sep="")

                if ques == "empty":
                    tnq(
                        dt[1]["Xtrain"], dt[1]["yemptytrain"],
                        dt[1]["Xtest"], dt[1]["yemptytest"])
                else:
                    tnq(
                        dt[1]["Xtrain"], dt[1]["yfulltrain"],
                        dt[1]["Xtest"], dt[1]["yfulltest"])

                print()
