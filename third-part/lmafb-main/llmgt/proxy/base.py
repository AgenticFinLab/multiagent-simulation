"""
Define the base structure and components of a proxy to be inherited by other proxies. It needs to be emphasize that the
proxy is implemented based on the Ray package, making a @ray.remote to be a necessary decorator for the
subsequent classes.
"""

import os
from abc import abstractmethod
from typing import Dict, List, Union

from llmgt.communication.base import (
    M2IMessage,
    I2MMessage,
    BaseCommProtocol,
    ProtocolOutbound,
)
from llmgt.market.base import BaseMarket, MarketDecision
from llmgt.investor.base import BaseInvestor, InvestorDecision


def set_environment(setup: dict):
    """Set the environment variables based on the setup."""
    for k, v in setup.items():
        os.environ[str(k)] = str(v)


# @ray.remote
# !Note: No need to add the @ray.remote decorator here, as it will be added in the child classes.
class BaseProxy:
    """
    A basic proxy containing the inherent functions and components to be inherited by other proxies.
    """

    def __init__(
            self,
            instance: Union[BaseMarket, BaseInvestor],
            proxy_config: dict,
    ):
        # An instance of the object to be proxied
        self._instance = instance
        self.id: str = instance.identity

        # Configuration to support the proxy
        self.proxy_config = proxy_config
        api_keys = proxy_config["api_keys"]
        env_overrides = proxy_config["env_overrides"]

        # Set up the environment variables
        set_environment(api_keys)
        set_environment(env_overrides)

    @abstractmethod
    async def handle_messages(
            self,
            messages: List[Union[I2MMessage, M2IMessage]],
    ) -> List[Union[I2MMessage, M2IMessage]]:
        """
        Handle and filter incoming messages for the instance before forwarding to decision-making.

        This method processes messages received from other entities (markets or investors)
        and performs validation, filtering, and preprocessing before they are used for
        decision-making.
        """
        raise NotImplementedError

    @abstractmethod
    async def process_protocol_outbounds(
            self,
            outbounds: List[ProtocolOutbound],
            protocol: BaseCommProtocol,
    ) -> List[Union[M2IMessage, I2MMessage]]:
        """
        Process protocol packets through Protocol's decode to generate the corresponding messages.

        This method takes raw protocol outbound packages and converts them into
        business messages using the provided communication protocol. It also
        handles any additional processing metadata.
        """
        raise NotImplementedError

    @abstractmethod
    async def decision_on_messages(
            self,
            messages: List[Union[M2IMessage, I2MMessage]],
    ) -> Union[M2IMessage, I2MMessage]:
        """
        Make decision based on the received messages.

        This is the core decision-making method that processes all necessary messages
        and generates a decision response. The method ensures that all required
        information is available before making the decision.
        """
        raise NotImplementedError

    @abstractmethod
    async def ready_for_decision(
            self,
            messages: List[Union[M2IMessage, I2MMessage]],
    ) -> bool:
        """
        Check if the current received messages contain sufficient information for decision-making.

        This method validates whether all necessary information has been received
        and the instance is ready to make a decision. The criteria for readiness
        depend on the specific requirements of the Market or Investor instance.
        """

        raise NotImplementedError

    async def perform_decision(
            self,
            outbounds: List[ProtocolOutbound],
            protocol: BaseCommProtocol,
    ) -> Union[List[Union[MarketDecision, InvestorDecision]], None]:
        """
        Dynamically receives the outbounds, process them to obtain messages, judge whether the decision condition
        reaches and making decision.

        This method coordinates the entire decision-making workflow:
        1. Process protocol outbounds to extract business messages
        2. Check if sufficient information is available for decision-making
        3. If ready, execute the decision-making process
        """
        raise NotImplementedError

    @abstractmethod
    async def send_message(self, i2m_message, **kwargs) -> Dict[str, M2IMessage]:
        """
        Build the message to be sent to others.

        This method handles the construction and routing of outgoing messages
        based on the decision made by the proxied instance. It manages the
        message distribution logic and handles any necessary message transformations.
        """

        raise NotImplementedError
