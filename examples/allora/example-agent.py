import os
from game_sdk.game.agent import Agent, WorkerConfig
from game_sdk.game.custom_types import FunctionResult
from game_sdk.game.worker import Worker
from plugins.allora.allora_plugin import AlloraPlugin
from allora_sdk.v2.api_client import ChainSlug, PricePredictionToken, PricePredictionTimeframe

def get_agent_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    """
    Update state based on the function results
    """
    init_state = {}

    if current_state is None:
        return init_state

    if function_result.info is not None:
        # Update state with the function result info
        current_state.update(function_result.info)

    return current_state

def get_worker_state(function_result: FunctionResult, current_state: dict) -> dict:
    """
    Update state based on the function results
    """
    init_state = {}

    if current_state is None:
        return init_state

    if function_result.info is not None:
        # Update state with the function result info
        current_state.update(function_result.info)

    return current_state

allora_network_client = AlloraPlugin(
  chain_slug=ChainSlug.TESTNET,
  api_key=os.environ.get("ALLORA_API_KEY") or "UP-17f415babba7482cb4b446a1",
)

price_prediction_worker = WorkerConfig(
    id="price_prediction_worker",
    worker_description="Worker specialized in using Allora Network to get price predictions",
    get_state_fn=get_worker_state,
    action_space=[
        allora_network_client.get_function("get_price_prediction"),
    ],
)

topics_inferences_worker = WorkerConfig(
    id="topics_inferences_worker",
    worker_description="Worker specialized in using Allora Network to get topics details and inferences for a specific topic",
    get_state_fn=get_worker_state,
    action_space=[
        allora_network_client.get_function("get_all_topics"),
        allora_network_client.get_function("get_inference_by_topic_id"),
    ]
)

# Initialize the agent
agent = Agent(
    api_key=os.environ.get("GAME_API_KEY"),
    name="Allora Agent",
    agent_goal="Help user get the 5m price predictions for Luna from Allora Network.",
    agent_description=(
        "You are an AI agent specialized in Allora Network."
        "You are able to get price predictions from Allora Network and provide users insights into future price of different crypto assets."
        "You are able to get details about the topics deployed on Allora Network and provide users insights into the topics."
        "For all the active topics, you are able to get the latest inference using the topic id."
        f"The available assets for price predictions worker are {', '.join([token.value for token in PricePredictionToken])};"
        f"for the following timeframes: {', '.join([timeframe.value for timeframe in PricePredictionTimeframe])}"
        "If a price prediction is not available for a specific asset and timeframe,"
        "you should determine the topic id for the asset and timeframe and use the topics inferences worker to get the latest inference"
        "for the specified asset and timeframe. This will return the equivalent of a price prediction for the asset and timeframe."
    ),
    get_agent_state_fn=get_agent_state_fn,
    workers=[
        price_prediction_worker,
        topics_inferences_worker,
    ]
)

agent.compile()
agent.run()
