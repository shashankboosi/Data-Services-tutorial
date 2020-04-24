# The logic to the code is written by sboosi(z5222766)
import sys
from ast import literal_eval

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from sklearn import linear_model
from sklearn.metrics import (accuracy_score, mean_squared_error,
                             precision_score, recall_score)
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC

# output = pd.DataFrame(data={"id": X_test["id"], "Prediction": y_pred})
# output.to_csv(path_or_buf="..\\output\\results.csv", index=False, quoting=3, sep=";")

# Function to import the data from the csv files
def load_data(train_data, validation_data):
    df_train = pd.read_csv(train_data)
    df_validation = pd.read_csv(validation_data)
    return df_train, df_validation


# Function to drop the columns which are not needed
def data_drop(data, type):
    columns_to_drop = [
        "homepage",
        "status",
        "overview",
        "tagline",
        "spoken_languages",
        "original_title",
    ]

    if type == "regression":
        columns_to_drop.append("rating")
    elif type == "classification":
        columns_to_drop.append("revenue")

    return data.drop(columns_to_drop, axis=1)


# Function to do the preliminary refinement of data
def data_refine(data, type):
    df_refine = data_drop(data, type)

    # Convert  release date to date-time and also extract the year
    df_refine["release_date"] = pd.to_datetime(
        df_refine["release_date"], format="%Y-%m-%d", errors="coerce"
    )

    df_refine["release_year"] = df_refine["release_date"].dt.year
    df_refine["release_month"] = df_refine["release_date"].dt.month
    df_refine.drop("release_date", axis=1, inplace=True)

    return df_refine


# This function extracts the first 3 attributes tag from the json feature objects and group them into a list of strings
def extract_attributes_from_json(json_data, attribute_name, no_of_elements):
    json_data = literal_eval(json_data)
    if json_data == []:
        return np.nan
    result_list = []
    count = 0
    for row in json_data:
        if count < no_of_elements:
            result_list.append(row[attribute_name])
            count += 1
        else:
            break
    return result_list


# This function extracts the job attributes with value Director from the json feature objects
def get_director_from_crew(json_data):
    json_data = literal_eval(json_data)
    if json_data == []:
        return np.nan
    for row in json_data:
        if row["job"] == "Director":
            return row["name"]
    return np.nan


# Function to extract the data out of the json object
def data_clean(data, type):
    df_clean = data_refine(data, type)

    # Features and their attributes with no of elements
    features = [
        ["cast", "name", 3],
        ["keywords", "name", 5],
        ["genres", "name", 5],
        ["production_companies", "name", 3],
        ["production_countries", "iso_3166_1", 3],
    ]
    # Extract the mentioned attributes from given feature
    for feature in features:
        df_clean[feature[0]] = df_clean[feature[0]].apply(
            lambda row: extract_attributes_from_json(row, feature[1], feature[2])
        )

    # Extract the director attributes from crew feature
    df_clean["director"] = df_clean["crew"].apply(get_director_from_crew)
    df_clean.drop("crew", axis=1, inplace=True)
    df_clean.dropna(inplace=True)

    return df_clean.reset_index(drop=True)


def replace_attribute_with_target_mean_values(data, value_dict, target):
    raw_dict = value_dict[target]
    if isinstance(data, list):
        result_list = []
        for i in data:
            result_list.append(raw_dict[i])
        return int(sum(result_list) / len(result_list))
    elif isinstance(data, str):
        return int(raw_dict[data])


def convert_the_attributes_based_on_target(data, feature, target):
    conversion_result = {}
    if isinstance(data[feature].iloc[0], list):
        data_stack = pd.DataFrame(
            {
                col: np.repeat(data[col].values, data[feature].str.len())
                for col in data.columns.drop(feature)
            }
        ).assign(**{feature: np.concatenate(data[feature].values)})[data.columns]
        conversion_result = data_stack.groupby([feature]).mean().to_dict()
    elif isinstance(data[feature].iloc[0], str):
        conversion_result = data.groupby([feature]).mean().to_dict()

    return data[feature].apply(
        lambda row: replace_attribute_with_target_mean_values(
            row, conversion_result, target
        )
    )


