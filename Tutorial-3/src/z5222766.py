# The logic to the code is written by sboosi(z5222766)
import sys

import pandas as pd
from sklearn import linear_model

# output = pd.DataFrame(data={"id": X_test["id"], "Prediction": y_pred})
# output.to_csv(path_or_buf="..\\output\\results.csv", index=False, quoting=3, sep=";")

# Function to import the data from the csv files
def load_data(train_data, validation_data):
    df_train = pd.read_csv(train_data)
    df_validation = pd.read_csv(validation_data)
    return df_train, df_validation


def data_refinement():
    pass


if __name__ == "__main__":

    # Condition to use 3 arguments according to the requirements
    if len(sys.argv) == 3:
        full_cmd_arguments = sys.argv
        argument_list = full_cmd_arguments[1:]
        # Send the file names coming from command prompt
        train, validation = load_data(argument_list[0], argument_list[1])

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
