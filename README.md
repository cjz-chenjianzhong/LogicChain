# LogicChain - Expert System based on Large Language Model

## Introduction

### 
- LogicChain uses an LLM as the rule reasoning engine of expert system, makes decisions based on rule logic and input information ，and takes actions.
- The input information is unrestricted and can include sensor status data, statistical information, AI detection results, user input text, clock information, and so on. Rule logic refers to text commands similar to "If ..., Then ..." and a large number of rules form a rule knowledge base, also known as expert knowledge in the field of expert systems. The actions to be executed by the decisions are also unrestricted and can include AI capabilities, message pushing, device operations, information inquiries, etc. In the current context of the LLM field, these actions are also referred to as Agents.
- The decision result itself is also fed back into the input information, cyclically triggering rules until the LLM believes that no rules can be triggered, which we call the decision chain or inner loop; the result of the action taken after the decision is also fed back into the input information, cyclically triggering rules to execute actions, which we call the action chain or outer loop.

<img src="img_for_readme/concept.png">

## Architecture

- LLM is the core of the system: LLM generates new triggered rules and actions According to external information, system prompts, rule libraries, action libraries, triggered rule instructions, and action results.


<img src="img_for_readme/architecture.png">


## What Can LogicChain do

## How To Use LogicChain

## To Do
