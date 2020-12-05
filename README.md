# Topics Evaluation

Open source code for quickly creating Qualtrics surveys for topic model quality evaluation. Two different topic evaluation tasks can be generated: Ratings and Intrusion.

Intrusion Task - This task, proposed by Chang et al 2009 (https://proceedings.neurips.cc/paper/2009/file/f92586a25bb3145facd64ab20fd554ff-Paper.pdf), asks users to identify an 'intruder' word in a topic. This intruder word is selected from a different topic than the one being evaluated. Code for selecting these intruders is included in the survey generation script.

Ratings Task - This task, proposed by Newman et al 2010 (https://www.aclweb.org/anthology/N10-1012.pdf) ,asks users to rate the quality of a topic on a three point Likert scale.

The generated Qualtrics surveys are produced in the 'qsf' format (Qualtrice Survey Format) which is a json file compatible with Qualtrics (as of 12/5/2020). This format may change over time however requiring slight adaptations to the survey template.

Inputs - Both survey generation scripts expect a text file containing topics in the following format:
- 1 Line per topic
- Each line should contain a list of comma separated words
- These words should be in sorted order with the highest weight words at the front of the list

NOTE: The "topic_id" used in the survey will be the line number of the topic in the input file

Example file is included - `example_topics.txt`
Example Usage:
`python survey_tools/generate_intrusion_survey.py --file example_topics.txt -m example -n 3 -o example_intrusion`
`python survey_tools/generate_ratings_survey.py --file example_topics.txt -m example -n 3 -o example_rating`

Folder Descriptions:
`survey_tools` - Scripts and utility functions for generating Qualtrics surveys for conducting topic evaluations using either the 'Ratings' or 'Intrusion' tasks.
`final_data` - Data used to compare Ratings and Intrusion tasks across 3 different datasets. Includes different automatic topic coherence evaluation metrics.


Additional code forked from https://github.com/dallascard/scholar


