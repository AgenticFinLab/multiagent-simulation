"""Canonical, scenario-agnostic agent classes.

This package auto-registers every archetype whose profile lives at
``examples/AGENT_POOL/{finance,market,opinion}/<stem>.md``.  See the
module docstring in earlier revisions for the naming contract and
the replication playbook.  209 archetypes are shipped as of the
latest full-pool rollout:

  * 195 finance investor agents  (Rule + LLM pairs)
  * 5 opinion-prefixed investor agents  (Rule + LLM pairs)
  * 9 market coordinators  (single Market<PascalStem> class each)

Investor modules expose ``Rule<PascalStem>`` + ``LLM<PascalStem>``
pairs sharing the same kebab-case ``STRATEGY``.  Coordinator modules
expose a single ``Market<PascalStem>`` class; they are always
rule-executed even when participants are LLM-driven.
"""

from masim.format.state import StandardMarketState
from masim.agents._base import CanonicalRulePlayer, CanonicalLLMPlayer
from masim.agents._coordinator_base import CanonicalMarketCoordinator

from masim.agents.active_rebalancer import RuleActiveRebalancer, LLMActiveRebalancer
from masim.agents.aggressive_investor import RuleAggressiveInvestor, LLMAggressiveInvestor
from masim.agents.algorithmic_trader import RuleAlgorithmicTrader, LLMAlgorithmicTrader
from masim.agents.anchor_depositor import RuleAnchorDepositor, LLMAnchorDepositor
from masim.agents.anchored_trader import RuleAnchoredTrader, LLMAnchoredTrader
from masim.agents.arbitrage_framer import RuleArbitrageFramer, LLMArbitrageFramer
from masim.agents.arbitrageur import RuleArbitrageur, LLMArbitrageur
from masim.agents.balanced_analyst import RuleBalancedAnalyst, LLMBalancedAnalyst
from masim.agents.bank_manager import RuleBankManager, LLMBankManager
from masim.agents.bayesian_updater import RuleBayesianUpdater, LLMBayesianUpdater
from masim.agents.belief_anchor import RuleBeliefAnchor, LLMBeliefAnchor
from masim.agents.block_trade_buyer import RuleBlockTradeBuyer, LLMBlockTradeBuyer
from masim.agents.bond_trader import RuleBondTrader, LLMBondTrader
from masim.agents.bottom_fisher import RuleBottomFisher, LLMBottomFisher
from masim.agents.break_even_trader import RuleBreakEvenTrader, LLMBreakEvenTrader
from masim.agents.bridge_builder import RuleBridgeBuilder, LLMBridgeBuilder
from masim.agents.calibrated_trader import RuleCalibratedTrader, LLMCalibratedTrader
from masim.agents.carry_trader import RuleCarryTrader, LLMCarryTrader
from masim.agents.cascade_follower import RuleCascadeFollower, LLMCascadeFollower
from masim.agents.category_overgeneralizer import RuleCategoryOvergeneralizer, LLMCategoryOvergeneralizer
from masim.agents.central_bank import RuleCentralBank, LLMCentralBank
from masim.agents.central_bank_defender import RuleCentralBankDefender, LLMCentralBankDefender
from masim.agents.commitment_escalator import RuleCommitmentEscalator, LLMCommitmentEscalator
from masim.agents.concentrated_fund import RuleConcentratedFund, LLMConcentratedFund
from masim.agents.conformist import RuleConformist, LLMConformist
from masim.agents.conservative_holder import RuleConservativeHolder, LLMConservativeHolder
from masim.agents.conservative_investor import RuleConservativeInvestor, LLMConservativeInvestor
from masim.agents.contagion_trader import RuleContagionTrader, LLMContagionTrader
from masim.agents.contrarian import RuleContrarian, LLMContrarian
from masim.agents.contrarian_investor import RuleContrarianInvestor, LLMContrarianInvestor
from masim.agents.contrarian_skeptic import RuleContrarianSkeptic, LLMContrarianSkeptic
from masim.agents.contrarian_statistical import RuleContrarianStatistical, LLMContrarianStatistical
from masim.agents.contrarian_trader import RuleContrarianTrader, LLMContrarianTrader
from masim.agents.convergence_arbitrageur import RuleConvergenceArbitrageur, LLMConvergenceArbitrageur
from masim.agents.convergence_trader import RuleConvergenceTrader, LLMConvergenceTrader
from masim.agents.core_bond_buyer import RuleCoreBondBuyer, LLMCoreBondBuyer
from masim.agents.counter_cyclical_lender import RuleCounterCyclicalLender, LLMCounterCyclicalLender
from masim.agents.creditor_panicker import RuleCreditorPanicker, LLMCreditorPanicker
from masim.agents.critical_thinker import RuleCriticalThinker, LLMCriticalThinker
from masim.agents.de_fi_lender import RuleDeFiLender, LLMDeFiLender
from masim.agents.default_follower import RuleDefaultFollower, LLMDefaultFollower
from masim.agents.depositor import RuleDepositor, LLMDepositor
from masim.agents.disposition_investor import RuleDispositionInvestor, LLMDispositionInvestor
from masim.agents.disposition_trader import RuleDispositionTrader, LLMDispositionTrader
from masim.agents.distorting_relayer import RuleDistortingRelayer, LLMDistortingRelayer
from masim.agents.distressed_buyer import RuleDistressedBuyer, LLMDistressedBuyer
from masim.agents.early_exit_trader import RuleEarlyExitTrader, LLMEarlyExitTrader
from masim.agents.ecb_intervenor import RuleEcbIntervenor, LLMEcbIntervenor
from masim.agents.endowed_holder import RuleEndowedHolder, LLMEndowedHolder
from masim.agents.equity_trader import RuleEquityTrader, LLMEquityTrader
from masim.agents.fact_checker import RuleFactChecker, LLMFactChecker
from masim.agents.flash_market_maker import RuleFlashMarketMaker, LLMFlashMarketMaker
from masim.agents.forced_seller import RuleForcedSeller, LLMForcedSeller
from masim.agents.frame_invariant_trader import RuleFrameInvariantTrader, LLMFrameInvariantTrader
from masim.agents.fundamental_analyst import RuleFundamentalAnalyst, LLMFundamentalAnalyst
from masim.agents.fundamental_anchor import RuleFundamentalAnchor, LLMFundamentalAnchor
from masim.agents.fundamental_hedger import RuleFundamentalHedger, LLMFundamentalHedger
from masim.agents.fundamental_investor import RuleFundamentalInvestor, LLMFundamentalInvestor
from masim.agents.fundamental_trader import RuleFundamentalTrader, LLMFundamentalTrader
from masim.agents.fundamentalist import RuleFundamentalist, LLMFundamentalist
from masim.agents.funding_currency_buyer import RuleFundingCurrencyBuyer, LLMFundingCurrencyBuyer
from masim.agents.gain_frame_follower import RuleGainFrameFollower, LLMGainFrameFollower
from masim.agents.greater_fool_speculator import RuleGreaterFoolSpeculator, LLMGreaterFoolSpeculator
from masim.agents.gullible_spreader import RuleGullibleSpreader, LLMGullibleSpreader
from masim.agents.hedged_carry_trader import RuleHedgedCarryTrader, LLMHedgedCarryTrader
from masim.agents.hedged_fund import RuleHedgedFund, LLMHedgedFund
from masim.agents.hft_market_maker import RuleHftMarketMaker, LLMHftMarketMaker
from masim.agents.high_frequency_trader import RuleHighFrequencyTrader, LLMHighFrequencyTrader
from masim.agents.hindsight_overconfident import RuleHindsightOverconfident, LLMHindsightOverconfident
from masim.agents.historical_anchor import RuleHistoricalAnchor, LLMHistoricalAnchor
from masim.agents.hot_hand_trader import RuleHotHandTrader, LLMHotHandTrader
from masim.agents.hot_money_funder import RuleHotMoneyFunder, LLMHotMoneyFunder
from masim.agents.house_money_trader import RuleHouseMoneyTrader, LLMHouseMoneyTrader
from masim.agents.ideologue import RuleIdeologue, LLMIdeologue
from masim.agents.imf_rescuer import RuleImfRescuer, LLMImfRescuer
from masim.agents.independent_assessor import RuleIndependentAssessor, LLMIndependentAssessor
from masim.agents.independent_thinker import RuleIndependentThinker, LLMIndependentThinker
from masim.agents.index_arbitrageur import RuleIndexArbitrageur, LLMIndexArbitrageur
from masim.agents.index_fund import RuleIndexFund, LLMIndexFund
from masim.agents.index_holder import RuleIndexHolder, LLMIndexHolder
from masim.agents.index_tracker import RuleIndexTracker, LLMIndexTracker
from masim.agents.inertial_holder import RuleInertialHolder, LLMInertialHolder
from masim.agents.information_environment import RuleInformationEnvironment, LLMInformationEnvironment
from masim.agents.information_trader import RuleInformationTrader, LLMInformationTrader
from masim.agents.insider_advantaged import RuleInsiderAdvantaged, LLMInsiderAdvantaged
from masim.agents.institutional_holder import RuleInstitutionalHolder, LLMInstitutionalHolder
from masim.agents.institutional_investor import RuleInstitutionalInvestor, LLMInstitutionalInvestor
from masim.agents.institutional_value import RuleInstitutionalValue, LLMInstitutionalValue
from masim.agents.intrinsic_value_trader import RuleIntrinsicValueTrader, LLMIntrinsicValueTrader
from masim.agents.ipo_flipper import RuleIpoFlipper, LLMIpoFlipper
from masim.agents.leverage_trader import RuleLeverageTrader, LLMLeverageTrader
from masim.agents.leveraged_buyer import RuleLeveragedBuyer, LLMLeveragedBuyer
from masim.agents.leveraged_carry_fund import RuleLeveragedCarryFund, LLMLeveragedCarryFund
from masim.agents.leveraged_fund import RuleLeveragedFund, LLMLeveragedFund
from masim.agents.leveraged_hedge_fund import RuleLeveragedHedgeFund, LLMLeveragedHedgeFund
from masim.agents.leveraged_investor import RuleLeveragedInvestor, LLMLeveragedInvestor
from masim.agents.leveraged_speculator import RuleLeveragedSpeculator, LLMLeveragedSpeculator
from masim.agents.liquidity_demander import RuleLiquidityDemander, LLMLiquidityDemander
from masim.agents.liquidity_provider import RuleLiquidityProvider, LLMLiquidityProvider
from masim.agents.liquidity_seeker import RuleLiquiditySeeker, LLMLiquiditySeeker
from masim.agents.long_horizon_investor import RuleLongHorizonInvestor, LLMLongHorizonInvestor
from masim.agents.long_term_investor import RuleLongTermInvestor, LLMLongTermInvestor
from masim.agents.long_vol_hedger import RuleLongVolHedger, LLMLongVolHedger
from masim.agents.loss_averse import RuleLossAverse, LLMLossAverse
from masim.agents.loss_averse_investor import RuleLossAverseInvestor, LLMLossAverseInvestor
from masim.agents.loss_frame_reactor import RuleLossFrameReactor, LLMLossFrameReactor
from masim.agents.macro_hedge_fund import RuleMacroHedgeFund, LLMMacroHedgeFund
from masim.agents.market_maker import RuleMarketMaker, LLMMarketMaker
from masim.agents.market_maker_gamma import RuleMarketMakerGamma, LLMMarketMakerGamma
from masim.agents.mbs_originator import RuleMbsOriginator, LLMMbsOriginator
from masim.agents.media_influenced_trader import RuleMediaInfluencedTrader, LLMMediaInfluencedTrader
from masim.agents.mental_accountant import RuleMentalAccountant, LLMMentalAccountant
from masim.agents.minsky_borrower import RuleMinskyBorrower, LLMMinskyBorrower
from masim.agents.momentum_buyer import RuleMomentumBuyer, LLMMomentumBuyer
from masim.agents.momentum_chaser import RuleMomentumChaser, LLMMomentumChaser
from masim.agents.momentum_follower import RuleMomentumFollower, LLMMomentumFollower
from masim.agents.momentum_investor import RuleMomentumInvestor, LLMMomentumInvestor
from masim.agents.momentum_retail import RuleMomentumRetail, LLMMomentumRetail
from masim.agents.momentum_speculator import RuleMomentumSpeculator, LLMMomentumSpeculator
from masim.agents.momentum_trader import RuleMomentumTrader, LLMMomentumTrader
from masim.agents.myopic_loss_averse import RuleMyopicLossAverse, LLMMyopicLossAverse
from masim.agents.myopic_loss_averse_investor import RuleMyopicLossAverseInvestor, LLMMyopicLossAverseInvestor
from masim.agents.narrative_believer import RuleNarrativeBeliever, LLMNarrativeBeliever
from masim.agents.new_buyer import RuleNewBuyer, LLMNewBuyer
from masim.agents.new_economy_evangelist import RuleNewEconomyEvangelist, LLMNewEconomyEvangelist
from masim.agents.noise_trader import RuleNoiseTrader, LLMNoiseTrader
from masim.agents.opinion_distorting_relayer import RuleOpinionDistortingRelayer, LLMOpinionDistortingRelayer
from masim.agents.opinion_environment import RuleOpinionEnvironment, LLMOpinionEnvironment
from masim.agents.opinion_fact_checker import RuleOpinionFactChecker, LLMOpinionFactChecker
from masim.agents.opinion_gullible_spreader import RuleOpinionGullibleSpreader, LLMOpinionGullibleSpreader
from masim.agents.opinion_skeptical_evaluator import RuleOpinionSkepticalEvaluator, LLMOpinionSkepticalEvaluator
from masim.agents.opinion_uninformed_bystander import RuleOpinionUninformedBystander, LLMOpinionUninformedBystander
from masim.agents.opportunistic_trader import RuleOpportunisticTrader, LLMOpportunisticTrader
from masim.agents.opportunity_cost_trader import RuleOpportunityCostTrader, LLMOpportunityCostTrader
from masim.agents.outcome_learner import RuleOutcomeLearner, LLMOutcomeLearner
from masim.agents.overconfident_trader import RuleOverconfidentTrader, LLMOverconfidentTrader
from masim.agents.panic_seller import RulePanicSeller, LLMPanicSeller
from masim.agents.passive_bystander import RulePassiveBystander, LLMPassiveBystander
from masim.agents.passive_follower import RulePassiveFollower, LLMPassiveFollower
from masim.agents.passive_investor import RulePassiveInvestor, LLMPassiveInvestor
from masim.agents.pattern_matcher import RulePatternMatcher, LLMPatternMatcher
from masim.agents.peg_defender import RulePegDefender, LLMPegDefender
from masim.agents.periphery_bond_seller import RulePeripheryBondSeller, LLMPeripheryBondSeller
from masim.agents.portfolio_insurer import RulePortfolioInsurer, LLMPortfolioInsurer
from masim.agents.prime_broker_delayed_liquidator import RulePrimeBrokerDelayedLiquidator, LLMPrimeBrokerDelayedLiquidator
from masim.agents.prime_broker_first_mover import RulePrimeBrokerFirstMover, LLMPrimeBrokerFirstMover
from masim.agents.pro_cyclical_lender import RuleProCyclicalLender, LLMProCyclicalLender
from masim.agents.process_evaluator import RuleProcessEvaluator, LLMProcessEvaluator
from masim.agents.program_trader import RuleProgramTrader, LLMProgramTrader
from masim.agents.rating_agency import RuleRatingAgency, LLMRatingAgency
from masim.agents.rational_arbitrageur import RuleRationalArbitrageur, LLMRationalArbitrageur
from masim.agents.rational_cutter import RuleRationalCutter, LLMRationalCutter
from masim.agents.rational_investor import RuleRationalInvestor, LLMRationalInvestor
from masim.agents.rational_optimizer import RuleRationalOptimizer, LLMRationalOptimizer
from masim.agents.rational_portfolio_manager import RuleRationalPortfolioManager, LLMRationalPortfolioManager
from masim.agents.rational_trader import RuleRationalTrader, LLMRationalTrader
from masim.agents.rational_updater import RuleRationalUpdater, LLMRationalUpdater
from masim.agents.recent_event_overweighter import RuleRecentEventOverweighter, LLMRecentEventOverweighter
from masim.agents.regulator import RuleRegulator, LLMRegulator
from masim.agents.reputation_herder import RuleReputationHerder, LLMReputationHerder
from masim.agents.retail_coordinated import RuleRetailCoordinated, LLMRetailCoordinated
from masim.agents.retail_coordinator import RuleRetailCoordinator, LLMRetailCoordinator
from masim.agents.retail_trader import RuleRetailTrader, LLMRetailTrader
from masim.agents.risk_averse_investor import RuleRiskAverseInvestor, LLMRiskAverseInvestor
from masim.agents.risk_averse_saver import RuleRiskAverseSaver, LLMRiskAverseSaver
from masim.agents.risk_manager import RuleRiskManager, LLMRiskManager
from masim.agents.risk_neutral_investor import RuleRiskNeutralInvestor, LLMRiskNeutralInvestor
from masim.agents.risk_parity_fund import RuleRiskParityFund, LLMRiskParityFund
from masim.agents.selective_scanner import RuleSelectiveScanner, LLMSelectiveScanner
from masim.agents.self_attributor import RuleSelfAttributor, LLMSelfAttributor
from masim.agents.self_fulfilling_trader import RuleSelfFulfillingTrader, LLMSelfFulfillingTrader
from masim.agents.sentiment_trader import RuleSentimentTrader, LLMSentimentTrader
from masim.agents.short_seller import RuleShortSeller, LLMShortSeller
from masim.agents.short_seller_hf import RuleShortSellerHf, LLMShortSellerHf
from masim.agents.short_vol_trader import RuleShortVolTrader, LLMShortVolTrader
from masim.agents.skeptical_analyst import RuleSkepticalAnalyst, LLMSkepticalAnalyst
from masim.agents.skeptical_evaluator import RuleSkepticalEvaluator, LLMSkepticalEvaluator
from masim.agents.skeptical_value_investor import RuleSkepticalValueInvestor, LLMSkepticalValueInvestor
from masim.agents.slow_adapter import RuleSlowAdapter, LLMSlowAdapter
from masim.agents.social_media_influencer import RuleSocialMediaInfluencer, LLMSocialMediaInfluencer
from masim.agents.social_proof_follower import RuleSocialProofFollower, LLMSocialProofFollower
from masim.agents.speculative_attacker import RuleSpeculativeAttacker, LLMSpeculativeAttacker
from masim.agents.stablecoin_holder import RuleStablecoinHolder, LLMStablecoinHolder
from masim.agents.status_quo_seller import RuleStatusQuoSeller, LLMStatusQuoSeller
from masim.agents.stop_loss_trader import RuleStopLossTrader, LLMStopLossTrader
from masim.agents.streak_reversal_trader import RuleStreakReversalTrader, LLMStreakReversalTrader
from masim.agents.sunk_cost_holder import RuleSunkCostHolder, LLMSunkCostHolder
from masim.agents.systematic_analyst import RuleSystematicAnalyst, LLMSystematicAnalyst
from masim.agents.tax_aware_investor import RuleTaxAwareInvestor, LLMTaxAwareInvestor
from masim.agents.technical_trader import RuleTechnicalTrader, LLMTechnicalTrader
from masim.agents.trend_chaser import RuleTrendChaser, LLMTrendChaser
from masim.agents.trend_follower import RuleTrendFollower, LLMTrendFollower
from masim.agents.uninformed_bystander import RuleUninformedBystander, LLMUninformedBystander
from masim.agents.value_buyer import RuleValueBuyer, LLMValueBuyer
from masim.agents.value_contrarian import RuleValueContrarian, LLMValueContrarian
from masim.agents.value_investor import RuleValueInvestor, LLMValueInvestor
from masim.agents.value_trader import RuleValueTrader, LLMValueTrader
from masim.agents.vol_arbitrageur import RuleVolArbitrageur, LLMVolArbitrageur
from masim.agents.vol_etn_manager import RuleVolEtnManager, LLMVolEtnManager
from masim.agents.volatility_trader import RuleVolatilityTrader, LLMVolatilityTrader


