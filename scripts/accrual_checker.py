import urllib.request, json


def main():
    sum = claim_data("DAI", "0xB361a3E75Bc2Ae6c8A045b3A43E2B0c9aD890d48") + claim_data("USDC", "0x2B1a6CB0168aA540ee8D853aB1d10d7A89d6351b") + claim_data("WETH", "0xbC0F2FF495eE2eb74A145EDAA457FA4Fa310DAC5")
    print(f'total sum {sum} rooks')

def claim_data(token: str, address: str):
    with urllib.request.urlopen(f"https://indibo-lpq3.herokuapp.com/reward_of_liquidity_provider/{address}") as url:
        data = json.loads(url.read().decode())
        amount = int(data["earnings_to_date"], 16)/1e18
        print(f'StrategyRook{token} has accrued {amount} total rook')
        return amount
