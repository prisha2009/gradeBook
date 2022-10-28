import pandas as pd   # Pandas help to open or edit files
from pathlib import Path  # Finds the absolute path of the parent folder.
import matplotlib.pyplot as plt
import scipy.stats
import numpy as np #numpy helps in complec mathematical questions

HERE = Path(__file__).parent
data_folder = HERE / "data"

roster = pd.read_csv(
    data_folder / "roster.csv",
    converters= {"NetID" : str.lower, "Email Address" : str.lower}, # Sets the rule for NetID and Email, the rule is, whenever they will be used, it will convert it to a lower case.
    usecols=["Section", "Email Address", "NetID"], # Create cols with netID and email in lower case
    index_col="NetID",
)

hw_exam = pd.read_csv(
    data_folder / "hw_exam_grades.csv",
    # usecols = []
    index_col = "SID"
)


# For Glob: https://www.geeksforgeeks.org/how-to-use-glob-function-to-find-files-recursively-in-python/
# print(list(data_folder.glob("quiz_*_grades.csv")))

quiz_grades = pd.DataFrame()

for file_path in data_folder.glob("quiz_*_grades.csv"):
    quiz_name = " ".join(file_path.stem.title().split("_")[:2])
    quiz = pd.read_csv(
        file_path,
        usecols=["Email","Grade"],
        index_col="Email"
    ).rename(columns = {'Grade':quiz_name})
    # print(quiz)
    quiz_grades = pd.concat([quiz_grades,quiz],axis = 1)
    

# Merging the data
final_data1 = pd.merge(
    roster,
    hw_exam,
    left_index=True,
    right_index=True,
)

final_data = pd.merge(
    final_data1,
    quiz_grades,
    left_on = "Email Address",
    right_index=True
)

final_data = final_data.fillna(0)
# print(final_data.head())

exam = 3
# 1,2,3
for n in range(1,exam+1):
    final_data[f"Exam {n} Score"] = (
        final_data[f"Exam {n}"] / final_data[f"Exam {n} - Max Points"]
    )
    
homework_scores = final_data.filter(regex=r"^Homework \d\d?$", axis = 1) # regex = regular expression and is used for searching a pattern in a file.
# print(homework_scores)
homework_max_points = final_data.filter(regex=r"^Homework \d\d? -",axis = 1)
# print(homework_max_points)


sum_of_hw_score = homework_scores.sum(axis=1)
sum_of_hw_max = homework_max_points.sum(axis=1)

avg_hw_score = sum_of_hw_score / sum_of_hw_max
# print(avg_hw_score)

final_data['Average Homework'] = avg_hw_score

quiz_scores = final_data.filter(regex=r"^Quiz \d\d?$", axis = 1)
quiz_max_points = pd.Series({'Quiz 1' : 20,'Quiz 2' : 20,'Quiz 3' : 20,'Quiz 4' : 20,'Quiz 5' : 20}) # Series() = Series of number

sum_of_quiz_score = quiz_scores.sum(axis=1)
sum_of_quiz_max_score = quiz_max_points.sum()

avg_of_quiz = sum_of_quiz_score / sum_of_quiz_max_score

final_data["Average Quiz"] = avg_of_quiz

# 100: E1-5%, E2-10%, E3-15%,  Q-5X4-20%, H-10X5-50%

weightings = pd.Series(
    {
        'Exam 1 Score': 0.05,
        'Exam 2 Score': 0.1,
        'Exam 3 Score': 0.15,
        'Average Quiz' : 0.20,
        'Average Homework' : 0.50,
    }
)

grades = {
    90: "A",
    80: "B",
    70: "C",
    60: "D",
    0: "F"
}


final_score = (final_data[weightings.index] * weightings).sum(axis = 1)

final_data['Final Score'] = final_score

final_mean = final_data['Final Score'].mean()
final_std = final_data['Final Score'].std()

x = np.linspace(final_mean - 5 * final_std, final_mean + 5 * final_std, 200)
dist = scipy.stats.norm.pdf(x, loc = final_mean, scale = final_std)
plt.plot(x, dist, label = "Normal Distribution", linewidth = 4)
plt.legend()
plt.show()

print(final_data)