REGISTRY: dict[str, tuple[type, type]] = {
    "active-rebalancer": (RuleActiveRebalancer, LLMActiveRebalancer),
    "aggressive-investor": (RuleAggressiveInvestor, LLMAggressiveInvestor),
    "algorithmic-trader": (RuleAlgorithmicTrader, LLMAlgorithmicTrader),
    "anchor-depositor": (RuleAnchorDepositor, LLMAnchorDepositor),
    "anchored-trader": (RuleAnchoredTrader, LLMAnchoredTrader),
    "arbitrage-framer": (RuleArbitrageFramer, LLMArbitrageFramer),
    "arbitrageur": (RuleArbitrageur, LLMArbitrageur),
    "balanced-analyst": (RuleBalancedAnalyst, LLMBalancedAnalyst),
    "bank-manager": (RuleBankManager, LLMBankManager),
    "bayesian-updater": (RuleBayesianUpdater, LLMBayesianUpdater),
    "belief-anchor": (RuleBeliefAnchor, LLMBeliefAnchor),
    "block-trade-buyer": (RuleBlockTradeBuyer, LLMBlockTradeBuyer),
    "bond-trader": (RuleBondTrader, LLMBondTrader),
    "bottom-fisher": (RuleBottomFisher, LLMBottomFisher),
    "break-even-trader": (RuleBreakEvenTrader, LLMBreakEvenTrader),
    "bridge-builder": (RuleBridgeBuilder, LLMBridgeBuilder),
    "calibrated-trader": (RuleCalibratedTrader, LLMCalibratedTrader),
    "carry-trader": (RuleCarryTrader, LLMCarryTrader),
    "cascade-follower": (RuleCascadeFollower, LLMCascadeFollower),
    "category-overgeneralizer": (RuleCategoryOvergeneralizer, LLMCategoryOvergeneralizer),
    "central-bank": (RuleCentralBank, LLMCentralBank),
    "central-bank-defender": (RuleCentralBankDefender, LLMCentralBankDefender),
    "commitment-escalator": (RuleCommitmentEscalator, LLMCommitmentEscalator),
    "concentrated-fund": (RuleConcentratedFund, LLMConcentratedFund),
    "conformist": (RuleConformist, LLMConformist),
    "conservative-holder": (RuleConservativeHolder, LLMConservativeHolder),
    "conservative-investor": (RuleConservativeInvestor, LLMConservativeInvestor),
    "contagion-trader": (RuleContagionTrader, LLMContagionTrader),
    "contrarian": (RuleContrarian, LLMContrarian),
    "contrarian-investor": (RuleContrarianInvestor, LLMContrarianInvestor),
    "contrarian-skeptic": (RuleContrarianSkeptic, LLMContrarianSkeptic),
    "contrarian-statistical": (RuleContrarianStatistical, LLMContrarianStatistical),
    "contrarian-trader": (RuleContrarianTrader, LLMContrarianTrader),
    "convergence-arbitrageur": (RuleConvergenceArbitrageur, LLMConvergenceArbitrageur),
    "convergence-trader": (RuleConvergenceTrader, LLMConvergenceTrader),
    "core-bond-buyer": (RuleCoreBondBuyer, LLMCoreBondBuyer),
    "counter-cyclical-lender": (RuleCounterCyclicalLender, LLMCounterCyclicalLender),
    "creditor-panicker": (RuleCreditorPanicker, LLMCreditorPanicker),
    "critical-thinker": (RuleCriticalThinker, LLMCriticalThinker),
    "de-fi-lender": (RuleDeFiLender, LLMDeFiLender),
    "default-follower": (RuleDefaultFollower, LLMDefaultFollower),
    "depositor": (RuleDepositor, LLMDepositor),
    "disposition-investor": (RuleDispositionInvestor, LLMDispositionInvestor),
    "disposition-trader": (RuleDispositionTrader, LLMDispositionTrader),
    "distorting-relayer": (RuleDistortingRelayer, LLMDistortingRelayer),
    "distressed-buyer": (RuleDistressedBuyer, LLMDistressedBuyer),
    "early-exit-trader": (RuleEarlyExitTrader, LLMEarlyExitTrader),
    "ecb-intervenor": (RuleEcbIntervenor, LLMEcbIntervenor),
    "endowed-holder": (RuleEndowedHolder, LLMEndowedHolder),
    "equity-trader": (RuleEquityTrader, LLMEquityTrader),
    "fact-checker": (RuleFactChecker, LLMFactChecker),
    "flash-market-maker": (RuleFlashMarketMaker, LLMFlashMarketMaker),
    "forced-seller": (RuleForcedSeller, LLMForcedSeller),
    "frame-invariant-trader": (RuleFrameInvariantTrader, LLMFrameInvariantTrader),
    "fundamental-analyst": (RuleFundamentalAnalyst, LLMFundamentalAnalyst),
    "fundamental-anchor": (RuleFundamentalAnchor, LLMFundamentalAnchor),
    "fundamental-hedger": (RuleFundamentalHedger, LLMFundamentalHedger),
    "fundamental-investor": (RuleFundamentalInvestor, LLMFundamentalInvestor),
    "fundamental-trader": (RuleFundamentalTrader, LLMFundamentalTrader),
    "fundamentalist": (RuleFundamentalist, LLMFundamentalist),
    "funding-currency-buyer": (RuleFundingCurrencyBuyer, LLMFundingCurrencyBuyer),
    "gain-frame-follower": (RuleGainFrameFollower, LLMGainFrameFollower),
    "greater-fool-speculator": (RuleGreaterFoolSpeculator, LLMGreaterFoolSpeculator),
    "gullible-spreader": (RuleGullibleSpreader, LLMGullibleSpreader),
    "hedged-carry-trader": (RuleHedgedCarryTrader, LLMHedgedCarryTrader),
    "hedged-fund": (RuleHedgedFund, LLMHedgedFund),
    "hft-market-maker": (RuleHftMarketMaker, LLMHftMarketMaker),
    "high-frequency-trader": (RuleHighFrequencyTrader, LLMHighFrequencyTrader),
    "hindsight-overconfident": (RuleHindsightOverconfident, LLMHindsightOverconfident),
    "historical-anchor": (RuleHistoricalAnchor, LLMHistoricalAnchor),
    "hot-hand-trader": (RuleHotHandTrader, LLMHotHandTrader),
    "hot-money-funder": (RuleHotMoneyFunder, LLMHotMoneyFunder),
    "house-money-trader": (RuleHouseMoneyTrader, LLMHouseMoneyTrader),
    "ideologue": (RuleIdeologue, LLMIdeologue),
    "imf-rescuer": (RuleImfRescuer, LLMImfRescuer),
    "independent-assessor": (RuleIndependentAssessor, LLMIndependentAssessor),
    "independent-thinker": (RuleIndependentThinker, LLMIndependentThinker),
    "index-arbitrageur": (RuleIndexArbitrageur, LLMIndexArbitrageur),
    "index-fund": (RuleIndexFund, LLMIndexFund),
    "index-holder": (RuleIndexHolder, LLMIndexHolder),
    "index-tracker": (RuleIndexTracker, LLMIndexTracker),
    "inertial-holder": (RuleInertialHolder, LLMInertialHolder),
    "information-environment": (RuleInformationEnvironment, LLMInformationEnvironment),
    "information-trader": (RuleInformationTrader, LLMInformationTrader),
    "insider-advantaged": (RuleInsiderAdvantaged, LLMInsiderAdvantaged),
    "institutional-holder": (RuleInstitutionalHolder, LLMInstitutionalHolder),
    "institutional-investor": (RuleInstitutionalInvestor, LLMInstitutionalInvestor),
    "institutional-value": (RuleInstitutionalValue, LLMInstitutionalValue),
    "intrinsic-value-trader": (RuleIntrinsicValueTrader, LLMIntrinsicValueTrader),
    "ipo-flipper": (RuleIpoFlipper, LLMIpoFlipper),
    "leverage-trader": (RuleLeverageTrader, LLMLeverageTrader),
    "leveraged-buyer": (RuleLeveragedBuyer, LLMLeveragedBuyer),
    "leveraged-carry-fund": (RuleLeveragedCarryFund, LLMLeveragedCarryFund),
    "leveraged-fund": (RuleLeveragedFund, LLMLeveragedFund),
    "leveraged-hedge-fund": (RuleLeveragedHedgeFund, LLMLeveragedHedgeFund),
    "leveraged-investor": (RuleLeveragedInvestor, LLMLeveragedInvestor),
    "leveraged-speculator": (RuleLeveragedSpeculator, LLMLeveragedSpeculator),
    "liquidity-demander": (RuleLiquidityDemander, LLMLiquidityDemander),
    "liquidity-provider": (RuleLiquidityProvider, LLMLiquidityProvider),
    "liquidity-seeker": (RuleLiquiditySeeker, LLMLiquiditySeeker),
    "long-horizon-investor": (RuleLongHorizonInvestor, LLMLongHorizonInvestor),
    "long-term-investor": (RuleLongTermInvestor, LLMLongTermInvestor),
    "long-vol-hedger": (RuleLongVolHedger, LLMLongVolHedger),
    "loss-averse": (RuleLossAverse, LLMLossAverse),
    "loss-averse-investor": (RuleLossAverseInvestor, LLMLossAverseInvestor),
    "loss-frame-reactor": (RuleLossFrameReactor, LLMLossFrameReactor),
    "macro-hedge-fund": (RuleMacroHedgeFund, LLMMacroHedgeFund),
    "market-maker": (RuleMarketMaker, LLMMarketMaker),
    "market-maker-gamma": (RuleMarketMakerGamma, LLMMarketMakerGamma),
    "mbs-originator": (RuleMbsOriginator, LLMMbsOriginator),
    "media-influenced-trader": (RuleMediaInfluencedTrader, LLMMediaInfluencedTrader),
    "mental-accountant": (RuleMentalAccountant, LLMMentalAccountant),
    "minsky-borrower": (RuleMinskyBorrower, LLMMinskyBorrower),
    "momentum-buyer": (RuleMomentumBuyer, LLMMomentumBuyer),
    "momentum-chaser": (RuleMomentumChaser, LLMMomentumChaser),
    "momentum-follower": (RuleMomentumFollower, LLMMomentumFollower),
    "momentum-investor": (RuleMomentumInvestor, LLMMomentumInvestor),
    "momentum-retail": (RuleMomentumRetail, LLMMomentumRetail),
    "momentum-speculator": (RuleMomentumSpeculator, LLMMomentumSpeculator),
    "momentum-trader": (RuleMomentumTrader, LLMMomentumTrader),
    "myopic-loss-averse": (RuleMyopicLossAverse, LLMMyopicLossAverse),
    "myopic-loss-averse-investor": (RuleMyopicLossAverseInvestor, LLMMyopicLossAverseInvestor),
    "narrative-believer": (RuleNarrativeBeliever, LLMNarrativeBeliever),
    "new-buyer": (RuleNewBuyer, LLMNewBuyer),
    "new-economy-evangelist": (RuleNewEconomyEvangelist, LLMNewEconomyEvangelist),
    "noise-trader": (RuleNoiseTrader, LLMNoiseTrader),
    "opinion-distorting-relayer": (RuleOpinionDistortingRelayer, LLMOpinionDistortingRelayer),
    "opinion-environment": (RuleOpinionEnvironment, LLMOpinionEnvironment),
    "opinion-fact-checker": (RuleOpinionFactChecker, LLMOpinionFactChecker),
    "opinion-gullible-spreader": (RuleOpinionGullibleSpreader, LLMOpinionGullibleSpreader),
    "opinion-skeptical-evaluator": (RuleOpinionSkepticalEvaluator, LLMOpinionSkepticalEvaluator),
    "opinion-uninformed-bystander": (RuleOpinionUninformedBystander, LLMOpinionUninformedBystander),
    "opportunistic-trader": (RuleOpportunisticTrader, LLMOpportunisticTrader),
    "opportunity-cost-trader": (RuleOpportunityCostTrader, LLMOpportunityCostTrader),
    "outcome-learner": (RuleOutcomeLearner, LLMOutcomeLearner),
    "overconfident-trader": (RuleOverconfidentTrader, LLMOverconfidentTrader),
    "panic-seller": (RulePanicSeller, LLMPanicSeller),
    "passive-bystander": (RulePassiveBystander, LLMPassiveBystander),
    "passive-follower": (RulePassiveFollower, LLMPassiveFollower),
    "passive-investor": (RulePassiveInvestor, LLMPassiveInvestor),
    "pattern-matcher": (RulePatternMatcher, LLMPatternMatcher),
    "peg-defender": (RulePegDefender, LLMPegDefender),
    "periphery-bond-seller": (RulePeripheryBondSeller, LLMPeripheryBondSeller),
    "portfolio-insurer": (RulePortfolioInsurer, LLMPortfolioInsurer),
    "prime-broker-delayed-liquidator": (RulePrimeBrokerDelayedLiquidator, LLMPrimeBrokerDelayedLiquidator),
    "prime-broker-first-mover": (RulePrimeBrokerFirstMover, LLMPrimeBrokerFirstMover),
    "pro-cyclical-lender": (RuleProCyclicalLender, LLMProCyclicalLender),
    "process-evaluator": (RuleProcessEvaluator, LLMProcessEvaluator),
    "program-trader": (RuleProgramTrader, LLMProgramTrader),
    "rating-agency": (RuleRatingAgency, LLMRatingAgency),
    "rational-arbitrageur": (RuleRationalArbitrageur, LLMRationalArbitrageur),
    "rational-cutter": (RuleRationalCutter, LLMRationalCutter),
    "rational-investor": (RuleRationalInvestor, LLMRationalInvestor),
    "rational-optimizer": (RuleRationalOptimizer, LLMRationalOptimizer),
    "rational-portfolio-manager": (RuleRationalPortfolioManager, LLMRationalPortfolioManager),
    "rational-trader": (RuleRationalTrader, LLMRationalTrader),
    "rational-updater": (RuleRationalUpdater, LLMRationalUpdater),
    "recent-event-overweighter": (RuleRecentEventOverweighter, LLMRecentEventOverweighter),
    "regulator": (RuleRegulator, LLMRegulator),
    "reputation-herder": (RuleReputationHerder, LLMReputationHerder),
    "retail-coordinated": (RuleRetailCoordinated, LLMRetailCoordinated),
    "retail-coordinator": (RuleRetailCoordinator, LLMRetailCoordinator),
    "retail-trader": (RuleRetailTrader, LLMRetailTrader),
    "risk-averse-investor": (RuleRiskAverseInvestor, LLMRiskAverseInvestor),
    "risk-averse-saver": (RuleRiskAverseSaver, LLMRiskAverseSaver),
    "risk-manager": (RuleRiskManager, LLMRiskManager),
    "risk-neutral-investor": (RuleRiskNeutralInvestor, LLMRiskNeutralInvestor),
    "risk-parity-fund": (RuleRiskParityFund, LLMRiskParityFund),
    "selective-scanner": (RuleSelectiveScanner, LLMSelectiveScanner),
    "self-attributor": (RuleSelfAttributor, LLMSelfAttributor),
    "self-fulfilling-trader": (RuleSelfFulfillingTrader, LLMSelfFulfillingTrader),
    "sentiment-trader": (RuleSentimentTrader, LLMSentimentTrader),
    "short-seller": (RuleShortSeller, LLMShortSeller),
    "short-seller-hf": (RuleShortSellerHf, LLMShortSellerHf),
    "short-vol-trader": (RuleShortVolTrader, LLMShortVolTrader),
    "skeptical-analyst": (RuleSkepticalAnalyst, LLMSkepticalAnalyst),
    "skeptical-evaluator": (RuleSkepticalEvaluator, LLMSkepticalEvaluator),
    "skeptical-value-investor": (RuleSkepticalValueInvestor, LLMSkepticalValueInvestor),
    "slow-adapter": (RuleSlowAdapter, LLMSlowAdapter),
    "social-media-influencer": (RuleSocialMediaInfluencer, LLMSocialMediaInfluencer),
    "social-proof-follower": (RuleSocialProofFollower, LLMSocialProofFollower),
    "speculative-attacker": (RuleSpeculativeAttacker, LLMSpeculativeAttacker),
    "stablecoin-holder": (RuleStablecoinHolder, LLMStablecoinHolder),
    "status-quo-seller": (RuleStatusQuoSeller, LLMStatusQuoSeller),
    "stop-loss-trader": (RuleStopLossTrader, LLMStopLossTrader),
    "streak-reversal-trader": (RuleStreakReversalTrader, LLMStreakReversalTrader),
    "sunk-cost-holder": (RuleSunkCostHolder, LLMSunkCostHolder),
    "systematic-analyst": (RuleSystematicAnalyst, LLMSystematicAnalyst),
    "tax-aware-investor": (RuleTaxAwareInvestor, LLMTaxAwareInvestor),
    "technical-trader": (RuleTechnicalTrader, LLMTechnicalTrader),
    "trend-chaser": (RuleTrendChaser, LLMTrendChaser),
    "trend-follower": (RuleTrendFollower, LLMTrendFollower),
    "uninformed-bystander": (RuleUninformedBystander, LLMUninformedBystander),
    "value-buyer": (RuleValueBuyer, LLMValueBuyer),
    "value-contrarian": (RuleValueContrarian, LLMValueContrarian),
    "value-investor": (RuleValueInvestor, LLMValueInvestor),
    "value-trader": (RuleValueTrader, LLMValueTrader),
    "vol-arbitrageur": (RuleVolArbitrageur, LLMVolArbitrageur),
    "vol-etn-manager": (RuleVolEtnManager, LLMVolEtnManager),
    "volatility-trader": (RuleVolatilityTrader, LLMVolatilityTrader),
}

