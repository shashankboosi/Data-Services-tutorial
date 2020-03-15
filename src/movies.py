import ast
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd

filename = os.path.basename(sys.modules[__name__].__file__)


def log(question, output_df, other):
    print("--------------- {}----------------".format(question))
    if other is not None:
        print(question, other)
    if output_df is not None:
        print(output_df.head(5).to_string())


def print_dataframe(dataframe, print_column=True, print_rows=True):
    # print column names
    if print_column:
        print(",".join([column for column in dataframe]))

    # print rows one by one
    if print_rows:
        for index, row in dataframe.iterrows():
            print(",".join([str(row[column]) for column in dataframe]))


def question_1(movies, credits):
    """
    :param movies: the path for the movie.csv file
    :param credits: the path for the credits.csv file
    Join the two datasets based on the "id" columns in the datasets
    :return: df1
            Data Type: Dataframe
    """

    movies_df = pd.read_csv(movies)
    credits_df = pd.read_csv(credits)
    df1 = pd.merge(left=movies_df, right=credits_df, left_on='id', right_on='id')

    log("QUESTION 1", output_df=df1, other=df1.shape)
    return df1


def question_2(df1):
    """
    :param df1: the dataframe created in question 1
    Keep the following columns in columns_to_store and drop the remaining in the resultant dataframe
    :return: df2
            Data Type: Dataframe
    """

    columns_to_store = [
        'id', 'title', 'popularity', 'cast', 'crew', 'budget', 'genres', 'original_language', 'production_companies',
        'production_countries', 'release_date', 'revenue', 'runtime', 'spoken_languages', 'vote_average', 'vote_count'
    ]
    columns_to_drop = [x for x in list(df1.columns) if x not in columns_to_store]
    df2 = df1.drop(columns_to_drop, axis=1)

    log("QUESTION 2", output_df=df2, other=(len(df2.columns), sorted(df2.columns)))
    return df2


def question_3(df2):
    """
    :param df2: the dataframe created in question 2
    Set the index of the resultant dataframe as 'id'
    :return: df3
            Data Type: Dataframe
    """

    df3 = df2.set_index('id')

    log("QUESTION 3", output_df=df3, other=df3.index.name)
    return df3


def question_4(df3):
    """
    :param df3: the dataframe created in question 3
    Drop all rows where the budget is 0
    :return: df4
            Data Type: Dataframe
    """

    df4 = df3[df3.budget != 0]

    log("QUESTION 4", output_df=df4, other=(df4['budget'].min(), df4['budget'].max(), df4['budget'].mean()))
    return df4


def question_5(df4):
    """
    :param df4: the dataframe created in question 4
    Add a new column for the dataframe, and name it "success_impact" based on " (revenue - budget)/budget "
    :return: df5
            Data Type: Dataframe
    """

    df5 = df4.assign(success_impact=pd.Series((df4['revenue'] - df4['budget']) / df4['budget']).values)

    log("QUESTION 5", output_df=df5,
        other=(df5['success_impact'].min(), df5['success_impact'].max(), df5['success_impact'].mean()))
    return df5


def question_6(df5):
    """
    :param df5: the dataframe created in question 5
    Normalize the " popularity " column by scaling between 0 to 100
    :return: df6
            Data Type: Dataframe
    """

    popularity_min = df5['popularity'].min()
    popularity_max = df5['popularity'].max()
    df5['popularity'] = df5['popularity'].apply(
        lambda x: ((x - popularity_min) / (popularity_max - popularity_min) * 100)
    )
    df6 = df5.copy()

    log("QUESTION 6", output_df=df6, other=(df6['popularity'].min(), df6['popularity'].max(), df6['popularity'].mean()))
    return df6


def question_7(df6):
    """
    :param df6: the dataframe created in question 6
    Change the data type of the "popularity" column to (int16)
    :return: df7
            Data Type: Dataframe
    """

    df7 = df6.astype({'popularity': 'int16'})

    log("QUESTION 7", output_df=df7, other=df7['popularity'].dtype)
    return df7


def question_8(df7):
    """
    :param df7: the dataframe created in question 7
    Clean the "cast" column by converting the complex value to a comma separated value.
     The cleaned "cast" column should be a comma-separated value of alphabetically sorted characters
    :return: df8
            Data Type: Dataframe
    """

    df7['cast'] = df7['cast'].apply(
        lambda x: ','.join(sorted([i['character'] for i in ast.literal_eval(x)]))
    )
    df8 = df7.copy()

    log("QUESTION 8", output_df=df8, other=df8["cast"].head(10).values)
    return df8


