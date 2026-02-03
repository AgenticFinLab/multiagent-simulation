"""
Define a general market proxy by inheriting from BaseProxy but adding more specific implementations.

This module provides a concrete implementation of BaseProxy specifically designed for
Market entities, handling Investor-to-Market communication and market decision-making processes.
"""

import logging
from typing import Dict, List, Optional, Union

import ray

from llmgt.utils import log_tag, record
from llmgt.proxy.base import BaseProxy
from llmgt.communication.base import (
    M2IMessage,
    I2MMessage,
    BaseCommProtocol,
    ProtocolOutbound,
)
from llmgt.utils.status import MarketStatus


class GeneralMarketProxy(BaseProxy):
    """
    A general market that inherits from BaseProxy to organize standard proxy interfaces.
    """

    def set_simulation_id(self, simulation_id: str):
        """
        Set the simulation ID for this market instance.

        This method is called by the Simulator to assign a unique simulation ID
        to the market, enabling tracking and correlation of market decisions
        across the distributed system.
        """
        self._instance.simulation_id = simulation_id

    def build_initial_m2i_messages(self, round_id: int) -> List[M2IMessage]:
        """
        Build initial messages for all investors participating in this market.

        Delegates to the underlying market instance to generate initial state
        messages for all registered investors.
        """
        return self._instance.build_initial_m2i_messages(round_id)

    async def handle_messages(
        self,
        messages: List[Union[I2MMessage, M2IMessage]],
    ) -> List[Union[I2MMessage, M2IMessage]]:

        target_messages: List[I2MMessage] = []

        # Some markets may only allow certain investors to participate
        # These are two abundant verification to filter out:
        #   1. one that is not the investor to market message
        #   2. one that is not sent from allowed investor
        # However, they are abundant because:
        #   1. in general case, only investor will send message to the market
        #   2. the investor will only send messages to the target market not all.
        target_messages = [
            msg
            for msg in messages
            if isinstance(msg, I2MMessage) and msg.market_id == self.id
        ]

        out_info = (
            f"{log_tag.BLOCK_INDENT}"
            f"{log_tag.PROCESS_TAG} Market {self.id}, "
            f"handled #{len(messages)} messages to "
            f"#{len(target_messages)} target messages."
        )
        logging.info(out_info)
        print(out_info)

        return target_messages

    async def process_protocol_outbounds(
        self,
        outbounds: List[ProtocolOutbound],
        protocol: BaseCommProtocol,
    ) -> List[I2MMessage]:
        """
        Process protocol packets through Protocol's decode to generate I2MMessage instances.

        This method decodes protocol-level outbound packages into business messages
        and filters them to only include messages relevant to this market.
        """

        i2m_messages: List[I2MMessage] = []
        try:
            for outbound in outbounds:
                # Call the Protocol's method to decode the protocol packet into I2MMessage
                decoded = protocol.decode([outbound])
                if decoded is None:
                    continue
                if isinstance(decoded, list):
                    i2m_messages.extend(decoded)
                else:
                    i2m_messages.append(decoded)
        except Exception as e:
            self._instance.alert_status = MarketStatus.DATA_ANOMALY
            out_error = f"Error decoding protocol outbounds: {e}"
            logging.info(out_error)
            print(out_error)

        out_info = (
            f"{log_tag.BLOCK_INDENT}{log_tag.DECODE_TAG} Market {self.id}, "
            f"decoded #{len(outbounds)} outbound to #{len(i2m_messages)} messages."
        )
        logging.info(out_info)
        print(out_info)

        target_messages = await self.handle_messages(i2m_messages)
        return target_messages

    async def ready_for_decision(
        self,
        messages: List[Union[M2IMessage, I2MMessage]],
    ) -> bool:
        """
        Check if the market is ready to make decisions based on received messages.

        This method delegates to the underlying BaseMarket instance to determine
        if sufficient information has been received to make a market decision.
        """

        return self._instance.ready_for_decision(messages)

    async def decision_on_messages(
        self,
        messages: List[Union[M2IMessage, I2MMessage]],
    ) -> M2IMessage:
        """
        Make decision based on the messages.

        This method orchestrates the complete decision-making pipeline:
        1. Process incoming investor messages
        2. Apply pre-decision processing
        3. Execute the core decision algorithm
        4. Apply post-decision processing
        5. Build the response message

        Note: `decision_on_messages` only return a single variable (that is the M2IMessage) containing one decision instead of a list. This is because the market only make one decision per round.
        """
        # Let BaseMarket handle the complete decision pipeline
        processed_messages = self._instance.on_investors_messages(messages)
        processed_messages = self._instance.prior_decision(processed_messages)

        decision = await self._instance.decide(processed_messages)
        final_decision = self._instance.post_decision(processed_messages, decision)

        # Create a complete record structure for this round
        # Include both the round ID and the clearing decision data for easy retrieval
        round_record = {
            "round_id": self._instance._round_index,
            "data": {"messages": processed_messages, "decision": final_decision},
        }

        # Save to persistent storage for long-term preservation
        # This ensures clearing decisions survive system restarts and enable historical analysis
        record.save_record(
            round_record,
            self._instance._storage_path,
            f"round_{self._instance._round_index:06d}",
            file_format="json",
            as_block=True,
        )
        self._instance.history_entry.append(round_record)

        m2i_message = self._instance.build_m2i_message(
            processed_messages, final_decision
        )
        return m2i_message

    async def perform_decision(
        self,
        outbounds: List[ProtocolOutbound],
        protocol: BaseCommProtocol,
    ) -> Optional[M2IMessage]:
        """
        Main decision pipeline following BaseProxy interface.

        This method orchestrates the complete workflow from protocol messages
        to market decisions, following the template defined in BaseProxy.
        """
        out_info = f"{log_tag.START_TAG} Market {self.id}, performing decision..."
        logging.info(out_info)
        print(out_info)

        # Process protocol outbounds to get messages
        messages = await self.process_protocol_outbounds(outbounds, protocol)

        # Check if ready for decision
        if not await self.ready_for_decision(messages):
            out_info = (
                f"{log_tag.BLOCK_INDENT}Market {self.id}, not ready for decision yet"
            )
            logging.info(out_info)
            print(out_info)
            return None

        # Make decisions on messages
        market_result = await self.decision_on_messages(messages)

        out_info = (
            f"{log_tag.BLOCK_INDENT}{log_tag.COMPLETE_TAG} Market {self.id}, "
            f"completed decision, produced 1 message"
        )
        logging.info(out_info)
        print(out_info)

        return market_result

    async def send_message(
        self,
        i2m_message,
        **kwargs,
    ) -> Dict[str, M2IMessage]:
        """
        Build messages to be sent to others.

        For markets, this method handles the distribution of market decisions
        to relevant investors. Markets typically broadcast decisions or send
        targeted responses based on investor participation.
        """
        return {}
