# L3AGQ_XAgent

## Objective
The goal of this project is to replace the existing Langchain REACT Agent with XAgent in the L3AGI project. 

## Approach
### Dependencies
- Removed all the dependencies related to Langchain REACT Agent in L3AGI PROJECT. Like from langchain.agents import create_react_agent.
- Replaced them with XAgent framework related dependencies.

### Target Files
- test.py, conversational.py, and dialogue_agent_with_tools.py are the target files I considered to be modified.
- These are the key areas in the L3AGI framework where the Langchain REACT Agent was implemented.

### Key Modifications
- XAgent Initialization: The new XAgent was initialised as "agent=XAgent(xagent_config)" instead of "agent=create_react_agent(llm, tools, prompt=agentPrompt)".
- Replaced Langchain’s initialize_agent and AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION to XAgent initialization.
- Updated the configurations and dependencies for XAgent.

### Changes in conversational.py
- Included dependencies for XAgent
  ```
  from xagent import XAgent
  from xagent.config import XAgentConfig
  ```
- Initialized XAgent with XAgentConfig for configurations.
  ```
  xagent_config = XAgentConfig(
                llm=llm,
                tools=tools,
                memory=memory,
                system_message=system_message,
                verbose=True,
                output_parser=ConvoOutputParser(),
            )
  agent = XAgent(xagent_config)
  agent_executor = agent.get_executor()
  ```
- Replaced Langchain’s AgentExecutor with XAgent’s direct execution flow using XAgent.run().

### Changes in dialogue_agent_with_tools.py
- The dependency added is ``` from xagent import XAgent ```.
- Initialized XAgent
  ```
  agent = XAgent(
                tools=tools,
                llm=llm,
                agent_kwargs={
                    "system_message": system_message,
                    "output_parser": ConvoOutputParser(),
                },
            )
  ```








  