# ---------------------------------------------------------------------------
# Market coordinator imports
# ---------------------------------------------------------------------------

from masim.agents.market_stock_standard_price_impact import MarketStockStandardPriceImpact
from masim.agents.market_opinion_echo_chamber_clustering import MarketOpinionEchoChamberClustering
from masim.agents.market_information_sis_contagion import MarketInformationSisContagion
from masim.agents.market_fx_currency_peg_and_attack import MarketFxCurrencyPegAndAttack
from masim.agents.market_bond_yield_spread_inverse import MarketBondYieldSpreadInverse
from masim.agents.market_crypto_algostable_depeg import MarketCryptoAlgostableDepeg
from masim.agents.market_derivatives_vol_feedback import MarketDerivativesVolFeedback
from masim.agents.market_deposit_bank_run_diamond_dybvig import MarketDepositBankRunDiamondDybvig
from masim.agents.market_credit_minsky_cycle import MarketCreditMinskyCycle

COORDINATOR_REGISTRY: dict[str, type] = {
    "stock-standard-price-impact": MarketStockStandardPriceImpact,
    "opinion-echo-chamber-clustering": MarketOpinionEchoChamberClustering,
    "information-sis-contagion": MarketInformationSisContagion,
    "fx-currency-peg-and-attack": MarketFxCurrencyPegAndAttack,
    "bond-yield-spread-inverse": MarketBondYieldSpreadInverse,
    "crypto-algostable-depeg": MarketCryptoAlgostableDepeg,
    "derivatives-vol-feedback": MarketDerivativesVolFeedback,
    "deposit-bank-run-diamond-dybvig": MarketDepositBankRunDiamondDybvig,
    "credit-minsky-cycle": MarketCreditMinskyCycle,
}


