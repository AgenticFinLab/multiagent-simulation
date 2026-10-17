"""Concrete archetype library: 209 reusable agent implementations.

Not part of the platform. Every module here is built on the templates in
``masim.agents`` and is scenario-agnostic, so several scenarios can reuse one
archetype:

  * ``finance/``  — investor archetypes (``Rule<Stem>`` + ``LLM<Stem>`` pairs
    sharing one kebab-case ``STRATEGY``);
  * ``market/``   — market coordinator mechanisms (``Market<Stem>``), always
    rule-executed even when the participants are LLM driven;
  * ``opinion/``  — opinion / information-spread actors;
  * ``defines/``  — the profile library: one Markdown record per archetype
    (theory, parameters, sources, I/O contract), 1:1 with the implementations,
    plus the agent icons.

Import from this package (``from agent_library import MomentumTrader``) or from
a submodule. Anything in here may be copied, replaced or ignored by a user who
prefers to write their own players; the platform does not depend on it.
"""

from agent_library.finance.active_rebalancer import RuleActiveRebalancer, LLMActiveRebalancer
from agent_library.finance.aggressive_investor import RuleAggressiveInvestor, LLMAggressiveInvestor
from agent_library.finance.algorithmic_trader import RuleAlgorithmicTrader, LLMAlgorithmicTrader
from agent_library.finance.anchor_depositor import RuleAnchorDepositor, LLMAnchorDepositor
from agent_library.finance.anchored_trader import RuleAnchoredTrader, LLMAnchoredTrader
from agent_library.finance.arbitrage_framer import RuleArbitrageFramer, LLMArbitrageFramer
from agent_library.finance.arbitrageur import RuleArbitrageur, LLMArbitrageur
from agent_library.finance.balanced_analyst import RuleBalancedAnalyst, LLMBalancedAnalyst
from agent_library.finance.bank_manager import RuleBankManager, LLMBankManager
from agent_library.finance.bayesian_updater import RuleBayesianUpdater, LLMBayesianUpdater
from agent_library.finance.belief_anchor import RuleBeliefAnchor, LLMBeliefAnchor
from agent_library.finance.block_trade_buyer import RuleBlockTradeBuyer, LLMBlockTradeBuyer
from agent_library.finance.bond_trader import RuleBondTrader, LLMBondTrader
from agent_library.finance.bottom_fisher import RuleBottomFisher, LLMBottomFisher
from agent_library.finance.break_even_trader import RuleBreakEvenTrader, LLMBreakEvenTrader
from agent_library.finance.bridge_builder import RuleBridgeBuilder, LLMBridgeBuilder
from agent_library.finance.calibrated_trader import RuleCalibratedTrader, LLMCalibratedTrader
from agent_library.finance.carry_trader import RuleCarryTrader, LLMCarryTrader
from agent_library.finance.cascade_follower import RuleCascadeFollower, LLMCascadeFollower
from agent_library.finance.category_overgeneralizer import RuleCategoryOvergeneralizer, LLMCategoryOvergeneralizer
from agent_library.finance.central_bank import RuleCentralBank, LLMCentralBank
from agent_library.finance.central_bank_defender import RuleCentralBankDefender, LLMCentralBankDefender
from agent_library.finance.commitment_escalator import RuleCommitmentEscalator, LLMCommitmentEscalator
from agent_library.finance.concentrated_fund import RuleConcentratedFund, LLMConcentratedFund
from agent_library.finance.conformist import RuleConformist, LLMConformist
from agent_library.finance.conservative_holder import RuleConservativeHolder, LLMConservativeHolder
from agent_library.finance.conservative_investor import RuleConservativeInvestor, LLMConservativeInvestor
from agent_library.finance.contagion_trader import RuleContagionTrader, LLMContagionTrader
from agent_library.finance.contrarian import RuleContrarian, LLMContrarian
from agent_library.finance.contrarian_investor import RuleContrarianInvestor, LLMContrarianInvestor
from agent_library.finance.contrarian_skeptic import RuleContrarianSkeptic, LLMContrarianSkeptic
from agent_library.finance.contrarian_statistical import RuleContrarianStatistical, LLMContrarianStatistical
from agent_library.finance.contrarian_trader import RuleContrarianTrader, LLMContrarianTrader
from agent_library.finance.convergence_arbitrageur import RuleConvergenceArbitrageur, LLMConvergenceArbitrageur
from agent_library.finance.convergence_trader import RuleConvergenceTrader, LLMConvergenceTrader
from agent_library.finance.core_bond_buyer import RuleCoreBondBuyer, LLMCoreBondBuyer
from agent_library.finance.counter_cyclical_lender import RuleCounterCyclicalLender, LLMCounterCyclicalLender
from agent_library.finance.creditor_panicker import RuleCreditorPanicker, LLMCreditorPanicker
from agent_library.finance.critical_thinker import RuleCriticalThinker, LLMCriticalThinker
from agent_library.finance.de_fi_lender import RuleDeFiLender, LLMDeFiLender
from agent_library.finance.default_follower import RuleDefaultFollower, LLMDefaultFollower
from agent_library.finance.depositor import RuleDepositor, LLMDepositor
from agent_library.finance.disposition_investor import RuleDispositionInvestor, LLMDispositionInvestor
from agent_library.finance.disposition_trader import RuleDispositionTrader, LLMDispositionTrader
from agent_library.finance.distorting_relayer import RuleDistortingRelayer, LLMDistortingRelayer
from agent_library.finance.distressed_buyer import RuleDistressedBuyer, LLMDistressedBuyer
from agent_library.finance.early_exit_trader import RuleEarlyExitTrader, LLMEarlyExitTrader
from agent_library.finance.ecb_intervenor import RuleEcbIntervenor, LLMEcbIntervenor
from agent_library.finance.endowed_holder import RuleEndowedHolder, LLMEndowedHolder
from agent_library.finance.equity_trader import RuleEquityTrader, LLMEquityTrader
from agent_library.finance.fact_checker import RuleFactChecker, LLMFactChecker
from agent_library.finance.flash_market_maker import RuleFlashMarketMaker, LLMFlashMarketMaker
from agent_library.finance.forced_seller import RuleForcedSeller, LLMForcedSeller
from agent_library.finance.frame_invariant_trader import RuleFrameInvariantTrader, LLMFrameInvariantTrader
from agent_library.finance.fundamental_analyst import RuleFundamentalAnalyst, LLMFundamentalAnalyst
from agent_library.finance.fundamental_anchor import RuleFundamentalAnchor, LLMFundamentalAnchor
from agent_library.finance.fundamental_hedger import RuleFundamentalHedger, LLMFundamentalHedger
from agent_library.finance.fundamental_investor import RuleFundamentalInvestor, LLMFundamentalInvestor
from agent_library.finance.fundamental_trader import RuleFundamentalTrader, LLMFundamentalTrader
from agent_library.finance.fundamentalist import RuleFundamentalist, LLMFundamentalist
from agent_library.finance.funding_currency_buyer import RuleFundingCurrencyBuyer, LLMFundingCurrencyBuyer
from agent_library.finance.gain_frame_follower import RuleGainFrameFollower, LLMGainFrameFollower
from agent_library.finance.greater_fool_speculator import RuleGreaterFoolSpeculator, LLMGreaterFoolSpeculator
from agent_library.finance.gullible_spreader import RuleGullibleSpreader, LLMGullibleSpreader
from agent_library.finance.hedged_carry_trader import RuleHedgedCarryTrader, LLMHedgedCarryTrader
from agent_library.finance.hedged_fund import RuleHedgedFund, LLMHedgedFund
from agent_library.finance.hft_market_maker import RuleHftMarketMaker, LLMHftMarketMaker
from agent_library.finance.high_frequency_trader import RuleHighFrequencyTrader, LLMHighFrequencyTrader
from agent_library.finance.hindsight_overconfident import RuleHindsightOverconfident, LLMHindsightOverconfident
from agent_library.finance.historical_anchor import RuleHistoricalAnchor, LLMHistoricalAnchor
from agent_library.finance.hot_hand_trader import RuleHotHandTrader, LLMHotHandTrader
from agent_library.finance.hot_money_funder import RuleHotMoneyFunder, LLMHotMoneyFunder
from agent_library.finance.house_money_trader import RuleHouseMoneyTrader, LLMHouseMoneyTrader
from agent_library.finance.ideologue import RuleIdeologue, LLMIdeologue
from agent_library.finance.imf_rescuer import RuleImfRescuer, LLMImfRescuer
from agent_library.finance.independent_assessor import RuleIndependentAssessor, LLMIndependentAssessor
from agent_library.finance.independent_thinker import RuleIndependentThinker, LLMIndependentThinker
from agent_library.finance.index_arbitrageur import RuleIndexArbitrageur, LLMIndexArbitrageur
from agent_library.finance.index_fund import RuleIndexFund, LLMIndexFund
from agent_library.finance.index_holder import RuleIndexHolder, LLMIndexHolder
from agent_library.finance.index_tracker import RuleIndexTracker, LLMIndexTracker
from agent_library.finance.inertial_holder import RuleInertialHolder, LLMInertialHolder
from agent_library.finance.information_environment import RuleInformationEnvironment, LLMInformationEnvironment
from agent_library.finance.information_trader import RuleInformationTrader, LLMInformationTrader
from agent_library.finance.insider_advantaged import RuleInsiderAdvantaged, LLMInsiderAdvantaged
from agent_library.finance.institutional_holder import RuleInstitutionalHolder, LLMInstitutionalHolder
from agent_library.finance.institutional_investor import RuleInstitutionalInvestor, LLMInstitutionalInvestor
from agent_library.finance.institutional_value import RuleInstitutionalValue, LLMInstitutionalValue
from agent_library.finance.intrinsic_value_trader import RuleIntrinsicValueTrader, LLMIntrinsicValueTrader
from agent_library.finance.ipo_flipper import RuleIpoFlipper, LLMIpoFlipper
from agent_library.finance.leverage_trader import RuleLeverageTrader, LLMLeverageTrader
from agent_library.finance.leveraged_buyer import RuleLeveragedBuyer, LLMLeveragedBuyer
from agent_library.finance.leveraged_carry_fund import RuleLeveragedCarryFund, LLMLeveragedCarryFund
from agent_library.finance.leveraged_fund import RuleLeveragedFund, LLMLeveragedFund
from agent_library.finance.leveraged_hedge_fund import RuleLeveragedHedgeFund, LLMLeveragedHedgeFund
from agent_library.finance.leveraged_investor import RuleLeveragedInvestor, LLMLeveragedInvestor
from agent_library.finance.leveraged_speculator import RuleLeveragedSpeculator, LLMLeveragedSpeculator
from agent_library.finance.liquidity_demander import RuleLiquidityDemander, LLMLiquidityDemander
from agent_library.finance.liquidity_provider import RuleLiquidityProvider, LLMLiquidityProvider
from agent_library.finance.liquidity_seeker import RuleLiquiditySeeker, LLMLiquiditySeeker
from agent_library.finance.long_horizon_investor import RuleLongHorizonInvestor, LLMLongHorizonInvestor
from agent_library.finance.long_term_investor import RuleLongTermInvestor, LLMLongTermInvestor
from agent_library.finance.long_vol_hedger import RuleLongVolHedger, LLMLongVolHedger
from agent_library.finance.loss_averse import RuleLossAverse, LLMLossAverse
from agent_library.finance.loss_averse_investor import RuleLossAverseInvestor, LLMLossAverseInvestor
from agent_library.finance.loss_frame_reactor import RuleLossFrameReactor, LLMLossFrameReactor
from agent_library.finance.macro_hedge_fund import RuleMacroHedgeFund, LLMMacroHedgeFund
from agent_library.finance.market_maker import RuleMarketMaker, LLMMarketMaker
from agent_library.finance.market_maker_gamma import RuleMarketMakerGamma, LLMMarketMakerGamma
from agent_library.finance.mbs_originator import RuleMbsOriginator, LLMMbsOriginator
from agent_library.finance.media_influenced_trader import RuleMediaInfluencedTrader, LLMMediaInfluencedTrader
from agent_library.finance.mental_accountant import RuleMentalAccountant, LLMMentalAccountant
from agent_library.finance.minsky_borrower import RuleMinskyBorrower, LLMMinskyBorrower
from agent_library.finance.momentum_buyer import RuleMomentumBuyer, LLMMomentumBuyer
from agent_library.finance.momentum_chaser import RuleMomentumChaser, LLMMomentumChaser
from agent_library.finance.momentum_follower import RuleMomentumFollower, LLMMomentumFollower
from agent_library.finance.momentum_investor import RuleMomentumInvestor, LLMMomentumInvestor
from agent_library.finance.momentum_retail import RuleMomentumRetail, LLMMomentumRetail
from agent_library.finance.momentum_speculator import RuleMomentumSpeculator, LLMMomentumSpeculator
from agent_library.finance.momentum_trader import RuleMomentumTrader, LLMMomentumTrader
from agent_library.finance.myopic_loss_averse import RuleMyopicLossAverse, LLMMyopicLossAverse
from agent_library.finance.myopic_loss_averse_investor import RuleMyopicLossAverseInvestor, LLMMyopicLossAverseInvestor
from agent_library.finance.narrative_believer import RuleNarrativeBeliever, LLMNarrativeBeliever
from agent_library.finance.new_buyer import RuleNewBuyer, LLMNewBuyer
from agent_library.finance.new_economy_evangelist import RuleNewEconomyEvangelist, LLMNewEconomyEvangelist
from agent_library.finance.noise_trader import RuleNoiseTrader, LLMNoiseTrader
from agent_library.opinion.distorting_relayer import RuleOpinionDistortingRelayer, LLMOpinionDistortingRelayer
from agent_library.finance.opinion_environment import RuleOpinionEnvironment, LLMOpinionEnvironment
from agent_library.opinion.fact_checker import RuleOpinionFactChecker, LLMOpinionFactChecker
from agent_library.opinion.gullible_spreader import RuleOpinionGullibleSpreader, LLMOpinionGullibleSpreader
from agent_library.opinion.skeptical_evaluator import RuleOpinionSkepticalEvaluator, LLMOpinionSkepticalEvaluator
from agent_library.opinion.uninformed_bystander import RuleOpinionUninformedBystander, LLMOpinionUninformedBystander
from agent_library.finance.opportunistic_trader import RuleOpportunisticTrader, LLMOpportunisticTrader
from agent_library.finance.opportunity_cost_trader import RuleOpportunityCostTrader, LLMOpportunityCostTrader
from agent_library.finance.outcome_learner import RuleOutcomeLearner, LLMOutcomeLearner
from agent_library.finance.overconfident_trader import RuleOverconfidentTrader, LLMOverconfidentTrader
from agent_library.finance.panic_seller import RulePanicSeller, LLMPanicSeller
from agent_library.finance.passive_bystander import RulePassiveBystander, LLMPassiveBystander
from agent_library.finance.passive_follower import RulePassiveFollower, LLMPassiveFollower
from agent_library.finance.passive_investor import RulePassiveInvestor, LLMPassiveInvestor
from agent_library.finance.pattern_matcher import RulePatternMatcher, LLMPatternMatcher
from agent_library.finance.peg_defender import RulePegDefender, LLMPegDefender
from agent_library.finance.periphery_bond_seller import RulePeripheryBondSeller, LLMPeripheryBondSeller
from agent_library.finance.portfolio_insurer import RulePortfolioInsurer, LLMPortfolioInsurer
from agent_library.finance.prime_broker_delayed_liquidator import RulePrimeBrokerDelayedLiquidator, LLMPrimeBrokerDelayedLiquidator
from agent_library.finance.prime_broker_first_mover import RulePrimeBrokerFirstMover, LLMPrimeBrokerFirstMover
from agent_library.finance.pro_cyclical_lender import RuleProCyclicalLender, LLMProCyclicalLender
from agent_library.finance.process_evaluator import RuleProcessEvaluator, LLMProcessEvaluator
from agent_library.finance.program_trader import RuleProgramTrader, LLMProgramTrader
from agent_library.finance.rating_agency import RuleRatingAgency, LLMRatingAgency
from agent_library.finance.rational_arbitrageur import RuleRationalArbitrageur, LLMRationalArbitrageur
from agent_library.finance.rational_cutter import RuleRationalCutter, LLMRationalCutter
from agent_library.finance.rational_investor import RuleRationalInvestor, LLMRationalInvestor
from agent_library.finance.rational_optimizer import RuleRationalOptimizer, LLMRationalOptimizer
from agent_library.finance.rational_portfolio_manager import RuleRationalPortfolioManager, LLMRationalPortfolioManager
from agent_library.finance.rational_trader import RuleRationalTrader, LLMRationalTrader
from agent_library.finance.rational_updater import RuleRationalUpdater, LLMRationalUpdater
from agent_library.finance.recent_event_overweighter import RuleRecentEventOverweighter, LLMRecentEventOverweighter
from agent_library.finance.regulator import RuleRegulator, LLMRegulator
from agent_library.finance.reputation_herder import RuleReputationHerder, LLMReputationHerder
from agent_library.finance.retail_coordinated import RuleRetailCoordinated, LLMRetailCoordinated
from agent_library.finance.retail_coordinator import RuleRetailCoordinator, LLMRetailCoordinator
from agent_library.finance.retail_trader import RuleRetailTrader, LLMRetailTrader
from agent_library.finance.risk_averse_investor import RuleRiskAverseInvestor, LLMRiskAverseInvestor
from agent_library.finance.risk_averse_saver import RuleRiskAverseSaver, LLMRiskAverseSaver
from agent_library.finance.risk_manager import RuleRiskManager, LLMRiskManager
from agent_library.finance.risk_neutral_investor import RuleRiskNeutralInvestor, LLMRiskNeutralInvestor
from agent_library.finance.risk_parity_fund import RuleRiskParityFund, LLMRiskParityFund
from agent_library.finance.selective_scanner import RuleSelectiveScanner, LLMSelectiveScanner
from agent_library.finance.self_attributor import RuleSelfAttributor, LLMSelfAttributor
from agent_library.finance.self_fulfilling_trader import RuleSelfFulfillingTrader, LLMSelfFulfillingTrader
from agent_library.finance.sentiment_trader import RuleSentimentTrader, LLMSentimentTrader
from agent_library.finance.short_seller import RuleShortSeller, LLMShortSeller
from agent_library.finance.short_seller_hf import RuleShortSellerHf, LLMShortSellerHf
from agent_library.finance.short_vol_trader import RuleShortVolTrader, LLMShortVolTrader
from agent_library.finance.skeptical_analyst import RuleSkepticalAnalyst, LLMSkepticalAnalyst
from agent_library.finance.skeptical_evaluator import RuleSkepticalEvaluator, LLMSkepticalEvaluator
from agent_library.finance.skeptical_value_investor import RuleSkepticalValueInvestor, LLMSkepticalValueInvestor
from agent_library.finance.slow_adapter import RuleSlowAdapter, LLMSlowAdapter
from agent_library.finance.social_media_influencer import RuleSocialMediaInfluencer, LLMSocialMediaInfluencer
from agent_library.finance.social_proof_follower import RuleSocialProofFollower, LLMSocialProofFollower
from agent_library.finance.speculative_attacker import RuleSpeculativeAttacker, LLMSpeculativeAttacker
from agent_library.finance.stablecoin_holder import RuleStablecoinHolder, LLMStablecoinHolder
from agent_library.finance.status_quo_seller import RuleStatusQuoSeller, LLMStatusQuoSeller
from agent_library.finance.stop_loss_trader import RuleStopLossTrader, LLMStopLossTrader
from agent_library.finance.streak_reversal_trader import RuleStreakReversalTrader, LLMStreakReversalTrader
from agent_library.finance.sunk_cost_holder import RuleSunkCostHolder, LLMSunkCostHolder
from agent_library.finance.systematic_analyst import RuleSystematicAnalyst, LLMSystematicAnalyst
from agent_library.finance.tax_aware_investor import RuleTaxAwareInvestor, LLMTaxAwareInvestor
from agent_library.finance.technical_trader import RuleTechnicalTrader, LLMTechnicalTrader
from agent_library.finance.trend_chaser import RuleTrendChaser, LLMTrendChaser
from agent_library.finance.trend_follower import RuleTrendFollower, LLMTrendFollower
from agent_library.finance.uninformed_bystander import RuleUninformedBystander, LLMUninformedBystander
from agent_library.finance.value_buyer import RuleValueBuyer, LLMValueBuyer
from agent_library.finance.value_contrarian import RuleValueContrarian, LLMValueContrarian
from agent_library.finance.value_investor import RuleValueInvestor, LLMValueInvestor
from agent_library.finance.value_trader import RuleValueTrader, LLMValueTrader
from agent_library.finance.vol_arbitrageur import RuleVolArbitrageur, LLMVolArbitrageur
from agent_library.finance.vol_etn_manager import RuleVolEtnManager, LLMVolEtnManager
from agent_library.finance.volatility_trader import RuleVolatilityTrader, LLMVolatilityTrader


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

