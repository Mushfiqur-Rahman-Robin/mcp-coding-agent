import asyncio
import os
import traceback

from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("Please set your OPENAI_API_KEY environment variable")

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1,
    openai_api_key=OPENAI_API_KEY
)

class CodingAgent:
    def __init__(self):
        self.server_config = {
            "CodingAgent": {
                "url": "http://localhost:8092/mcp/",
                "transport": "streamable_http"
            }
        }
        self.client = MultiServerMCPClient(self.server_config)

    async def execute_task(self, task: str) -> str:
        """
        Executes a single coding task by creating a session, loading tools,
        and running the agent within that session's context.
        """
        final_message = "Agent did not produce a final answer."
        try:
            # The session must be active for the entire agent invocation
            async with self.client.session("CodingAgent") as session:
                # Load tools inside the active session
                tools: list[BaseTool] = await load_mcp_tools(session)
                print(f"✅ Loaded {len(tools)} tools for this task.")

                agent = create_react_agent(llm, tools)

                print("--- AGENT WORKFLOW STARTED ---")
                async for chunk in agent.astream(
                    {"messages": [{"role": "user", "content": task}]}
                ):
                    if "messages" in chunk.get("agent", {}):
                        last_message = chunk["agent"]["messages"][-1]
                        if isinstance(last_message, AIMessage) and not last_message.tool_calls:
                             final_message = last_message.content
                print("--- AGENT WORKFLOW FINISHED ---")

            return final_message

        except Exception as e:
            print(f"AN EXCEPTION OCCURRED: {e}")
            traceback.print_exc()
            return f"❌ Error during task execution: {str(e)}"


async def main():
    agent = CodingAgent()
    print("🤖 Coding Agent Initialized!")
    print("Available commands:")
    print("  - Type your coding task")
    print("  - Type 'quit' to exit")
    print("-" * 50)

    while True:
        try:
            task = input("\n💭 Enter your coding task: ").strip()
            if task.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            if not task:
                continue

            print("🔄 Processing your request...")
            result = await agent.execute_task(task)
            print(f"\n🤖 Agent's Final Response:\n{result}")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())