def question_9(df8):
    """
    :param df9: the dataframe created in question 8
    Return a list, containing the names of the top 10 movies according to the number of movie characters
    :return: movies
            Data Type: List of strings (movie titles)
    """

    df9 = df8.copy()
    df9['cast_list'] = df9['cast'].apply(
        lambda x: len(x.split(","))
    )
    sorted_df9 = df9.sort_values(by='cast_list', ascending=False)
    movies = sorted_df9['title'].iloc[:10].tolist()

    log("QUESTION 9", output_df=None, other=movies)
    return movies


def question_10(df8):
    """
    :param df8: the dataframe created in question 8
    Sort the dataframe by the release date
    :return: df10
            Data Type: Dataframe
    """

    df8['release_date_format'] = pd.to_datetime(df8.release_date)
    df10 = df8.sort_values(by='release_date_format', ascending=False)
    df10.drop('release_date_format', inplace=True, axis=1)

    log("QUESTION 10", output_df=df10, other=df10["release_date"].head(5).to_string().replace("\n", " "))
    return df10


def question_11(df10):
    """
    :param df10: the dataframe created in question 10
    Plot a pie chart, showing the distribution of genres in the dataset (e.g., Family, Drama)
    :return: nothing, but saves the figure on the disk
    """

    # Get the list of all the genres list
    genre_list = df10['genres'].apply(
        lambda x: [i['name'] for i in ast.literal_eval(x)]
    ).apply(pd.Series).stack().reset_index(drop=True)

    genre_distribution = genre_list.value_counts().sort_values(ascending=False)
    # Genres that are merged are: Music, Western, Documentary and TV Movie
    genres_to_merge = genre_distribution.iloc[-4:]
    final_distribution = genre_distribution.iloc[:-4]
    # Add the other genres to the genre distribution by summing the 4 infrequent labels of all genres
    final_distribution['other genres'] = genres_to_merge.sum()

    final_distribution.plot.pie(figsize=(8, 8), autopct='%1.1f%%', pctdistance=0.8)
    plt.title('Genres')
    plt.ylabel("")
    plt.tight_layout()

    plt.savefig("../output/{}-Q11.png".format(filename))


def question_12(df10):
    """
    :param df10: the dataframe created in question 10
    Plot a bar chart of the countries in which movies have been produced.
    For each county you need to show the count of movies
    :return: nothing, but saves the figure on the disk
    """

    plt.clf()
    country_list = df10['production_countries'].apply(
        lambda x: [i['name'] for i in ast.literal_eval(x)]
    ).apply(pd.Series).stack().reset_index(drop=True)

    country_list_distribution = country_list.value_counts().sort_index()
    plt.figure(figsize=(8, 6))
    country_list_distribution.plot.bar()
    plt.title('Production Country')
    plt.tight_layout()

    plt.savefig("../output/{}-Q12.png".format(filename))


def question_13(df10):
    """
    :param df10: the dataframe created in question 10
    Plot a scatter chart with x axis being "vote_average" and y axis being "success_impact"
    :return: nothing, but saves the figure on the disk
    """

    plt.clf()
    original_language_list = list(df10['original_language'].unique())
    color = ['royalblue', 'magenta', 'seagreen', 'mediumorchid', 'dimgray', 'palevioletred', 'cyan', 'orangered',
             'sandybrown', 'purple', 'brown', 'olive', 'pink', 'lightcoral', 'darkorange']
    if len(original_language_list) == len(color):
        first = original_language_list.pop(0)
        ax = df10.query('original_language == "' + first + '"').plot.scatter(x='vote_average',
                                                                             y='success_impact',
                                                                             label=first,
                                                                             color=color.pop(0))
        for lang, color in zip(original_language_list, color):
            ax = df10.query('original_language == "' + lang + '"').plot.scatter(x='vote_average',
                                                                                y='success_impact',
                                                                                label=lang,
                                                                                color=color,
                                                                                ax=ax)
    plt.title('vote_average vs success_impact')
    plt.tight_layout()

    plt.savefig("../output/{}-Q13.png".format(filename))


if __name__ == "__main__":
    df1 = question_1("../resources/movies_dataset/movies.csv", "../resources/movies_dataset/credits.csv")
    df2 = question_2(df1)
    df3 = question_3(df2)
    df4 = question_4(df3)
    df5 = question_5(df4)
    df6 = question_6(df5)
    df7 = question_7(df6)
    df8 = question_8(df7)
    movies = question_9(df8)
    df10 = question_10(df8)
    question_11(df10)
    question_12(df10)
    question_13(df10)
