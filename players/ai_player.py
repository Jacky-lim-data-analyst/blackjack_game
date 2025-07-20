# Inherits from base_player.Player. Its make_decision() method would be done by LLM 
# based on some known info like how many players, what cards are in play (flipped_up),
# how many decks. Might need external dependencies like Langchain and Ollama

import asyncio
import json
from typing import Optional

from pydantic import BaseModel, Field   # for structured output
from ollama import AsyncClient

from .base_player import Player
from game_logic.hand import Hand
from game_logic.card import Card
from config import Decision, DEFAULT_OLLAMA_MODEL, POSSIBLE_BETS

class LLMDecision(BaseModel):
    """
    A Pydantic model to structure the decision output from the LLM.
    This ensures the output is predictable and easy to parse.
    """
    decision: Decision = Field(..., description="The decision to make. Must be one of the available options")
    reasoning: str = Field(..., description="Brief explanation of the reasoning behind the decision.")

class LLMInsuranceDecision(BaseModel):
    """
    A Pydantic model to structure the insurance decision output from the LLM
    """
    side_bet_or_not: bool = Field(..., description="True to take the insurance bet, False otherwise")
    reasoning: str = Field(..., description="Brief explanation of the reasoning behind the decision.")

class LLMPlayer(Player):
    """
    An AI player that uses LLM to make decisions.
    """
    def __init__(self, name, chips, model: str = DEFAULT_OLLAMA_MODEL):
        """
        Initializes the LLMPlayer.

        Args:
            name (str): The name of the player.
            chips (str): The number of chips the player has.
            model (str): The Ollama LLM model to use.
        """
        super().__init__(name, chips)
        # self.type = PlayerTypes.LLM
        self.local_llm = AsyncClient()
        self.model = model

    def get_possible_decisions(self, hand_index = 0):
        return super().get_possible_decisions(hand_index)
    
    def choose_bets(self):
        # TODO
        return super().choose_bets()

    def make_decision(self, hand: Hand, dealer_upcard: Card, context: Optional[dict] = None) -> Decision:
        """
        Synchronous wrapper for the async decision-making process.
        
        Args:
            hand (Hand): The player's hand.
            dealer_upcard (Card): The upcard of the dealer's hand.
            context (dict, optional): Additional context for decision-making. Defaults to None.

        Returns:
            Decision: The decision made by the llm.
        """
        # The game loop is asynchronous, so we run the async method and wait for its result
        return asyncio.run(self._async_make_decision(hand, dealer_upcard, context))
    
    async def _async_choose_bets(self, available_bets: list[int]) -> int:
        """Async method to get structured bet decision from LLM"""
        class LLMBetDecision(BaseModel):
            """
            A Pydantic model to structure the decision output from the LLM.
            """
            bet_amount: int = Field(..., description=f"Bet amounts chosen from available options: {available_bets}")
            reasoning: str = Field(..., description="Brief rationale for bet choice")

        system_prompt = f"""
        You're an expert Blackjack player. Choose a bet amount considering:
        - Available chips: {self.chips}
        - Table limits: {POSSIBLE_BETS}
        - Valid options: {available_bets}
        Use smart bankroll management.
        Respond ONLY in JSON format matching the schema.
        """

        user_prompt = f"Select your bet amount from {available_bets}:"
        try:
            response = await self.local_llm.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                format=LLMBetDecision.model_json_schema(),
                options={'temperature': 0.1}
            )

            # parse and validate response
            decision = LLMBetDecision.model_validate_json(response.message.content)
            print(f"{self.name} bets ${decision.bet_amount}.\nReasoning: {decision.reasoning}")

            # Ensure LLM chose valid bet
            if decision.bet_amount in available_bets:
                return decision.bet_amount
            else:
                print(f"Invalid bet ${decision.bet_amount}. Defaulting to min bet")
                return min(available_bets)

        except Exception as e:
            print(f"LLM bet error: {e}. Use min bet ${min(available_bets)}")
            return min(available_bets)


    async def _async_make_decision(self, hand: Hand, dealer_upcard: Card, context: Optional[dict] = None) -> Decision:
        """
        Core async method that interacts with LLM to get a decision
        """
        # determine the hand's index to get possible decisions
        try:
            hand_index = self.hand.index(hand)
        except ValueError:
            hand_index = 0

        possible_decisions = self.get_possible_decisions(hand_index)

        # if there are no possible decisions (e.g. player is bust), just stand
        if not possible_decisions:
            return Decision.STAND
        
        # system prompt to set the LLM's role and behavior
        system_prompt = """
        You are an expert Blackjack player. Your goal is to make the best possible decision to maximize
        your winnings based on basic Blackjack strategy. You will be given your current hand, 
        the dealer's upcard, and a list of valid decisions you can make.

        Analyze the situation carefully and choose the optimal move.
        You must respond in a structured JSON format that adheres to the provided schema,
        containing your decision and a brief reason for it.
        """

        # user prompt providing the current game state to the LLM
        user_prompt = f"""
        Here is the current game state:
        - Your hand: {hand} (Total value: {hand.calculate_total_value()})
        - Dealer's upcard: {dealer_upcard})
        - Your available options are: {', '. join([d.value for d in possible_decisions])}.
        - Additional context: {context if context else "No additional context."}

        Based on this information, what is your decision?
        """

        try:
            # call the LLM with the prompts and the desired JSON structure
            response = await self.local_llm.chat(
                model=self.model,
                messages= [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                format=LLMDecision.model_json_schema(),
                options={'temperature': 0.1},
            )

            # extract the tool call and parse the arguments from the LLM's response
            decision_response = LLMDecision.model_validate_json(response.message.content)
            # args = json.loads(tool_call.function.arguments)

            # llm_decision = LLMDecision(**args)
            decision = decision_response.decision

            print(f"LLM Player ({self.name}) reasoning: '{decision_response.reasoning}' -> Chose: {decision.value}")

            # validate that the LLM's decision is part of the possible decisions
            if decision in possible_decisions:
                return decision
            else:
                print(f"LLM chose an invalid decision: {decision.value}. Defaulting to 'stand'")
                return Decision.STAND
        except (Exception, json.JSONDecodeError) as e:
            print(f"An error occurred while getting the LLM decision: {e}")
            print("Defaulting to save move: stand")
            if Decision.STAND in possible_decisions:
                return Decision.STAND
            return possible_decisions[0]
        
    def make_decision_insurance(self, context = None) -> bool:
        """
        Synchronous wrapper for the async insurance decision-making process.
        
        Args:
            context (dict, optional): Additional context for decision-making. Defaults to None.

        Returns:
            bool: The decision made by the llm.
        """
        return asyncio.run(self._async_make_insurance_decision(context))
    
    async def _async_make_insurance_decision(self, context: Optional[dict] = None) -> bool:
        """
        Core async method that interacts with LLM to get an insurance decision
        """
        # Insurance is half the original bet. Check if player can afford it
        original_bet = self.bets[0] if self.bets else 0
        insurance_amount = original_bet / 2
        if self.chips < insurance_amount:
            print(f"LLM player {self.name} does not have enough chips to place an insurance bet.")
            return False
        
        system_prompt = """
        You are an expert Blackjack player providing advice on taking an insurance bet.
        The dealer's upcard is an Ace. Insurance is a side bet that pays 2:1 if the dealer has Blackjack.
        Statistically, insurance is often considered a poor bet for a basic strategy player.
        However, if card counting indicates a high proportion of 10-value cards remaining in the deck,
        it can become profitable.

        Analyze the provided context and decide whether to take the insurance bet.
        You must respond in a structured JSON format with 'side_bet_or_not' (boolean) and 'reasoning' (string).
        """

        user_prompt = f"""
        Here is the current game state:
        - Your hand: {self.hand[0]} (Total value: {self.hand[0].calculate_total_value()})
        - Your primary bet: {original_bet}
        - Insurance bet: {insurance_amount}
        - Your remaining chips: {self.chips}
        - Game context: {context if context else "No additional context provided"}
        Based on this information, should you take the insurance bet?
        """

        try:
            response = await self.local_llm.chat(
                model=self.model,
                messages= [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                format=LLMInsuranceDecision.model_json_schema(),
                options={'temperature': 0.1},
            )

            decision_response = LLMInsuranceDecision.model_validate_json(response.message.content)
            decision = decision_response.side_bet_or_not

            print(f"LLM Player ({self.name}) insurance reasoning: '{decision_response.reasoning}' -> Choose {'Yes' if decision else 'No'}")

            return decision
        
        except (Exception, json.JSONDecodeError) as e:
            print(f"An error occurred while getting the LLM insurance decision: {e}")
            print("Defaulting to not taking insurance.")
            return False