def string_transformation(string_data):
    if isinstance(string_data, list):
        return [str.lower(i.replace(" ", "")) for i in string_data]
    elif isinstance(string_data, str):
        return str.lower(string_data.replace(" ", ""))


def feature_extraction_and_transformation(clean_data, target, id_flag=False):
    features = [
        "cast",
        "keywords",
        "genres",
        "production_companies",
        "production_countries",
        "director",
    ]

    for feature in features:
        clean_data[feature] = clean_data[feature].apply(string_transformation)
        df_feature = clean_data[[feature, target]].copy()
        clean_data[feature + "_new"] = convert_the_attributes_based_on_target(
            df_feature, feature, target
        )
        clean_data.drop(feature, axis=1, inplace=True)

    clean_data.dropna(inplace=True)

    le = LabelEncoder()
    clean_data["original_language"] = le.fit_transform(clean_data["original_language"])

    id_target = []
    if id_flag:
        id_target = clean_data[["movie_id"]].copy()
    clean_data.drop("movie_id", axis=1, inplace=True)

    Y = clean_data[target]
    X = clean_data.drop(target, axis=1)

    # Min Max Scaler
    standard = StandardScaler()
    X = standard.fit_transform(X)

    if id_flag:
        return X, Y, id_target
    else:
        return X, Y


def pre_modeling(train, validation, problem_type, target):
    df_train_clean = data_clean(train, problem_type)
    X_train, Y_train = feature_extraction_and_transformation(df_train_clean, target)
    df_clean_val = data_clean(validation, problem_type)
    X_test, Y_test, id_target = feature_extraction_and_transformation(
        df_clean_val, target, True
    )
    return X_train, Y_train, X_test, Y_test, id_target


if __name__ == "__main__":

    # Condition to use 3 arguments according to the requirements
    if len(sys.argv) == 3:
        full_cmd_arguments = sys.argv
        argument_list = full_cmd_arguments[1:]
        # Send the file names coming from command prompt
        train, validation = load_data(argument_list[0], argument_list[1])

        zid = "z5222766"
        # ----------------------- Regression ------------------------
        problem_type = "regression"
        target = "revenue"
        X_train, Y_train, X_test, Y_test, id_target = pre_modeling(
            train, validation, problem_type, target
        )

        model = linear_model.Lasso()
        model.fit(X_train, Y_train)

        Y_pred = model.predict(X_test)

        regression_output_df = pd.DataFrame(
            {"movie_id": id_target["movie_id"].values, "predicted_revenue": Y_pred}
        )
        regression_output_df.to_csv(zid + ".PART1.output.csv", index=False)

        # The mean squared error and pearson correlation
        corr, _ = scipy.stats.pearsonr(Y_test, Y_pred)
        regression_pred_df = pd.DataFrame(
            {
                "zid": [zid],
                "MSR": [round(mean_squared_error(Y_test, Y_pred), 2)],
                "correlation": [round(corr, 2)],
            }
        )
        regression_pred_df.to_csv(zid + ".PART1.summary.csv", index=False)

        # ------------------------- Classification ---------------------
        problem_type = "classification"
        target = "rating"
        df_train_clean = data_clean(train, problem_type)
        X_train, Y_train, X_test, Y_test, id_target = pre_modeling(
            train, validation, problem_type, target
        )
        # Support Vector Machine
        svm = SVC(kernel="rbf")
        svm.fit(X_train, Y_train)

        predictions_svm = svm.predict(X_test)

        classification_output_df = pd.DataFrame(
            {
                "movie_id": id_target["movie_id"].values,
                "predicted_rating": predictions_svm,
            }
        )
        classification_output_df.to_csv(zid + ".PART2.output.csv", index=False)

        classification_pred_df = pd.DataFrame(
            {
                "zid": [zid],
                "average_precision": [
                    round(precision_score(Y_test, predictions_svm, average="macro"), 2)
                ],
                "average_recall": [
                    round(recall_score(Y_test, predictions_svm, average="macro"), 2)
                ],
                "accuracy": [round(accuracy_score(Y_test, predictions_svm), 2)],
            }
        )
        classification_pred_df.to_csv(zid + ".PART2.summary.csv", index=False)

    else:
        raise Exception(
            "Please make sure to give arguments according to the structure /python3 zid.py path1 path2/"
        )
