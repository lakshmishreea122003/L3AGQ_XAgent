import asyncio
from langchain import hub
from xagent import XAgent  # Import XAgent

from agents.base_agent import BaseAgent
from agents.conversational.output_parser import ConvoOutputParser
from agents.conversational.streaming_aiter import AsyncCallbackHandler
from agents.handle_agent_errors import handle_agent_error
from config import Config
from memory.zep.zep_memory import ZepMemory
from postgres import PostgresChatMessageHistory
from services.pubsub import ChatPubSubService
from services.run_log import RunLogsManager
from services.voice import speech_to_text, text_to_speech
from typings.agent import AgentWithConfigsOutput
from typings.config import AccountSettings, AccountVoiceSettings
from utils.system_message import SystemMessageBuilder
from utils.model import get_llm

class ConversationalAgent(BaseAgent):
    async def run(
        self,
        settings: AccountSettings,
        voice_settings: AccountVoiceSettings,
        chat_pubsub_service: ChatPubSubService,
        agent_with_configs: AgentWithConfigsOutput,
        tools,
        prompt: str,
        voice_url: str,
        history: PostgresChatMessageHistory,
        human_message_id: str,
        run_logs_manager: RunLogsManager,
        pre_retrieved_context: str,
    ):
        # Initialize memory
        memory = ZepMemory(
            session_id=str(self.session_id),
            url=Config.ZEP_API_URL,
            api_key=Config.ZEP_API_KEY,
            memory_key="chat_history",
            return_messages=True,
        )
        memory.human_name = self.sender_name
        memory.ai_name = agent_with_configs.agent.name

        # Build the system message
        system_message = SystemMessageBuilder(
            agent_with_configs, pre_retrieved_context
        ).build()

        callbacks = []

        if run_logs_manager:
            callbacks.append(run_logs_manager.get_agent_callback_handler())

        res: str

        try:
            # Handle voice input
            if voice_url:
                configs = agent_with_configs.configs
                prompt = speech_to_text(voice_url, configs, voice_settings)

            # Initialize XAgent using the pattern from the first implementation
            agent = XAgent(
                tools=tools,
                model=get_llm(settings, agent_with_configs),
                system_message=system_message.content,
                memory=memory,
                callbacks=callbacks,
                output_parser=ConvoOutputParser(),
            )

            # Run the XAgent to get the response
            res = agent.run(input=prompt)

        except Exception as err:
            # Handle errors and save context
            res = handle_agent_error(err)
            memory.save_context(
                {
                    "input": prompt,
                    "chat_history": memory.load_memory_variables({})["chat_history"],
                },
                {"output": res},
            )
            yield res

        try:
            # Generate voice output if applicable
            configs = agent_with_configs.configs
            voice_url = None
            if "Voice" in configs.response_mode:
                voice_url = text_to_speech(res, configs, voice_settings)

        except Exception as err:
            res = f"{res}\n\n{handle_agent_error(err)}"
            yield res

        # Create and send AI message
        ai_message = history.create_ai_message(
            res,
            human_message_id,
            agent_with_configs.agent.id,
            voice_url,
        )

        chat_pubsub_service.send_chat_message(chat_message=ai_message)