from agent_library.market.stock_standard_price_impact import MarketStockStandardPriceImpact
from agent_library.market.opinion_echo_chamber_clustering import MarketOpinionEchoChamberClustering
from agent_library.market.information_sis_contagion import MarketInformationSisContagion
from agent_library.market.fx_currency_peg_and_attack import MarketFxCurrencyPegAndAttack
from agent_library.market.bond_yield_spread_inverse import MarketBondYieldSpreadInverse
from agent_library.market.crypto_algostable_depeg import MarketCryptoAlgostableDepeg
from agent_library.market.derivatives_vol_feedback import MarketDerivativesVolFeedback
from agent_library.market.deposit_bank_run_diamond_dybvig import MarketDepositBankRunDiamondDybvig
from agent_library.market.credit_minsky_cycle import MarketCreditMinskyCycle

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


# ---------------------------------------------------------------------------
# ``__all__`` — auto-derived from the registries above.
#
# Rationale: the hand-maintained wildcard list previously spanned 420 lines
# and duplicated every class name already present in ``REGISTRY`` /
# ``COORDINATOR_REGISTRY``. Any archetype added to the registries but not
# hand-added to ``__all__`` silently disappeared from ``from masim.agents
# import *`` callers — a real drift trap. The registries are now the
# single source of truth: ``__all__`` walks them and lifts ``.__name__``
# from every class object, so an archetype registered above is guaranteed
# to be re-exported.
# ---------------------------------------------------------------------------

_BASE_EXPORTS: list[str] = [
    "StandardMarketState",
    "CanonicalRulePlayer",
    "CanonicalLLMPlayer",
    "CanonicalRagPlayer",
    "RAG_FALLBACK_MESSAGE",
    "CanonicalMarketCoordinator",
    "REGISTRY",
    "COORDINATOR_REGISTRY",
    "get_agent",
    "get_coordinator",
]

__all__ = (
    _BASE_EXPORTS
    + [cls.__name__ for cls in COORDINATOR_REGISTRY.values()]
    + [rule_cls.__name__ for rule_cls, _ in REGISTRY.values()]
    + [llm_cls.__name__ for _, llm_cls in REGISTRY.values()]
)
