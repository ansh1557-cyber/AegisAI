from engine.multi_timeframe import MultiTimeframeAnalyzer
from engine.bias import BiasEngine
from engine.entry import EntryEngine
from engine.risk_manager import RiskManager

# Run market analysis
analysis = MultiTimeframeAnalyzer().analyze()
from pprint import pprint

print("\n===== M15 Analysis =====")
pprint(analysis["M15"])


entry_price = analysis["M15"]["data"]["Close"].iloc[-1]

# Determine market bias
bias = BiasEngine().analyze(analysis)

# Package results for EntryEngine
results = {
    "analysis": analysis,
    "bias": bias,
}

# Generate entry signal
signal = EntryEngine().analyze(results)

# Calculate trade parameters
trade = RiskManager().calculate(
    signal=signal,
    entry_price=entry_price
)

print("\n========== AEGIS AI TRADE ==========\n")

print(f"Signal: {signal['signal']}")
print(f"Confidence: {signal['confidence']}%")

if trade:
    print(f"\nEntry: {trade['entry']}")
    print(f"Stop Loss: {trade['stop_loss']}")
    print(f"Take Profit: {trade['take_profit']}")
    print(f"Risk : Reward: {trade['risk_reward']}")
    print(f"Lot Size: {trade['lot_size']}")
    print(f"Risk Amount: ${trade['risk']}")

print("\nReasons:")

for reason in signal["reasons"]:
    print(f"✓ {reason}")