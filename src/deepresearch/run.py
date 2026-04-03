# Copyright (c) 2025 IFLYTEK Ltd.
# SPDX-License-Identifier: Apache 2.0 License

import asyncio
from typing import List, Union
from langgraph.types import Command

from deepresearch.agent.agent import build_agent
from langchain_core.messages import HumanMessage, AIMessage

graph = build_agent()


async def call_agent(
        messages: List[Union[HumanMessage, AIMessage]],
        max_depth: int = 3,
        save_as_html: bool = True,
        save_path: str = "./example/report"
) -> List[Union[HumanMessage, AIMessage]]:
    """
    调用Agent处理消息
    
    Args:
        messages: 消息列表
        max_depth: 最大搜索深度
        save_as_html: 是否保存为HTML
        save_path: 保存路径
        
    Returns:
        更新后的消息列表
    """
    if not messages:
        raise ValueError("Input could not be empty")
        
    # 验证消息类型
    valid_messages = [m for m in messages if isinstance(m, (HumanMessage, AIMessage))]
    if not valid_messages:
        raise ValueError("Messages must contain valid HumanMessage or AIMessage objects")
        
    state = {
        "messages": valid_messages
    }
    config = {
        "configurable": {
            "depth": max(1, min(max_depth, 10)),  # 限制范围 1-10
            "save_as_html": save_as_html,
            "save_path": save_path
        }
    }
    output = ""
    try:
        for message in graph.stream(
            input=state, config=config, stream_mode="values"
        ):
            if isinstance(message, Command):
                message = message.update
            if isinstance(message, dict) and "messages" in message:
                if "output" in message and isinstance(message["output"], dict):
                    if "message" in message["output"]:
                        output = message["output"]["message"]
    except Exception as e:
        print(f"Error during agent execution: {e}")
        output = f"Error: {str(e)}"
        
    valid_messages.append(AIMessage(content=output))
    return valid_messages


async def interactive_agent(max_depth: int = 3, save_as_html: bool = True):
    """
    Interactive function for conversing with the agent
    :param max_depth: Maximum depth for deepresearch.
    :param need_html: Save report as html in local.

    """
    messages: List[Union[HumanMessage, AIMessage]] = []

    welcome = "Welcome to iFlytek's DeepResearch!\n"
    input_prompt = "\nEnter your message and press Enter to send. \nType 'quit' to exit. \nType 'clear' to start a new session.\nPlease enter: "

    print(welcome)
    while True:
        try:
            user_input = input(input_prompt)
        except KeyboardInterrupt:
            print("\nProgram interrupted")
            break

        if user_input.lower() == 'quit':
            print("Exiting conversation, goodbye!")
            break
        if user_input.lower() == 'clear':
            messages = []
            print(welcome)
            continue

        messages.append(HumanMessage(content=user_input))

        print("Agent is processing...")
        messages = await call_agent(messages=messages, max_depth=max_depth, save_as_html=save_as_html)


if __name__ == '__main__':
    asyncio.run(interactive_agent(max_depth=1))

