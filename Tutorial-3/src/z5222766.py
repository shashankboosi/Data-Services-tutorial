# The logic to the code is written by sboosi(z5222766)
import sys
from ast import literal_eval

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler

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
        "movie_id",
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
        ["keywords", "name", 3],
        ["genres", "name", 3],
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

    return df_clean


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


def feature_extraction_and_transformation(clean_data, target):
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

    le = LabelEncoder()
    clean_data["original_language"] = le.fit_transform(clean_data["original_language"])

    print(clean_data.iloc[1])

    min_max = MinMaxScaler()
    for i in clean_data.columns:
        clean_data[i] = min_max.fit_transform(clean_data[i]).reshape(1, -1)

    print(clean_data.iloc[1])


if __name__ == "__main__":

    # Condition to use 3 arguments according to the requirements
    if len(sys.argv) == 3:
        full_cmd_arguments = sys.argv
        argument_list = full_cmd_arguments[1:]
        # Send the file names coming from command prompt
        train, validation = load_data(argument_list[0], argument_list[1])
        df_train_clean = data_clean(train, "regression")
        feature_extraction_and_transformation(df_train_clean, "revenue")
        print()
        print("---------------Validation---------------")
        print()
        df_clean_val = data_clean(validation, "regression")
        feature_extraction_and_transformation(df_clean_val, "revenue")

    else:
        raise Exception(
            "Please make sure to give arguments according to the structure /python3 zid.py path1 path2/"
        )

    # model = linear_model.LinearRegression()
    # # model = linear_model.BayesianRidge(alpha_1=1e-06, alpha_2=1e-06, compute_score=False, copy_X=True,
    # #                                    fit_intercept=True, lambda_1=1e-06, lambda_2=1e-06, n_iter=300,
    # #                                    normalize=False, tol=0.001, verbose=False)
    # model.fit(diet_X_train, diet_y_train)

    # y_pred = model.predict(diet_X_test)

    # for i in range(len(diet_y_test)):
    #     print ("Expected:", diet_y_test[i], "Predicted:", y_pred[i])

    # # The mean squared error
    # print ("Mean squared error: %.2f" % mean_squared_error(diet_y_test, y_pred))
