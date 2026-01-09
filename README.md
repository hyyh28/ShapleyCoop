# Shapley-Coop


## Quick Setup
```
conda create -n shapley python=3.10
conda activate shapley
pip install -r requirements.txt
cd src
```
Setup API keys in model.py
Set the corresponding agents in the chat_agent.py and main.py.


### Chatdev
```
cd src/Chatdev
python main.py --game Chatdev --max_negotiation_round 3 --final_round 3 --dev_dir=bmilog.json
```
or just
```
python main.py
```

### Explanation of the ChatDev Setup

The execution results of **ChatDev** in our experiments are based on the original project available at
[https://github.com/OpenBMB/ChatDev/](https://github.com/OpenBMB/ChatDev/).
We directly used their implementation, and the experiments can be reproduced by following the official documentation.

Our main focus is to evaluate whether **Shapley-Coop** can effectively perform **post-hoc benefit allocation** in real-world tasks. Therefore, when using ChatDev, we only consider **post-task credit and reward allocation** (i.e., fairly allocating credits and rewards after task completion). Unlike the **Raid Battle** setting, we do not model cooperation emergence during the task execution. This is because ChatDev itself is a deterministic and fully cooperative task.

For the complete **Shapley-Coop prompt design**, please refer to `raid_agent.py` under the `raid_battle` directory.

The file **`bmi.json`** contains organized results derived from the JSON logs produced by running ChatDev on the BMI example provided in the original repository. This organization was done manually, as the original log files are very long. The raw logs can be found at:
[https://github.com/OpenBMB/ChatDev/blob/main/WareHouse/BMI%20Calculator_DefaultOrganization_20230918110521/BMI%20Calculator_DefaultOrganization_20230918110521.log](https://github.com/OpenBMB/ChatDev/blob/main/WareHouse/BMI%20Calculator_DefaultOrganization_20230918110521/BMI%20Calculator_DefaultOrganization_20230918110521.log)

We processed the logs by keeping only the parts that reflect workload and task completion summaries.

The file **`ArtCanvas_Results.json`** contains the final results of our experiments on the **ArtCanvas** scenario. Unfortunately, the intermediate logs are no longer available due to a server issue that required reinstallation. At the time, we were working under a tight ACL deadline. In the future, when we release the complete GitHub project, we will rerun the experiments and provide the full logs.

Finally, the model used in our experiments was **DeepSeek-v3**. Since the model has been updated since then, results may vary with newer versions.



