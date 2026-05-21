import os

def rename_files_from_n(folder, number):
    for filename in sorted(os.listdir(folder)):
        ext = os.path.splitext(filename)[1]
        old = os.path.join(folder, filename)
        new = os.path.join(folder, f"{number}_synth{ext}")
        os.rename(old, new)
        number += 1

# Использование:
rename_files_from_n("/home/matan/Desktop/STUDYING/COURSE_Classwork/data/dataset_v6_synth/result/labels", 971)