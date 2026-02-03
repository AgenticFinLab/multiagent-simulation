"""
Define a general investor proxy by inheriting from BaseProxy but adding more specific implementations.
"""

import logging
from typing import List, Union, Dict

import ray

from llmgt.utils import record
from llmgt.utils import log_tag
from llmgt.proxy.base import BaseProxy
from llmgt.communication.base import (
    M2IMessage,
    I2MMessage,
    BaseCommProtocol,
    ProtocolOutbound,
)
from llmgt.utils.status import InvestorStatus


class GeneralInvestorProxy(BaseProxy):
    """
    A general investor that inherits from BaseProxy to organize standard proxy interfaces.

    The proxy serves as a distributed wrapper around BaseInvestor instances,
    enabling them to participate in Ray-based distributed market simulations.
    """

    def set_simulation_id(self, simulation_id: str):
        """
        Set the simulation ID for this investor instance.

        This method is called by the Simulator to assign a unique simulation ID
        to the investor, enabling tracking and correlation of investment decisions
        across the distributed system.
        """
        self._instance.simulation_id = simulation_id

    async def handle_messages(
        self,
        messages: List[Union[I2MMessage, M2IMessage]],
    ) -> List[Union[I2MMessage, M2IMessage]]:
        """
        Handle and filter incoming messages for the investor.

        For investors, this method filters to only process M2IMessage instances
        that are specifically targeted to this investor instance.
        """

        target_messages: List[M2IMessage] = []

        # Only targeted messages are received
        # These are two abundant verification to filter out:
        #   1. one that is not the market to investor message
        #   2. one that is not sent to this investor
        # However, they are abundant because:
        #   1. in general case, only market will send message to the investor
        #   2. the market will only send messages to the target investor not all.
        target_messages = [
            msg
            for msg in messages
            if isinstance(msg, M2IMessage)
            and (msg.investor_id == self.id or msg.investor_id is None)
        ]

        out_info = (
            f"{log_tag.BLOCK_INDENT}"
            f"{log_tag.PROCESS_TAG} Investor {self.id}, "
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
    ) -> List[M2IMessage]:
        """
        Process protocol packets through Protocol's decode to generate M2IMessage instances.

        This method decodes protocol-level outbound packages into business messages
        and filters them to only include messages relevant to this investor.
        """

        m2i_messages: List[M2IMessage] = []

        try:
            for outbound in outbounds:
                # Call the Protocol's method to decode the protocol packet into M2IMessage
                decoded = protocol.decode([outbound])
                if decoded is None:
                    continue
                if isinstance(decoded, list):
                    m2i_messages.extend(decoded)
                else:
                    m2i_messages.append(decoded)
        except Exception as e:
            self._instance.alert_status = InvestorStatus.DATA_ANOMALY.format(e)
            out_error = f"Error decoding protocol outbounds: {e}"
            logging.info(out_error)
            print(out_error)

        out_info = (
            f"{log_tag.BLOCK_INDENT}{log_tag.DECODE_TAG} Investor {self.id}, "
            f"decoded #{len(outbounds)} outbound to #{len(m2i_messages)} messages."
        )
        logging.info(out_info)
        print(out_info)

        target_messages = await self.handle_messages(m2i_messages)
        return target_messages

    async def ready_for_decision(
        self,
        messages: List[Union[M2IMessage, I2MMessage]],
    ) -> bool:
        """
        Check if the investor is ready to make decisions based on received messages.

        This method delegates to the underlying BaseInvestor instance to determine
        if sufficient information has been received to make an investment decision.
        """

        return self._instance.ready_for_decision(messages)

    async def decision_on_messages(
        self,
        messages: List[Union[M2IMessage, I2MMessage]],
    ) -> List[I2MMessage]:
        """
        Make investment decision based on the received market messages.

        This method orchestrates the complete decision-making pipeline:
        1. Process incoming market messages
        2. Apply pre-decision processing
        3. Execute the core decision algorithm
        4. Apply post-decision processing
        5. Build the response message
        """

        # Let BaseInvestor handle the complete decision pipeline
        processed_msgs = self._instance.on_markets_messages(messages)
        processed_msgs = self._instance.prior_decision(processed_msgs)

        decision = await self._instance.decide(processed_msgs)
        final_decision = self._instance.post_decision(processed_msgs, decision)

        round_record = {
            "round_id": self._instance._round_index,
            "data": {"messages": processed_msgs, "decision": final_decision},
        }

        record.save_record(
            round_record,
            self._instance._storage_path,
            f"round_{self._instance._round_index:06d}",
            file_format="json",
            as_block=True,
        )
        self._instance.history_entry.append(round_record)

        i2m_message = self._instance.build_i2m_message(processed_msgs, final_decision)

        out_info = f"{log_tag.BLOCK_INDENT}{log_tag.BUILD_TAG} Investor {self.id}, built I2M message"
        logging.info(out_info)
        print(out_info)

        return i2m_message

    async def perform_decision(
        self,
        outbounds: List[ProtocolOutbound],
        protocol: BaseCommProtocol,
    ) -> List[I2MMessage]:
        """
        Main decision pipeline following BaseProxy interface.

        This method orchestrates the complete workflow from protocol messages
        to investment decisions, following the template defined in BaseProxy.
        """
        out_info = f"{log_tag.START_TAG} Investor {self.id}, performing decision..."
        logging.info(out_info)
        print(out_info)

        # Process protocol outbounds to get messages
        messages = await self.process_protocol_outbounds(outbounds, protocol)

        # Check if ready for decision
        if not await self.ready_for_decision(messages):
            out_info = (
                f"{log_tag.BLOCK_INDENT}Investor {self.id}, not ready for decision yet"
            )
            logging.info(out_info)
            print(out_info)
            return []

        # Make decisions on messages
        investor_result = await self.decision_on_messages(messages)

        out_info = (
            f"{log_tag.BLOCK_INDENT}{log_tag.COMPLETE_TAG} Investor {self.id}, "
            f"completed decision, produced 1 message"
        )
        logging.info(out_info)
        print(out_info)

        return investor_result

    async def send_message(self, i2m_message, **kwargs) -> Dict[str, M2IMessage]:
        """
        Build messages to be sent to others.

        For investors, this method typically handles responses to market messages
        rather than initiating new communications. Investors generally respond
        to market decisions rather than broadcasting their own initiatives.
        """
        return {}