def get_coordinator(archetype: str) -> type:
    """Look up a canonical market coordinator class by kebab stem."""
    if archetype not in COORDINATOR_REGISTRY:
        raise KeyError(
            f"Unknown coordinator archetype {archetype!r}. Known: "
            f"{sorted(COORDINATOR_REGISTRY)}"
        )
    return COORDINATOR_REGISTRY[archetype]


def get_agent(archetype: str, engine: str = "Rule") -> type:
    """Look up a canonical agent class by kebab stem and engine."""
    if archetype not in REGISTRY:
        raise KeyError(
            f"Unknown canonical archetype {archetype!r}. Known: "
            f"{sorted(REGISTRY)}"
        )
    rule_cls, llm_cls = REGISTRY[archetype]
    if engine == "Rule":
        return rule_cls
    if engine == "LLM":
        return llm_cls
    raise ValueError(f"engine must be 'Rule' or 'LLM', got {engine!r}")


__all__ = [
    "StandardMarketState",
    "CanonicalRulePlayer",
    "CanonicalLLMPlayer",
    "CanonicalMarketCoordinator",
    "REGISTRY",
    "COORDINATOR_REGISTRY",
    "get_agent",
    "get_coordinator",
    "MarketStockStandardPriceImpact",
    "MarketOpinionEchoChamberClustering",
    "MarketInformationSisContagion",
    "MarketFxCurrencyPegAndAttack",
    "MarketBondYieldSpreadInverse",
    "MarketCryptoAlgostableDepeg",
    "MarketDerivativesVolFeedback",
    "MarketDepositBankRunDiamondDybvig",
    "MarketCreditMinskyCycle",
    "RuleActiveRebalancer",
    "RuleAggressiveInvestor",
    "RuleAlgorithmicTrader",
    "RuleAnchorDepositor",
    "RuleAnchoredTrader",
    "RuleArbitrageFramer",
    "RuleArbitrageur",
    "RuleBalancedAnalyst",
    "RuleBankManager",
    "RuleBayesianUpdater",
    "RuleBeliefAnchor",
    "RuleBlockTradeBuyer",
    "RuleBondTrader",
    "RuleBottomFisher",
    "RuleBreakEvenTrader",
    "RuleBridgeBuilder",
    "RuleCalibratedTrader",
    "RuleCarryTrader",
    "RuleCascadeFollower",
    "RuleCategoryOvergeneralizer",
    "RuleCentralBank",
    "RuleCentralBankDefender",
    "RuleCommitmentEscalator",
    "RuleConcentratedFund",
    "RuleConformist",
    "RuleConservativeHolder",
    "RuleConservativeInvestor",
    "RuleContagionTrader",
    "RuleContrarian",
    "RuleContrarianInvestor",
    "RuleContrarianSkeptic",
    "RuleContrarianStatistical",
    "RuleContrarianTrader",
    "RuleConvergenceArbitrageur",
    "RuleConvergenceTrader",
    "RuleCoreBondBuyer",
    "RuleCounterCyclicalLender",
    "RuleCreditorPanicker",
    "RuleCriticalThinker",
    "RuleDeFiLender",
    "RuleDefaultFollower",
    "RuleDepositor",
    "RuleDispositionInvestor",
    "RuleDispositionTrader",
    "RuleDistortingRelayer",
    "RuleDistressedBuyer",
    "RuleEarlyExitTrader",
    "RuleEcbIntervenor",
    "RuleEndowedHolder",
    "RuleEquityTrader",
    "RuleFactChecker",
    "RuleFlashMarketMaker",
    "RuleForcedSeller",
    "RuleFrameInvariantTrader",
    "RuleFundamentalAnalyst",
    "RuleFundamentalAnchor",
    "RuleFundamentalHedger",
    "RuleFundamentalInvestor",
    "RuleFundamentalTrader",
    "RuleFundamentalist",
    "RuleFundingCurrencyBuyer",
    "RuleGainFrameFollower",
    "RuleGreaterFoolSpeculator",
    "RuleGullibleSpreader",
    "RuleHedgedCarryTrader",
    "RuleHedgedFund",
    "RuleHftMarketMaker",
    "RuleHighFrequencyTrader",
    "RuleHindsightOverconfident",
    "RuleHistoricalAnchor",
    "RuleHotHandTrader",
    "RuleHotMoneyFunder",
    "RuleHouseMoneyTrader",
    "RuleIdeologue",
    "RuleImfRescuer",
    "RuleIndependentAssessor",
    "RuleIndependentThinker",
    "RuleIndexArbitrageur",
    "RuleIndexFund",
    "RuleIndexHolder",
    "RuleIndexTracker",
    "RuleInertialHolder",
    "RuleInformationEnvironment",
    "RuleInformationTrader",
    "RuleInsiderAdvantaged",
    "RuleInstitutionalHolder",
    "RuleInstitutionalInvestor",
    "RuleInstitutionalValue",
    "RuleIntrinsicValueTrader",
    "RuleIpoFlipper",
    "RuleLeverageTrader",
    "RuleLeveragedBuyer",
    "RuleLeveragedCarryFund",
    "RuleLeveragedFund",
    "RuleLeveragedHedgeFund",
    "RuleLeveragedInvestor",
    "RuleLeveragedSpeculator",
    "RuleLiquidityDemander",
    "RuleLiquidityProvider",
    "RuleLiquiditySeeker",
    "RuleLongHorizonInvestor",
    "RuleLongTermInvestor",
    "RuleLongVolHedger",
    "RuleLossAverse",
    "RuleLossAverseInvestor",
    "RuleLossFrameReactor",
    "RuleMacroHedgeFund",
    "RuleMarketMaker",
    "RuleMarketMakerGamma",
    "RuleMbsOriginator",
    "RuleMediaInfluencedTrader",
    "RuleMentalAccountant",
    "RuleMinskyBorrower",
    "RuleMomentumBuyer",
    "RuleMomentumChaser",
    "RuleMomentumFollower",
    "RuleMomentumInvestor",
    "RuleMomentumRetail",
    "RuleMomentumSpeculator",
    "RuleMomentumTrader",
    "RuleMyopicLossAverse",
    "RuleMyopicLossAverseInvestor",
    "RuleNarrativeBeliever",
    "RuleNewBuyer",
    "RuleNewEconomyEvangelist",
    "RuleNoiseTrader",
    "RuleOpinionDistortingRelayer",
    "RuleOpinionEnvironment",
    "RuleOpinionFactChecker",
    "RuleOpinionGullibleSpreader",
    "RuleOpinionSkepticalEvaluator",
    "RuleOpinionUninformedBystander",
    "RuleOpportunisticTrader",
    "RuleOpportunityCostTrader",
    "RuleOutcomeLearner",
    "RuleOverconfidentTrader",
    "RulePanicSeller",
    "RulePassiveBystander",
    "RulePassiveFollower",
    "RulePassiveInvestor",
    "RulePatternMatcher",
    "RulePegDefender",
    "RulePeripheryBondSeller",
    "RulePortfolioInsurer",
    "RulePrimeBrokerDelayedLiquidator",
    "RulePrimeBrokerFirstMover",
    "RuleProCyclicalLender",
    "RuleProcessEvaluator",
    "RuleProgramTrader",
    "RuleRatingAgency",
    "RuleRationalArbitrageur",
    "RuleRationalCutter",
    "RuleRationalInvestor",
    "RuleRationalOptimizer",
    "RuleRationalPortfolioManager",
    "RuleRationalTrader",
    "RuleRationalUpdater",
    "RuleRecentEventOverweighter",
    "RuleRegulator",
    "RuleReputationHerder",
    "RuleRetailCoordinated",
    "RuleRetailCoordinator",
    "RuleRetailTrader",
    "RuleRiskAverseInvestor",
    "RuleRiskAverseSaver",
    "RuleRiskManager",
    "RuleRiskNeutralInvestor",
    "RuleRiskParityFund",
    "RuleSelectiveScanner",
    "RuleSelfAttributor",
    "RuleSelfFulfillingTrader",
    "RuleSentimentTrader",
    "RuleShortSeller",
    "RuleShortSellerHf",
    "RuleShortVolTrader",
    "RuleSkepticalAnalyst",
    "RuleSkepticalEvaluator",
    "RuleSkepticalValueInvestor",
    "RuleSlowAdapter",
    "RuleSocialMediaInfluencer",
    "RuleSocialProofFollower",
    "RuleSpeculativeAttacker",
    "RuleStablecoinHolder",
    "RuleStatusQuoSeller",
    "RuleStopLossTrader",
    "RuleStreakReversalTrader",
    "RuleSunkCostHolder",
    "RuleSystematicAnalyst",
    "RuleTaxAwareInvestor",
    "RuleTechnicalTrader",
    "RuleTrendChaser",
    "RuleTrendFollower",
    "RuleUninformedBystander",
    "RuleValueBuyer",
    "RuleValueContrarian",
    "RuleValueInvestor",
    "RuleValueTrader",
    "RuleVolArbitrageur",
    "RuleVolEtnManager",
    "RuleVolatilityTrader",
    "LLMActiveRebalancer",
    "LLMAggressiveInvestor",
    "LLMAlgorithmicTrader",
    "LLMAnchorDepositor",
    "LLMAnchoredTrader",
    "LLMArbitrageFramer",
    "LLMArbitrageur",
    "LLMBalancedAnalyst",
    "LLMBankManager",
    "LLMBayesianUpdater",
    "LLMBeliefAnchor",
    "LLMBlockTradeBuyer",
    "LLMBondTrader",
    "LLMBottomFisher",
    "LLMBreakEvenTrader",
    "LLMBridgeBuilder",
    "LLMCalibratedTrader",
    "LLMCarryTrader",
    "LLMCascadeFollower",
    "LLMCategoryOvergeneralizer",
    "LLMCentralBank",
    "LLMCentralBankDefender",
    "LLMCommitmentEscalator",
    "LLMConcentratedFund",
    "LLMConformist",
    "LLMConservativeHolder",
    "LLMConservativeInvestor",
    "LLMContagionTrader",
    "LLMContrarian",
    "LLMContrarianInvestor",
    "LLMContrarianSkeptic",
    "LLMContrarianStatistical",
    "LLMContrarianTrader",
    "LLMConvergenceArbitrageur",
    "LLMConvergenceTrader",
    "LLMCoreBondBuyer",
    "LLMCounterCyclicalLender",
    "LLMCreditorPanicker",
    "LLMCriticalThinker",
    "LLMDeFiLender",
    "LLMDefaultFollower",
    "LLMDepositor",
    "LLMDispositionInvestor",
    "LLMDispositionTrader",
    "LLMDistortingRelayer",
    "LLMDistressedBuyer",
    "LLMEarlyExitTrader",
    "LLMEcbIntervenor",
    "LLMEndowedHolder",
    "LLMEquityTrader",
    "LLMFactChecker",
    "LLMFlashMarketMaker",
    "LLMForcedSeller",
    "LLMFrameInvariantTrader",
    "LLMFundamentalAnalyst",
    "LLMFundamentalAnchor",
    "LLMFundamentalHedger",
    "LLMFundamentalInvestor",
    "LLMFundamentalTrader",
    "LLMFundamentalist",
    "LLMFundingCurrencyBuyer",
    "LLMGainFrameFollower",
    "LLMGreaterFoolSpeculator",
    "LLMGullibleSpreader",
    "LLMHedgedCarryTrader",
    "LLMHedgedFund",
    "LLMHftMarketMaker",
    "LLMHighFrequencyTrader",
    "LLMHindsightOverconfident",
    "LLMHistoricalAnchor",
    "LLMHotHandTrader",
    "LLMHotMoneyFunder",
    "LLMHouseMoneyTrader",
    "LLMIdeologue",
    "LLMImfRescuer",
    "LLMIndependentAssessor",
    "LLMIndependentThinker",
    "LLMIndexArbitrageur",
    "LLMIndexFund",
    "LLMIndexHolder",
    "LLMIndexTracker",
    "LLMInertialHolder",
    "LLMInformationEnvironment",
    "LLMInformationTrader",
    "LLMInsiderAdvantaged",
    "LLMInstitutionalHolder",
    "LLMInstitutionalInvestor",
    "LLMInstitutionalValue",
    "LLMIntrinsicValueTrader",
    "LLMIpoFlipper",
    "LLMLeverageTrader",
    "LLMLeveragedBuyer",
    "LLMLeveragedCarryFund",
    "LLMLeveragedFund",
    "LLMLeveragedHedgeFund",
    "LLMLeveragedInvestor",
    "LLMLeveragedSpeculator",
    "LLMLiquidityDemander",
    "LLMLiquidityProvider",
    "LLMLiquiditySeeker",
    "LLMLongHorizonInvestor",
    "LLMLongTermInvestor",
    "LLMLongVolHedger",
    "LLMLossAverse",
    "LLMLossAverseInvestor",
    "LLMLossFrameReactor",
    "LLMMacroHedgeFund",
    "LLMMarketMaker",
    "LLMMarketMakerGamma",
    "LLMMbsOriginator",
    "LLMMediaInfluencedTrader",
    "LLMMentalAccountant",
    "LLMMinskyBorrower",
    "LLMMomentumBuyer",
    "LLMMomentumChaser",
    "LLMMomentumFollower",
    "LLMMomentumInvestor",
    "LLMMomentumRetail",
    "LLMMomentumSpeculator",
    "LLMMomentumTrader",
    "LLMMyopicLossAverse",
    "LLMMyopicLossAverseInvestor",
    "LLMNarrativeBeliever",
    "LLMNewBuyer",
    "LLMNewEconomyEvangelist",
    "LLMNoiseTrader",
    "LLMOpinionDistortingRelayer",
    "LLMOpinionEnvironment",
    "LLMOpinionFactChecker",
    "LLMOpinionGullibleSpreader",
    "LLMOpinionSkepticalEvaluator",
    "LLMOpinionUninformedBystander",
    "LLMOpportunisticTrader",
    "LLMOpportunityCostTrader",
    "LLMOutcomeLearner",
    "LLMOverconfidentTrader",
    "LLMPanicSeller",
    "LLMPassiveBystander",
    "LLMPassiveFollower",
    "LLMPassiveInvestor",
    "LLMPatternMatcher",
    "LLMPegDefender",
    "LLMPeripheryBondSeller",
    "LLMPortfolioInsurer",
    "LLMPrimeBrokerDelayedLiquidator",
    "LLMPrimeBrokerFirstMover",
    "LLMProCyclicalLender",
    "LLMProcessEvaluator",
    "LLMProgramTrader",
    "LLMRatingAgency",
    "LLMRationalArbitrageur",
    "LLMRationalCutter",
    "LLMRationalInvestor",
    "LLMRationalOptimizer",
    "LLMRationalPortfolioManager",
    "LLMRationalTrader",
    "LLMRationalUpdater",
    "LLMRecentEventOverweighter",
    "LLMRegulator",
    "LLMReputationHerder",
    "LLMRetailCoordinated",
    "LLMRetailCoordinator",
    "LLMRetailTrader",
    "LLMRiskAverseInvestor",
    "LLMRiskAverseSaver",
    "LLMRiskManager",
    "LLMRiskNeutralInvestor",
    "LLMRiskParityFund",
    "LLMSelectiveScanner",
    "LLMSelfAttributor",
    "LLMSelfFulfillingTrader",
    "LLMSentimentTrader",
    "LLMShortSeller",
    "LLMShortSellerHf",
    "LLMShortVolTrader",
    "LLMSkepticalAnalyst",
    "LLMSkepticalEvaluator",
    "LLMSkepticalValueInvestor",
    "LLMSlowAdapter",
    "LLMSocialMediaInfluencer",
    "LLMSocialProofFollower",
    "LLMSpeculativeAttacker",
    "LLMStablecoinHolder",
    "LLMStatusQuoSeller",
    "LLMStopLossTrader",
    "LLMStreakReversalTrader",
    "LLMSunkCostHolder",
    "LLMSystematicAnalyst",
    "LLMTaxAwareInvestor",
    "LLMTechnicalTrader",
    "LLMTrendChaser",
    "LLMTrendFollower",
    "LLMUninformedBystander",
    "LLMValueBuyer",
    "LLMValueContrarian",
    "LLMValueInvestor",
    "LLMValueTrader",
    "LLMVolArbitrageur",
    "LLMVolEtnManager",
    "LLMVolatilityTrader",
]
