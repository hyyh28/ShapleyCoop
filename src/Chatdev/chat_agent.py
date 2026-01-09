import os
import json
import argparse
from model import call_api
import time
import numpy as np
import re
from typing import Dict, List, Tuple

agents = ["Chief Executive Officer", "Chief Product Officer", "Chief Technology Officer", "Programmer", "Code Reviewer", "Counselor"]

def parse(message):
    assert '<s>' in message and '</s>' in message
    start = message.index('<s>') + len('<s>')
    end = message.index('</s>')
    return message[start:end]


def parse_action(message, choices):
    assert '<s>' in message and '</s>' in message
    start = message.index('<s>') + len('<s>')
    end = message.index('</s>')
    action = message[start:end].strip('\n').strip()
    assert action in choices
    return message[start:end]

def append_to_json(new_data, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    else:
        existing_data = []
    
    existing_data.append(new_data)
    
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, ensure_ascii=False, indent=2)

def add_log_to_prompt(log_path: str) -> str:
    """
    Simply load JSON game log and append to existing prompt
    
    Args:
        log_path: Path to JSON log file
        base_prompt: Your existing negotiation prompt
        
    Returns:
        Prompt with raw log appended
    """
    with open(log_path) as f:
        game_log = json.load(f)
    
    return f"""
    ------Game log is as following:------
    {game_log}"""

class Agent:
    def __init__(self, args, name):
        self.args = args
        self.name = name
        self.dev = self.args.dev_dir
        self.log_dir = self.args.log_dir
        self.the_other_player = self.other_player(self.name)
        self.max_negotiation_round = self.args.max_negotiation_round
        self.previous_message = []
        self.n_agents = len(agents)
        self.gift = np.zeros((self.n_agents, self.n_agents), dtype=float)
        
    def other_player(self, name):
        return [ag for ag in agents if ag not in name]

    def negotiation(self, pre=False, s_q=True, sum=False):

        if s_q:
            negotiate_prompt = f"""
            You are {self.name}. Discuss with {self.other_player(self.name)} to distribute team rewards proportionally based on:
            1. Each agent's measurable contributions
            2. Critical actions that impacted outcomes
            3. Relative importance of each role

            *** You are self-interested, so your goal is to maximize your total reward(get more team reward).

            Guidelines:
            - Analyze game log for objective metrics
            - Propose percentage splits (0-100%) with justification
            - Adjust offers based on evidence
            - Maximum {self.max_negotiation_round} round.
           
            """
            
            negotiate_prompt += add_log_to_prompt(self.dev)     

            negotiate_prompt += """
            **You should analyze the step-by-step based on Shapley Value principles**:
            
            
            - Step 1: What is the potential total reward of all players(calculate the total reward use the action reward above and the system reward)?
              Please give an accurate number of the rewards of each players and check if your calculation is right(Agent1:reward, ... , Agent4:reward).
            - Step 2: Without detailed calculation, intuitively consider:
                - How much do you individually contribute to the whole game?
                - How much does the other player contribute?
               Please give an accurate number of the contribution of each player (Agent1:contribution, ... , Agent4:contribution).
            - Step 3: According to Shapley Value thinking:
                - Fair rewards should reflect each player's marginal contribution.
                - No player should demand more than their fair contribution.
            - Step 4: Analyze the previous messages:
                - Does the other player recognize your contribution fairly?
                - Are they offering a fair split, or are they trying to exploit you?
            - Step 5: Based on fairness and self-interest:
                - Should you agree, propose a counteroffer, or challenge their fairness?
            
            Please **explicitly write down your reasoning under a section called "Thought Process:"**.
            
            ### Thought Process:
            (Write your analysis step-by-step following the above steps.)
            
            ---
            
            Then, **write your negotiation message separately**

            Format: 
            <s>[Your analysis of contributions step by step] 
            [Proposed distribution with rationale] 
            [Response to previous offer if applicable]</s>

            Example(for Agent2), it the team wins the game, use reward, else use punishment:
            <s>Thought Process : I should analyze the step-by-step based on Shapley Value principles: Step1, ...... , Step5..... 
            Based on logged metrics: Agent1 30% team reward/punishment because due to the Shapley Value..., Agent3 20% team reward/punishment because due to the Shapley Value..., Agent4 20% team reward/punishment because due to the Shapley Value....
            I can adjust if you show different metrics.</s> 

            or if others gave proposal before, you can also say :
            <s>Thought Process : I should analyze the step-by-step based on Shapley Value principles: Step1, ...... , Step5..... 
            I accept/reject XX's proposal , because ....... </s>
            """
            if pre:
                previous_messages = "\n\nThe previous rounds of negotiation are presented below:\n" + '\n'.join(
                    self.previous_message)
                negotiate_prompt += previous_messages

        if sum:
            previous_messages = "\n\nThe previous rounds of negotiation are presented below:\n" + '\n'.join(
                    self.previous_message)
            negotiate_prompt = """
            You are the decider and need to make a final decision according to the negotiation rounds between players.
            """
            negotiate_prompt += previous_messages 
            negotiate_prompt += f"""
            ### Negotiation Summary
            After the negotiation, please give a conclusion of the team reward allocation and give the final decision.

            Format: 
            <s>[Your analysis of contributions according to the negotiation] 
            [The final decision of the reward allocation for each player]</s>

            ###Example(Surround your message with '<s>' and '</s>' to indicate the start and end of your message, it the team wins the game, use reward in reward/punishment, else use punishment.):
            
            <s>Based on the previous consersation, i will give a summary and reach the final decision: According to the negotiation, ......  The final decision is : Agent1 30% team reward/punishment because ..., Agent2 20% team reward/punishment because ..., Agent3 20% team reward/punishment because ..., Agent4 20% team reward/punishment because ....
            This is the final reward for each player.</s>
            """ 

        while True:
            try:
                message = call_api(self.args.model, negotiate_prompt, self.args.system_prompt)
                message = parse(message)
                return message
            except:
                time.sleep(0.1)

