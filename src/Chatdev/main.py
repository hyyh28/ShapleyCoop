# from raid_agent import Agent, append_to_json, agents
from chat_agent import Agent, append_to_json, agents
import os
import json
import argparse
from model import call_api
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', type=str, default='Chatdev')
    parser.add_argument('--max_negotiation_round', type=int, default=3)
    parser.add_argument('--final_round', type=int, default=3)
    parser.add_argument('--sample_num', type=int, default=10)
    parser.add_argument('--system_prompt', type=str, default="rational")
    parser.add_argument('--model', type=str, default='deepseek')
    parser.add_argument('--log_dir', default='./Bmi_Results.json')
    parser.add_argument('--dev_dir', default='./bmilog.json')
    args = parser.parse_args()
    args.system_prompt = f'You are a {args.system_prompt} assistant that carefully answer the question.'
    max_n = args.max_negotiation_round
    agents_chat = {"Chief Executive Officer": Agent(args, name="Chief Executive Officer"),
                   "Chief Product Officer": Agent(args, name="Chief Product Officer"),
                   "Chief Technology Officer": Agent(args, name="Chief Technology Officer"),
                   "Programmer": Agent(args, name="Programmer"),
                   "Code Reviewer": Agent(args, name="Code Reviewer"),
                   "Counselor": Agent(args, name="Counselor")}

    for i in range(0, args.final_round):
        print('------- Negotiation for the final team reward--------')
        for ag in agents:
            msg = agents_chat[ag].negotiation(s_q=True)
            agents_chat[ag].previous_message.append('{}'.format(ag) + 'said in negotiation turn {}: '.format(i + 1) + msg)
            for oth in agents_chat[ag].the_other_player:
                agents_chat[oth].previous_message.append(
                    '{}'.format(ag) + 'said in negotiation turn {}: '.format(i + 1) + msg)
            formatted_msg = f"{ag} said in negotiation turn {i + 1}: {msg}."
            print(formatted_msg)
            append_to_json([formatted_msg], args.log_dir)
    print('------- Final decision--------')
    msg = agents_chat[agents[0]].negotiation(pre=False, s_q=False, sum=True)
    formatted_msg = f"The final decision : {msg}."   
    print(formatted_msg)
    append_to_json([formatted_msg], args.log_dir)

    for ag in agents:
            agents_chat[ag].previous_message = []

    print(f'------------------log to {args.log_dir}--------------------')

